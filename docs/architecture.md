# Architecture — Cellular Device Performance Lab

## Design Principles
- **Modular**: Each engineering concern (RF generation, KPI calculation, protocol analysis, diagnostics, visualization) lives in its own package.
- **Explainable**: Every KPI has documented formula, units, assumptions, and limitations.
- **Synthetic but Plausible**: Relationships between RSRP, SINR, BLER, MCS, throughput, and RTT are modeled with simplified but physically motivated equations. Not a modem emulator.
- **Device-side focus**: Emphasizes UE/modem behavior, RF front-end effects, L1/L2/L3 protocol stack, TCP/IP interaction, and power/thermal — the gaps when coming from RAN engineering.
- **Interview-aligned**: Every major capability maps to questions Apple Cellular Performance Engineers are expected to answer.

## Logical Modules

| Module | Responsibility | Key Outputs |
|--------|----------------|-------------|
| A. Test Data Generator | Configurable synthetic LTE/NR SA/NSA datasets with plausible cross-layer relationships | CSV/JSON traces |
| B. Ingestion & Validation | Schema validation, missing-value handling, data-quality scoring | Validated DataFrames + quality reports |
| C. KPI Calculation Engine | RF, PHY, MAC, RLC/PDCP, TCP, Application, Power KPIs with documented formulas | KPI tables |
| D. Protocol Stack Analysis | L1/L2/L3 event interpretation and correlation (not full protocol decoding) | Layer-specific insights |
| E. TCP/IP & Application | End-to-end performance diagnostics, goodput vs radio throughput | Transport root-cause hypotheses |
| F. Channel & Mobility Simulation | AWGN, Rayleigh, Rician, Doppler, multipath parameterizable models | Channel condition traces |
| G. Automated Test Framework | Scenario execution, configurable thresholds, verdicts, regression | Test reports + verdicts |
| H. Root-Cause Engine | Rule-based, evidence-graded diagnostics | Investigation recommendations |
| I. Dashboard | Streamlit engineering workstation UI | Interactive exploration |
| J. Reporting | CSV/HTML/PDF engineering reports | Review-ready documents |

## Data Flow
```
Scenario Config → Data Generator → Synthetic Trace
                      ↓
                 Ingestion + Validation
                      ↓
              KPI Engine + Protocol Analysis + TCP Analysis
                      ↓
                 Diagnostic Engine
                      ↓
           Dashboard / Reporting / Test Verdict
```

## Highest-Risk Technical Assumptions
1. Simplified link-budget and SINR-to-BLER mapping will not match real modem link adaptation.
2. No actual L1/L2 protocol messages — only aggregate counters and derived indicators.
3. Power and thermal models are high-level correlations, not silicon-level.
4. TCP modeling is statistical, not full congestion-control simulation.
5. Handover and mobility effects are event-based interruptions, not full RRC procedure simulation.

These limitations will be explicitly documented in every report and dashboard.

## Phase 1 Acceptance Criteria
- Project structure matches specification.
- Configurable synthetic generator produces LTE baseline, degraded SINR, high mobility, and UL degradation scenarios.
- Generated datasets contain the required columns (or explicit NaN with reason).
- Schema validation rejects invalid values and scores data quality.
- Seeded random generation is reproducible.
- Basic CLI or script can generate and save a dataset.
- Unit tests cover generator reproducibility and schema validation.
- Progress document updated.

## Technology Choices
- **Pydantic v2**: Schema definition and validation.
- **Pandas + NumPy**: Time-series handling and vectorized calculations.
- **SciPy**: Statistical distributions and simple channel models.
- **Streamlit + Plotly**: Professional engineering dashboard.
- **Pytest**: Unit and integration tests.
- **YAML**: Human-editable configuration and thresholds.
