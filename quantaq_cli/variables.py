from collections import namedtuple
import operator

from loguru import logger


Flag = namedtuple("Flag", ["name", "value", "nan_columns"])

# Columns to Nan -- only for standardized schema types
_OPC_COLUMNS = [
    "opc_bin0", "opc_bin1", "opc_bin2", "opc_bin3", "opc_bin4", "opc_bin5", "opc_bin6", "opc_bin7", "opc_bin8", "opc_bin9",
    "opc_bin10", "opc_bin11", "opc_bin12", "opc_bin13", "opc_bin14", "opc_bin15", "opc_bin16", "opc_bin17", "opc_bin18",
    "opc_bin19", "opc_bin20", "opc_bin21", "opc_bin22", "opc_bin23", 
    "opc_bin1MToF", "opc_bin3MToF", "opc_bin5MToF", "opc_bin7MToF",
    "opc_sample_period", "opc_sample_flow",
    "opc_pm1", "opc_pm25", "opc_pm10",
    "opc_laser_status", "opc_temp", "opc_rh", 
]

_NEPH_COLUMNS = [
    "neph_pm1_std", "neph_pm25_std", "neph_pm10_std", 
    "neph_pm1_env", "neph_pm25_env", "neph_pm10_env",
    "neph_bin0", "neph_bin1", "neph_bin2", "neph_bin3", "neph_bin4", "neph_bin5",
]

_RHT_COLUMNS = [
    "sample_rh", "sample_temp",
]

_CO_COLUMNS = [
    "co", 
    "co_we", "co_ae", "co_diff", 
]

_NO_COLUMNS = [
    "no", 
    "no_we", "no_ae", "no_diff", 
]

_NO2_COLUMNS = [
    "no2", 
    "no2_we", "no2_ae", "no2_diff", 
]

_O3_COLUMNS = [
    "o3",
    "o3_we", "o3_ae", "ox_diff",
]

# Flag Name, Flag Bitmask Value, Columns to Nan
FLAG_DEFINITIONS = [
    # when FLAG_STARTUP is set, nan all gas columns
    Flag("FLAG_STARTUP", 1, _CO_COLUMNS + _NO_COLUMNS + _NO2_COLUMNS + _O3_COLUMNS),
    Flag("FLAG_OPC", 2, _OPC_COLUMNS),
    Flag("FLAG_NEPH", 4, _NEPH_COLUMNS),
    Flag("FLAG_RHT", 8, _RHT_COLUMNS),
    Flag("FLAG_CO", 16, _CO_COLUMNS),
    Flag("FLAG_NO", 32, _NO_COLUMNS),
    Flag("FLAG_NO2", 64, _NO2_COLUMNS),
    Flag("FLAG_O3", 128, _O3_COLUMNS),
    Flag("FLAG_CO2", 256, ["co2_raw", "co2"]),
    Flag("FLAG_SO2", 512, ["so2_we", "so2_ae", "so2_diff", "so2"]),
    Flag("FLAG_H2S", 1024, ["h2s_we", "h2s_ae", "h2s_diff", "h2s"]),
    Flag("FLAG_BAT", 2048, ["bat_voltage", "soc", "vbat"]),
    Flag("FLAG_OVERHEAT", 4096, None), # QUESTION: should this be set to _OPC_COLUMNS?
]
FLAG_VALUES = {flag.name: flag.value for flag in FLAG_DEFINITIONS}

SUPPORTED_MODELS = ("modulair", "modulair-x", "modulair-pm", "modulair-x-pm", "modulair-ufp")

# Types of flag criteria / sub-criteria
Range = namedtuple("Range", ["column", "lo", "hi"])
Gap = namedtuple(
    "Gap",
    ["gap_in_seconds", "post_gap_flag_length_seconds", "warmup_min_lipo_soc"],
    defaults=[None],  # defaults apply to the trailing fields, rightmost first
)
Single = namedtuple("Single", ["column", "op", "value"])  # op: '<', '<=', '>', '>=', '=='
Ratio = namedtuple("Ratio", ["column_numerator", "column_denominator", "op", "value"])
Multiple = namedtuple("Multiple", ["criteria", "logical_operator"])


OPS = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq,
}

