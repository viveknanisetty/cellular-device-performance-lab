# Phase 1 Teaching Notes — Foundation: Synthetic Data Generation & Validation

## Engineering Concept
When a Cellular Performance Engineer at Apple (or any device OEM) receives a field complaint or a lab failure ("poor throughput in good coverage"), the first step is not to open a modem log. It is to **reproduce the condition under controlled, repeatable circumstances**.

On the network side you are used to looking at eNodeB/gNodeB counters (PRB utilization, RLF rate, handover success). On the device side you must generate or capture a time-aligned trace that contains:
- RF measurements the UE itself reports (RSRP, RSRQ, SINR, CQI)
- PHY/MAC outcomes (MCS, BLER, HARQ)
- Higher-layer results (PDCP throughput, TCP RTT, application goodput)
- Context (mobility, temperature, power)

Because we do not have a call box or channel emulator connected, we build a **synthetic generator** that produces statistically plausible traces with known ground-truth scenarios. This lets us later build and validate KPI engines and diagnostic rules against known failure modes.

## Why Apple Cares
Apple Cellular Performance Engineers must:
- Characterize new modem firmware or antenna designs before mass production.
- Isolate whether a throughput problem is RF (antenna, PA, interference), modem (link adaptation, HARQ), or higher-layer (TCP, app, thermal).
- Create repeatable benchmarks that survive across software builds.
- Explain results to hardware, modem, and software teams with evidence, not anecdotes.

A well-structured synthetic lab demonstrates you understand the measurement chain and the need for controlled conditions.

## What We Built
- Configurable scenarios in YAML (baseline, degraded SINR, high mobility, UL degradation).
- Vectorized generator that creates consistent relationships:
  - SINR → CQI/MCS (simple linear map)
  - SINR → BLER (logistic)
  - Spectral efficiency → theoretical throughput → realized throughput after BLER
  - Radio throughput → application throughput (overhead factor)
  - Poor RF → higher RTT and power
- Pydantic schema so invalid data is rejected with clear errors.
- Data-quality score and warning list.
- Fixed seed + fixed start timestamp for perfect reproducibility.

## Key Assumptions (Always State These)
1. The SINR-to-BLER curve is a simple logistic, not a real turbo/LDPC code performance curve.
2. Spectral efficiency is a Shannon-like approximation, not actual MCS table lookup.
3. No scheduling, no grant limitation, no power headroom modeling yet.
4. Handover is a simple periodic SINR dip, not a full RRC procedure.
5. All numbers are synthetic.

## How to Validate
- Same seed + same scenario → identical DataFrame (unit test).
- Degraded SINR scenario must show clearly worse BLER, throughput, and RTT than baseline.
- Quality score > 0.9 on clean generated data.
- Visual inspection of time series: RSRP relatively stable, SINR more variable, throughput tracks SINR.

## Practical Exercise for You
1. Generate both `baseline_lte` and `degraded_sinr`.
2. Compute mean(SINR), mean(BLER), mean(DL throughput) for each.
3. Explain in one paragraph why the degraded case has high RSRP but low throughput.
4. Change the logistic BLER parameters and observe the effect. Document the assumption you just modified.

## Interview Talking Points
"When I needed to prepare for device-side performance work, I built a synthetic lab that generates time-aligned RF, PHY, and TCP traces under known conditions. This let me practice the exact isolation techniques used in call-box testing: I can force a high-RSRP / low-SINR case and show that the diagnostic engine correctly points at interference or link adaptation rather than coverage. All assumptions are documented so I never over-claim the fidelity of the model."

## Next Phase Preview
Phase 2 will turn these traces into a proper KPI engine with documented formulas for every metric (average RSRP, 5th/95th percentile throughput, HARQ retransmission rate, energy per GB, etc.) and unit tests that verify the math.
