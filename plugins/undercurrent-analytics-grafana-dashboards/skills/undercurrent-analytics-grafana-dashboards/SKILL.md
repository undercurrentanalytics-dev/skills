---
name: undercurrent-analytics-grafana-dashboards
description: Create, edit or delete usage analytics dashboards at https://grafana.undercurrentanalytics.dev. Use when asked to build, update, or delete dashboards/panels for Grafana or Undercurrent Analytics, or query usage analytics data in SQL that is stored by Undercurrent Analytics.
---

Undercurrent Analytics is a mobile analytics service that uses Grafana for
analytics dashboards. There is an Undercurrent Analytics credentials JSON
file in the current repo, containing a Grafana Service Account
token with Admin permissions, and the username/password credentials for a
Grafana org admin, which you can use to interact with Grafana over the HTTP
API. Using the Grafana HTTP API, you can create, edit or delete usage analytics dashboards, as well as run queries against the default datasource.

## Authenticating with the Grafana HTTP API

Find the Undercurrent Analytics credentials JSON file in the repo. If you
can't find it, stop here and report that you need it in order to use the Grafana HTTP API to create or edit dashboards, or to run SQL queries against the usage analytics data. If you do find it, ensure it is ignored by version control and
not checked in.

## Finding the app's registered analytics events

Look through the source code to find the events that the app tracks. If you
can't find any, then stop and let the user know, because analytics events
need to be registered before dashboards can be created for them.

## Writing SQL queries for Undercurrent Analytics

### The analytics events table: `$__table`

During query execution, `$__table` is expanded into a view that is already
filtered to show only the relevant data, so:

- In queries, write `FROM $__table` (optionally followed by
  WHERE/GROUP BY/ORDER BY/HAVING/LIMIT/OFFSET/JOIN…ON).
- Do NOT alias it (no `$__table t`); reference its columns unqualified.

### The time filter

Include `WHERE $__timeFilter(time)` in queries when reading from `$__table`,
so you are only reading events within the selected time range.

### The table schema (`$__table` columns)

| Column                      | Type           | Non-null | Notes                                                  |
|-----------------------------|----------------|----------|---------------------------------------------------------|
| `event`                     | string         | ✅        | Event name                                             |
| `time`                      | timestamp (ms) | ✅        | Event time                                             |
| `distinct_id`               | string         |          | Identifies a unique installation of the app            |
| `properties`                | string         |          | JSON string of custom properties attached to the event |
| `app_build_number`          | string         |          | The app's build number                                 |
| `app_version_string`        | string         |          | Mixpanel `$app_version_string`                         |
| `carrier`                   | string         |          | Mixpanel `$carrier`                                    |
| `city`                      | string         |          | Mixpanel `$city`                                       |
| `device_id`                 | string         |          | Mixpanel `$device_id`                                  |
| `had_persisted_distinct_id` | bool           |          | Mixpanel `$had_persisted_distinct_id`                  |
| `lib_version`               | string         |          | Mixpanel `$lib_version`                                |
| `manufacturer`              | string         |          | Mixpanel `$manufacturer`                               |
| `model`                     | string         |          | Mixpanel `$model`                                      |
| `os`                        | string         |          | Mixpanel `$os`                                         |
| `os_version`                | string         |          | Mixpanel `$os_version`                                 |
| `radio`                     | string         |          | Mixpanel `$radio`                                      |
| `region`                    | string         |          | Mixpanel `$region`                                     |
| `screen_height`             | int64          |          | Mixpanel `$screen_height`                              |
| `screen_width`              | int64          |          | Mixpanel `$screen_width`                               |
| `user_id`                   | string         |          | Mixpanel `$user_id`                                    |
| `wifi`                      | bool           |          | Mixpanel `$wifi`                                       |
| `mp_country_code`           | string         |          | Mixpanel `mp_country_code`                              |
| `mp_lib`                    | string         |          | Mixpanel `mp_lib`                                       |
| `mp_processing_time_ms`     | int64          |          | Mixpanel `mp_processing_time_ms`                        |
| `mp_event_size`             | int64          |          | Mixpanel `$mp_event_size`                               |

(There are other columns, but they are irrelevant, so never use them.)

### SQL dialect

Uses Cloudflare R2 SQL. See:
https://developers.cloudflare.com/r2-sql/sql-reference/, but note that you
must only use the table `$__table`, and you cannot run SHOW or DESCRIBE
statements.

- SELECT statements only.
- Use WITH to join and self-reference the events table.
- Don't use WITH RECURSIVE.

### Example: An "events per hour" timeseries panel's SQL query

```sql
SELECT date_trunc('hour', time) AS hour, COUNT(*) AS event_count
FROM $__table
WHERE $__timeFilter(time)
GROUP BY date_trunc('hour', time)
ORDER BY date_trunc('hour', time)
```

## Creating Grafana dashboards via the HTTP API

### Using the HTTP API

Copy `scripts/build_dashboard.py` (bundled with this skill) into the target
repo somewhere untracked, and edit the copy to fill in the configuration and
panels for the dashboard(s) being built. Don't add the edited
`build_dashboard.py` to version control - either ignore it, or put it
somewhere that is already not tracked by version control (such as a scratch space or tmp directory). The same goes for
any other Python-related files that may become present in the repo after running it, such as `__pycache__/`.

Smoke test the dashboards and panels against the live data source after
they've been created to ensure that they really work. This is important.

The bundled script supports two commands:

```
python3 build_dashboard.py smoke    # validate each panel query against the datasource
python3 build_dashboard.py deploy   # smoke-test, then create/update the dashboard
```

Edit the `PANELS` list (and the configuration constants at the top of the
file) to match the dashboard(s) needed for the app being worked on - the two
panels included in the template are only examples and should be replaced.

## Reporting back

Once finished, report the links to any dashboards created or edited.
