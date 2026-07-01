# Undercurrent Analytics Skills

A Claude Code plugin marketplace with skills for working on Undercurrent
Analytics projects.

## Adding this marketplace

In Claude Code:
```
/plugin marketplace add undercurrentanalytics-dev/skills
/plugin install undercurrent-analytics-grafana-dashboards@undercurrent-analytics-skills
/reload-plugins
```

## Available skills

Installing the `undercurrent-analytics-grafana-dashboards` plugin gives you both of these skills:

- **undercurrent-analytics-grafana-dashboards** - Create and edit Grafana
  dashboards to surface insights based on the analytics events included in your app.
  Covers how to write SQL in the correct dialect (Cloudflare R2 SQL) and how to interact
  with the Grafana HTTP API at https://grafana.undercurrentanalytics.dev.
- **undercurrent-analytics-recent-events-dashboard** - For working on the 'Recent events'
  Grafana dashboard specifically. Contains the base dashboard definition, and some common
  and useful patterns for improving this dashboard for your own usage.
