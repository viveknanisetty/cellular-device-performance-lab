"""Unit tests for data generator and validation."""

import pytest
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_generator.generator import SyntheticDataGenerator
from src.validation.validator import validate_dataframe


def test_generator_reproducible():
    gen1 = SyntheticDataGenerator(seed=42)
    gen2 = SyntheticDataGenerator(seed=42)
    df1 = gen1.generate("baseline_lte")
    df2 = gen2.generate("baseline_lte")
    pd.testing.assert_frame_equal(df1, df2)


def test_generator_produces_expected_columns():
    gen = SyntheticDataGenerator(seed=1)
    df = gen.generate("baseline_lte")
    expected = ["timestamp", "rsrp_dbm", "sinr_db", "dl_throughput_mbps", "bler", "rtt_ms"]
    for col in expected:
        assert col in df.columns
    assert len(df) > 100


def test_validation_passes_good_data():
    gen = SyntheticDataGenerator(seed=7)
    df = gen.generate("baseline_lte")
    validated, warnings, score = validate_dataframe(df)
    assert score > 0.9
    assert len(validated) == len(df)
    assert len(warnings) == 0 or "Missing" not in str(warnings)
