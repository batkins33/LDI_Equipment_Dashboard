# Flag Rules (Initial 10)

Threshold defaults (configurable):
- MIN_ACTIVE_HOURS = 0.5
- VAR_WARN_HOURS = 1.0
- VAR_CRIT_HOURS = 2.0
- APPROVAL_LAG_WARN_DAYS = 2
- APPROVAL_LAG_CRIT_DAYS = 4

Flags:
1) GPS>0 & TC=0
2) TC>0 & GPS=0
3) |TC-GPS| > WARN
4) |TC-GPS| > CRIT
5) Inspection missing & GPS>MIN_ACTIVE
6) |Meter-GPS| > WARN
7) Missing equipment crosswalk mapping
8) Multi-job day without allocation model
9) Provisional != Final by > WARN
10) Approval lag > WARN/CRIT

Confidence scoring example:
Start 100, subtract for missing sources and mapping uncertainty; band into High/Med/Low.

