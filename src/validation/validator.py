"""
Data ingestion and validation utilities.
"""

from typing import Tuple, List
import pandas as pd
from pydantic import ValidationError

from ..data_generator.models import CellularMeasurement


def validate_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], float]:
    """
    Validate a DataFrame of measurements.
    Returns: (validated_df, warnings, quality_score)
    quality_score in [0, 1]
    """
    warnings: List[str] = []
    valid_rows = []
    invalid_count = 0

    required_cols = {"timestamp", "test_id", "device_id", "technology", "rsrp_dbm", "sinr_db"}
    missing = required_cols - set(df.columns)
    if missing:
        warnings.append(f"Missing required columns: {missing}")

    for idx, row in df.iterrows():
        try:
            # Convert timestamp if needed
            data = row.to_dict()
            if isinstance(data.get("timestamp"), str):
                data["timestamp"] = pd.to_datetime(data["timestamp"])
            CellularMeasurement(**data)
            valid_rows.append(row)
        except ValidationError as e:
            invalid_count += 1
            if invalid_count <= 5:  # limit warning spam
                warnings.append(f"Row {idx} validation error: {e.error_count()} issues")

    validated = pd.DataFrame(valid_rows) if valid_rows else df.iloc[0:0]

    # Simple quality score
    completeness = 1 - (df.isna().mean().mean())
    validity = 1 - (invalid_count / max(1, len(df)))
    quality = float((completeness * 0.6 + validity * 0.4))

    if invalid_count > 0:
        warnings.append(f"{invalid_count} rows failed schema validation")

    return validated, warnings, round(quality, 3)
