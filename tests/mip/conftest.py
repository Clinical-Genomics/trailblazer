"""MIP specific fixtures"""
import pytest

from trailblazer.mip import sacct
from trailblazer.mip import start


@pytest.fixture(scope="session")
def failed_sacct_jobs():
    """Get failed jobs ids"""
    with open("tests/fixtures/sacct/failed.log.status") as stream:
        sacct_jobs = sacct.parse_sacct(stream)
    return sacct_jobs


@pytest.fixture(scope="session")
def mip_cli():
    """Generate a mip CLI object"""
    _mip_cli = start.MipCli(
        script="test/fake_mip.pl", pipeline="rd_dna", conda_env="dummy_env"
    )
    return _mip_cli


@pytest.fixture(scope="session")
def mip_meta_data() -> dict:
    """Define MIP meta data metrics"""
    return {
        "FATHER_AT_DROPOUT": 2.673848,
        "FATHER_FRACTION_DUPLICATES": 0.0400685961424888,
        "FATHER_GC_DROPOUT": 0.198037,
        "FATHER_MEDIAN_INSERT_SIZE": 393,
        "FATHER_PCT_TARGET_BASES_10X": 0.987132,
        "FATHER_PCT_TARGET_BASES_20X": 0.916531,
        "FATHER_PCT_TARGET_BASES_50X": 0.004152,
        "FATHER_PCT_TARGET_BASES_100X": 0.000118,
        "FATHER_MEAN_TARGET_COVERAGE": 29.027266,
        "FATHER_STANDARD_DEVIATION": 88.653614,
        "FATHER_STRAND_BALANCE": 0.501377,
        "GENOME_BUILD_SOURCE": "grch",
        "GENOME_BUILD_VERSION": 37,
        "MOTHER_AT_DROPOUT": 1.716704,
        "MOTHER_FRACTION_DUPLICATES": 0.0379523291229131,
        "MOTHER_GC_DROPOUT": 0.214813,
        "MOTHER_MEDIAN_INSERT_SIZE": 409,
        "MOTHER_PCT_TARGET_BASES_10X": 0.98974,
        "MOTHER_PCT_TARGET_BASES_20X": 0.935455,
        "MOTHER_PCT_TARGET_BASES_50X": 0.002685,
        "MOTHER_PCT_TARGET_BASES_100X": 0.000101,
        "MOTHER_MEAN_TARGET_COVERAGE": 28.643247,
        "MOTHER_RAW_TOTAL_SEQUENCES": 600006004,
        "MOTHER_READS_MAPPED": 598456583,
        "MOTHER_STANDARD_DEVIATION": 94.353778,
        "MOTHER_STRAND_BALANCE": 0.50162,
        "MOTHER_MAPPED": 598456583 / 600006004,
        "RANK_MODEL_VERSION": "1.25",
    }
