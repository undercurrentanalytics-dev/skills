#!/usr/bin/env python3
"""Deploy a Grafana dashboard via the HTTP API.

Usage:
  python3 build_dashboard.py smoke    # validate each panel query against the datasource
  python3 build_dashboard.py deploy   # smoke-test, then create/update the dashboard
"""
import json, sys, time, urllib.request, urllib.error

# ── Configuration ──────────────────────────────────────────────────────────────
GRAFANA_URL     = "https://grafana.undercurrentanalytics.dev"
API_KEY         = "<your Grafana API key here>"
DATASOURCE      = {"type": "agentified-r2sql-datasource", "uid": "<datasource UID here>"}
DASHBOARD_UID   = "<dashboard UID if exists>"  # existing dashboard; update in place
DASHBOARD_TITLE = "<dashboard title>"
DASHBOARD_TAGS  = [] # List of string tags

# Appended to every $__timeFilter(time) clause.  Set to `None` to disable.
EXTRA_FILTER = None

# ── App-specific SQL fragments ─────────────────────────────────────────────────
# ...

# ── Panels ─────────────────────────────────────────────────────────────────────
# Each entry: (title, viz_type, rawSql, fieldConfig_overrides, options, w, h)
#   viz_type         – Grafana panel type id, e.g. "timeseries", "stat", "barchart", "piechart", "table"
#   fieldConfig_overrides – merged into defaults; use None for no overrides
#   options          – panel options dict; use None for defaults
#   w, h             – grid units (grid is 24 wide)
# Two examples included below. Replace them with the dashboards for this app.
PANELS = [
    ("Daily active users", "timeseries",
     "SELECT date_trunc('day', time) AS day, COUNT(DISTINCT distinct_id) AS dau "
     "FROM $__table WHERE event='app_launch' AND $__timeFilter(time) "
     "GROUP BY date_trunc('day', time) ORDER BY day",
     {"custom": {"drawStyle": "line", "lineWidth": 2, "fillOpacity": 10,
                 "pointSize": 6, "showPoints": "always"}, "unit": "short"}, None, 16, 8),

    ("Event volume per day", "timeseries",
     "SELECT date_trunc('day', time) AS day, COUNT(*) AS events FROM $__table "
     "WHERE $__timeFilter(time) GROUP BY date_trunc('day', time) ORDER BY day",
     {"custom": {"drawStyle": "bars", "fillOpacity": 70, "lineWidth": 1},
      "unit": "short"}, None, 12, 8),
]

# ── Infrastructure ─────────────────────────────────────────────────────────────

def _inject_filter(sql):
    if EXTRA_FILTER:
        return sql.replace("$__timeFilter(time)", f"$__timeFilter(time) AND {EXTRA_FILTER}")
    return sql


def http(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        GRAFANA_URL + path, data=data, method=method,
        headers={"Authorization": f"Bearer {API_KEY}",
                 "Content-Type": "application/json",
                 "User-Agent": "curl/8.4.0"})
    def parse(raw):
        try:
            return json.loads(raw or "{}")
        except json.JSONDecodeError:
            return {"_raw": raw}
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, parse(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, parse(e.read().decode())


def smoke():
    now = int(time.time() * 1000)
    frm = now - 400 * 86400 * 1000
    ok = True
    for title, _vt, sql, *_ in PANELS:
        body = {"from": str(frm), "to": str(now), "queries": [
            {"refId": "A", "datasource": DATASOURCE,
             "rawSql": _inject_filter(sql), "format": "table"}]}
        status, resp = http("POST", "/api/ds/query", body)
        r = resp.get("results", {}).get("A", {})
        st = r.get("status", status)
        if st == 200:
            frames = r.get("frames", [])
            vals = frames[0]["data"]["values"] if frames and frames[0].get("data") else []
            print(f"  OK   [{len(vals)}c x {len(vals[0]) if vals else 0}r]  {title}")
        else:
            ok = False
            print(f"  FAIL [{st}]  {title}\n        {str(r.get('error') or resp)[:200]}")
    return ok


def build_model():
    panels = []
    x = y = row_h = 0
    for i, (title, vt, sql, fc, opts, w, h) in enumerate(PANELS, start=1):
        if x + w > 24:
            x = 0
            y += row_h
            row_h = 0
        defaults = {"color": {"mode": "palette-classic"}, "custom": {}, "unit": "short"}
        for k, v in (fc or {}).items():
            if isinstance(v, dict) and isinstance(defaults.get(k), dict):
                defaults[k] = {**defaults[k], **v}
            else:
                defaults[k] = v
        panel = {
            "datasource": DATASOURCE,
            "fieldConfig": {"defaults": defaults, "overrides": []},
            "gridPos": {"h": h, "w": w, "x": x, "y": y},
            "id": i,
            "title": title,
            "type": vt,
            "targets": [{"datasource": DATASOURCE, "rawSql": _inject_filter(sql),
                         "refId": "A", "format": "table"}],
        }
        if opts:
            panel["options"] = opts
        panels.append(panel)
        x += w
        row_h = max(row_h, h)

    return {
        "annotations": {"list": []},
        "editable": True,
        "fiscalYearStartMonth": 0,
        "graphTooltip": 0,
        "links": [],
        "panels": panels,
        "refresh": "",
        "schemaVersion": 39,
        "tags": DASHBOARD_TAGS,
        "templating": {"list": []},
        "time": {"from": "now-30d", "to": "now"},
        "timepicker": {},
        "timezone": "",
        "title": DASHBOARD_TITLE,
        "uid": DASHBOARD_UID,
        "weekStart": "",
    }


def deploy():
    print("Smoke-testing panel queries...")
    if not smoke():
        print("\nAborting deploy: one or more panel queries failed.")
        sys.exit(1)
    print("\nAll queries OK. Creating dashboard...")
    status, resp = http("POST", "/api/dashboards/db",
                        {"dashboard": build_model(), "overwrite": True})
    print(status, json.dumps(resp, indent=2))
    if resp.get("url"):
        print(f"\nOpen: {GRAFANA_URL}{resp['url']}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    if cmd == "smoke":
        smoke()
    elif cmd == "deploy":
        deploy()
    else:
        print(__doc__)
