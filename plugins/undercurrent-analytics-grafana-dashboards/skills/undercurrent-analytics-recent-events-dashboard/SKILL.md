---
name: undercurrent-analytics-recent-events-dashboard
description: Work on the 'Recent Events' usage analytics Grafana dashboards at https://grafana.undercurrentanalytics.dev. Use when asked to do create or edit a live events/live usage/recent events/recent usage table or dashboard based on usage analytics or events for Undercurrent Analytics.
---

Undercurrent Analytics is a mobile analytics service that uses Grafana for
analytics dashboards. There is an Undercurrent Analytics credentials JSON
file in the current repo, containing a Grafana Service Account
token with Admin permissions, and the username/password credentials for a
Grafana org admin, which you can use to interact with Grafana over the HTTP
API. Using the Grafana HTTP API, you can create, edit or delete usage analytics dashboards, as well as run queries against the default datasource.

## Common requests

To exclude certain events, for example those that come from the developer's own usage, determine how best to do that from the app's source code by looking at the events it sends. You may also need to add some metadata to a sent event (for example the app_launch event) which indicates that the app user is a developer (for example, an app may have a 'developer mode').

Other usage may also be worth excluding, such as that done by external testers from the App Store/Play Store. Identify hasty, shallow app usage from distinct users who never return, by querying the usage analytics data using SQL and propose identifying characteristics for events to exclude. For example, such users may use 1-letter text entries in onboarding, or speed through onboarding screens too fast to have possibly understood them.

### If the user wants to reset their 'Recent events' dashboard

The JSON file `scripts/default-events-dashboard.json` contains the default 'Recent events' Grafana dashboard definition. You can use an altered version of it as the initial version of the Grafana dashboard to show live events. In it, you need to replace the variable `${DS_UID}` with the actual Datasource ID, which you can get from the Grafana HTTP API at https://grafana.undercurrentanalytics.dev.
