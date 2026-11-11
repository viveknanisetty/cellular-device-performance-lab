"""
Synthetic cellular test data generator.

Produces plausible time-series traces for LTE and 5G NR scenarios.
Relationships are simplified engineering models, not modem-accurate.
All outputs are synthetic.
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pandas as pd
import yaml

from .models import CellularMeasurement


class SyntheticDataGenerator:
    """Configurable generator for synthetic device performance traces."""

    def __init__(self, config_path: str = None, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)

        if config_path is None:
            # Try multiple possible locations so it works locally and on Streamlit Cloud
            # (Streamlit Cloud often has a nested folder structure)
            possible_paths = [
                Path(__file__).resolve().parent.parent.parent / "config" / "settings.yaml",
                Path(__file__).resolve().parent.parent / "config" / "settings.yaml",
                Path.cwd() / "config" / "settings.yaml",
                Path.cwd().parent / "config" / "settings.yaml",
            ]
            config_path = None
            for p in possible_paths:
                if p.exists():
                    config_path = p
                    break
            if config_path is None:
                raise FileNotFoundError(
                    "Could not find config/settings.yaml. Tried:\n" +
                    "\n".join(str(p) for p in possible_paths)
                )

        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def generate(self, scenario_name: str) -> pd.DataFrame:
        """Generate a full trace for a named scenario."""
        # Re-seed at the start of each generation for true reproducibility
        np.random.seed(self.seed)
        if scenario_name not in self.config["scenarios"]:
            raise ValueError(f"Unknown scenario: {scenario_name}")

        sc = self.config["scenarios"][scenario_name]
        n_samples = int(sc["duration_seconds"] * 1000 / sc["sampling_interval_ms"])
        # Fixed start time for reproducibility (or use a configurable epoch)
        start_time = datetime(2026, 1, 1, 12, 0, 0)

        records = []
        for i in range(n_samples):
            ts = start_time + timedelta(milliseconds=i * sc["sampling_interval_ms"])
            rec = self._generate_sample(sc, i, ts, scenario_name)
            records.append(rec)

        df = pd.DataFrame(records)
        return df

    def _generate_sample(self, sc: Dict[str, Any], idx: int, ts: datetime, scenario: str) -> Dict[str, Any]:
        """Generate one measurement sample with plausible relationships."""
        # Base RF
        rsrp = sc["rsrp_mean_dbm"] + np.random.normal(0, 2.5)
        sinr = sc["sinr_mean_db"] + np.random.normal(0, 1.5)

        # Mobility / interference effects
        if sc.get("mobility_speed_kmh", 0) > 50:
            sinr -= np.random.uniform(0, 4)
            if idx % 300 == 0:  # occasional handover
                sinr -= 8
                handover = True
            else:
                handover = False
        else:
            handover = False

        if sc.get("interference_level") == "high":
            sinr -= np.random.uniform(3, 7)

        # Simple SINR → CQI / MCS / BLER mapping (illustrative)
        cqi = max(1, min(15, int(sinr * 0.6 + 5)))
        mcs = max(0, min(28, int(sinr * 1.2 + 8)))
        bler = 1 / (1 + np.exp((sinr - 2) * 0.8))  # logistic
        bler = float(np.clip(bler + np.random.normal(0, 0.02), 0, 1))

        # Throughput estimation (very simplified)
        # Spectral efficiency rough approximation from SINR
        se = max(0.1, min(6.0, 0.5 * np.log2(1 + 10 ** (sinr / 10))))
        bw = sc.get("bandwidth_mhz", 20)
        layers = 2 if sc["technology"] != "lte" else 2
        theoretical_dl = se * bw * layers * 0.75  # efficiency factor
        dl_tput = theoretical_dl * (1 - bler) * np.random.uniform(0.85, 1.0)
        ul_tput = dl_tput * np.random.uniform(0.15, 0.35)

        if scenario == "ul_degradation":
            ul_tput *= 0.3

        # TCP / application layer (slightly lower than radio)
        app_dl = dl_tput * np.random.uniform(0.75, 0.92)
        rtt = 25 + max(0, 40 - sinr) * 1.5 + np.random.normal(0, 5)

        # Power (rough correlation with activity and poor RF)
        base_power = 800
        power = base_power + dl_tput * 8 + max(0, -sinr) * 30 + np.random.normal(0, 50)

        return {
            "timestamp": ts.isoformat(),
            "test_id": f"TEST-{scenario.upper()}-{self.seed}",
            "device_id": self.config["default_device"]["device_id"],
            "technology": sc["technology"],
            "rat": sc["rat"],
            "band": "B7" if sc["technology"] == "lte" else "n78",
            "bandwidth_mhz": bw,
            "carrier_aggregation": "1CC" if "baseline" in scenario else "2CC",
            "mimo_layers": layers,
            "rsrp_dbm": round(rsrp, 1),
            "rsrq_db": round(-8 + np.random.normal(0, 1), 1),
            "rssi_dbm": round(rsrp + 10 + np.random.normal(0, 2), 1),
            "sinr_db": round(sinr, 1),
            "cqi": cqi,
            "mcs": mcs,
            "bler": round(bler, 4),
            "harq_retransmissions": int(bler * 20 + np.random.poisson(0.5)),
            "rlc_retransmissions": int(bler * 5),
            "pdcp_throughput_mbps": round(dl_tput * 0.98, 2),
            "dl_throughput_mbps": round(dl_tput, 2),
            "ul_throughput_mbps": round(ul_tput, 2),
            "rtt_ms": round(max(5, rtt), 1),
            "latency_ms": round(max(5, rtt * 0.6), 1),
            "jitter_ms": round(abs(np.random.normal(2, 1.5)), 1),
            "packet_loss": round(max(0, bler * 0.05 + np.random.uniform(0, 0.002)), 4),
            "tcp_retransmissions": int(np.random.poisson(bler * 10)),
            "tcp_cwnd_bytes": int(50000 + dl_tput * 2000),
            "cpu_utilization_pct": round(15 + dl_tput * 0.3 + np.random.uniform(0, 5), 1),
            "device_temperature_c": round(38 + dl_tput * 0.15 + np.random.normal(0, 1), 1),
            "power_consumption_mw": round(max(200, power), 0),
            "mobility_speed_kmh": sc.get("mobility_speed_kmh", 0),
            "handover_event": handover,
            "connection_state": "CONNECTED",
        }


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic cellular performance traces")
    parser.add_argument("--scenario", default="baseline_lte", help="Scenario name from config")
    parser.add_argument("--output", default="data/synthetic/output.csv", help="Output CSV path")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    gen = SyntheticDataGenerator(seed=args.seed)
    df = gen.generate(args.scenario)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Generated {len(df)} samples for scenario '{args.scenario}'")
    print(f"Saved to {args.output}")
    print("\nSample statistics:")
    print(df[["rsrp_dbm", "sinr_db", "bler", "dl_throughput_mbps", "ul_throughput_mbps", "rtt_ms"]].describe().round(2))


if __name__ == "__main__":
    main()
