"""
Pydantic models for cellular measurement schema.
Used for validation and documentation of expected fields.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class CellularMeasurement(BaseModel):
    """Single time-series sample of device cellular performance."""

    timestamp: datetime
    test_id: str
    device_id: str
    technology: Literal["lte", "nr_sa", "nr_nsa"]
    rat: str
    band: str
    bandwidth_mhz: float
    carrier_aggregation: Optional[str] = None
    mimo_layers: int
    rsrp_dbm: Optional[float] = None
    rsrq_db: Optional[float] = None
    rssi_dbm: Optional[float] = None
    sinr_db: Optional[float] = None
    cqi: Optional[int] = Field(None, ge=0, le=15)
    mcs: Optional[int] = Field(None, ge=0, le=31)
    bler: Optional[float] = Field(None, ge=0.0, le=1.0)
    harq_retransmissions: Optional[int] = Field(None, ge=0)
    rlc_retransmissions: Optional[int] = Field(None, ge=0)
    pdcp_throughput_mbps: Optional[float] = None
    dl_throughput_mbps: Optional[float] = None
    ul_throughput_mbps: Optional[float] = None
    rtt_ms: Optional[float] = None
    latency_ms: Optional[float] = None
    jitter_ms: Optional[float] = None
    packet_loss: Optional[float] = Field(None, ge=0.0, le=1.0)
    tcp_retransmissions: Optional[int] = Field(None, ge=0)
    tcp_cwnd_bytes: Optional[int] = None
    cpu_utilization_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    device_temperature_c: Optional[float] = None
    power_consumption_mw: Optional[float] = None
    mobility_speed_kmh: Optional[float] = Field(None, ge=0.0)
    handover_event: Optional[bool] = False
    connection_state: Optional[str] = "CONNECTED"

    @field_validator("rsrp_dbm")
    @classmethod
    def rsrp_reasonable(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v > -40 or v < -140):
            raise ValueError("RSRP outside plausible range [-140, -40] dBm")
        return v

    @field_validator("sinr_db")
    @classmethod
    def sinr_reasonable(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v > 40 or v < -15):
            raise ValueError("SINR outside plausible range [-15, 40] dB")
        return v