DATABASE_CRITERIA = {
    "FLAG_STARTUP": [
        # Check: if device was offline for > 1 hour, flag the following 4 hours
        Gap(gap_in_seconds=60 * 60, post_gap_flag_length_seconds=4 * 60 * 60),
    ],
    "FLAG_RHT": [
        # Check 1: any one of these individually out-of-range
        Range(column="sample_rh", lo=0.0, hi=100.0),
        Range(column="sample_temp", lo=-60.0, hi=85.0),
        # Check 2: both sample_rh and sample_temp are exactly 0.0
        Multiple(
            criteria=(
                Single(column="sample_rh", op="==", value=0.0),
                Single(column="sample_temp", op="==", value=0.0),
            ),
            logical_operator="AND",
            )
    ],
    "FLAG_CO": [ 
        # Check: ae out-of-range
        Range(column="co_ae", lo=535.0, hi=800.0),
    ],
    "FLAG_NO": [
        # Check: ae out-of-range
        Range(column="no_ae", lo=640.0, hi=900.0),
    ],
    "FLAG_NO2": [
        # Check: ae out-of-range
        Range(column="no2_ae", lo=1600.0, hi=1700.0),
    ],
    "FLAG_O3": [
        # Check: ae out-of-range
        Range(column="o3_ae", lo=1600.0, hi=1700.0),
    ],
    "FLAG_OVERHEAT": [
        # Check: device is power saving or overheating
        # note: I'm not sure why the firmware includes power saving in FLAG_OVERHEAT
        Single(column="dd_operating_state", op="==", value=1), # 0 = power saving
        Single(column="dd_operating_state", op='==', value=2) # 2 = overheating
    ],
    # QUESTION: if FLAG_OPC was previously set by the firmware using other OPC criteria
    # (see the 5 QC checks below in RAWSD_CRITERIA), I'm not sure we'd want to override that here?
    # Isoprene did not re-flag FLAG_OPC and FLAG_NEPH.
    "FLAG_OPC": [
        # Check: ratio between the OPC and nephelometer is within spec
        Multiple(
            criteria=(
                Single(column="opc_bin0", op=">=", value=10.0),
                Ratio(column_numerator="neph_bin0", 
                      column_denominator="opc_bin0",
                      op=">", 
                      value=2000.0),
            ), logical_operator="AND",
            ),
    ],
     "FLAG_NEPH": [
        # Check 1: ensure that the neph isn't reading 0's when it shouldn't be
        Multiple(
            criteria=(
                Single(column="opc_bin0", op=">=", value=10.0),
                Single(column="neph_bin0", op="==", value=0.0)
            ),
            logical_operator="AND",
        ),
        # Check 2: ratio between the OPC and nephelometer is within spec
        Multiple(
            criteria=(
                Single(column="neph_bin0", op=">=", value=10.0),
                Ratio(column_numerator="neph_bin0", 
                      column_denominator="opc_bin0",
                      op=">", 
                      value=2000.0),
            ), logical_operator="AND",
        ),
    ],
}

RAWSD_CRITERIA = {
    **DATABASE_CRITERIA, # similar to database, except for FLAG_STARTUP and FLAG_OPC
    "FLAG_STARTUP": [
        Gap(gap_in_seconds=60 * 60, post_gap_flag_length_seconds=4 * 60 * 60, warmup_min_lipo_soc=0.1)
    ],
    "FLAG_OPC": [
        # Check 1: OPC is warming up or hibernating
        Single(column="dd_measurement_state", op="==", value=0), # 0 = warmup
        Single(column="dd_measurement_state", op='==', value=2), # 2 = hibernate
        # Check 2: laser status out of range
        Range(column="opc_laser_status", lo=500.0, hi=650.0),
        # Check 3: sample period of OPC excessively long
        Single(column="opc_sample_period", op=">", value=10.0),
        # Check 4: sample flow of OPC in error
        Single(column="opc_sample_flow", op="==", value=0.0),
        # Check 5: ratio between the OPC and nephelometer is within spec
        Multiple(
            criteria=(
                Single(column="neph_bin0", op=">=", value=10.0),
                Ratio(column_numerator="neph_bin0", 
                      column_denominator="opc_bin0",
                      op=">", 
                      value=2000.0),
            ), logical_operator="AND",
            ),
    ]
}

FLAG_CRITERIA = {
    "database": DATABASE_CRITERIA,
    "rawsd": RAWSD_CRITERIA
}

SUPPORTED_SOURCES = tuple(FLAG_CRITERIA.keys())

def flag_name_to_criteria(source):
    """Return the flag criteria for a given data source.

    Args:
        source (str): the data source (in SUPPORTED_SOURCES)

    Returns:
        dict: Mapping of flag name to flag criteria.

    """
    if source not in SUPPORTED_SOURCES:
        error = ValueError(f"Unsupported source: {source!r}")
        logger.error(error)
        raise error
    
    return FLAG_CRITERIA[source]
