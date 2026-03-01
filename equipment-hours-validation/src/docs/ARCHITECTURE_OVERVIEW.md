# Architecture Overview

## Inputs
- HeavyJob (timecards + equipment hours)
- Safety Inspections (meter readings + evidence)
- Equipment360 (meter readings + maintenance context)
- Telematics/GPS (engine runtime)

## Data layers (medallion)
- **Bronze:** raw JSON snapshots + request metadata
- **Silver:** normalized source facts
- **Gold:** reconciled Equipment-Day facts + flags + exceptions queue

```mermaid
flowchart LR
  HJ[HeavyJob] --> BRZ[Bronze]
  SAF[Safety] --> BRZ
  E360[Equipment360] --> BRZ
  GPS[Telematics] --> BRZ
  BRZ --> SLV[Silver]
  SLV --> GLD[Gold: Recon + Flags]
  GLD --> DASH[Dashboard + Exceptions]
```

## Design principle
Do not block on approvals: compute provisional daily; overlay final continuously.

