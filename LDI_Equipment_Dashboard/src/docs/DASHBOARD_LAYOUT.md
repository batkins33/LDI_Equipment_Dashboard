# Dashboard Layout Spec

## Page 1 — Executive Overview
KPIs:
- Validated Equipment-Days % (7d/30d)
- High-variance Equipment-Days (yesterday)
- Telematics coverage % (yesterday)
- Inspection compliance % (yesterday)
- Approval lag (median, 14d)
- Top jobs by unvalidated hours (7d)

## Page 2 — Yesterday Provisional (by 6am)
Main table (Equipment × Day):
- GPS engine hours
- Timecard equipment hours (provisional)
- Inspection meter delta
- E360 meter delta (optional)
- Variances
- Confidence score
- Flags + open exceptions

## Page 3 — Exceptions Queue
Views:
- Unassigned / Assigned / By job / By foreman / By equipment manager
Fields:
- Equipment + date + job
- Flag types + severity
- Evidence links (raw payloads, inspection photos, GPS summary)
- Recommended action + owner + status

## Page 4 — Approval Flow Health
- Lag distribution
- Lag by foreman/job
- Timecards older than X days unapproved
- Provisional vs final deltas

## Page 5 — Inspections Compliance
- Missing meter readings list for active equipment-days
- Compliance trend by job/foreman

## Page 6 — Telematics Health
- Devices offline
- GPS=0 but TC>0
- TC=0 but GPS>0
- Missing mappings list

## Page 7 — Equipment Drilldown
- 30-day timeline: GPS vs TC vs meter deltas
- Multi-job allocations
- Inspection evidence
- Maintenance context (work orders/meter history)
- Exception history

