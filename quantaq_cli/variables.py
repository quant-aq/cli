from collections import namedtuple
import operator

from loguru import logger

Flag = namedtuple("Flag", ["name", "value", "nan_columns"])

# Columns to Nan across all schema types (db, rawsd, cloudapi)
_OPC_COLUMNS = [
    "bin0", "bin1", "bin2", "bin3", "bin4", "bin5", "bin6", "bin7", "bin8", "bin9",
    "bin10", "bin11", "bin12", "bin13", "bin14", "bin15", "bin16", "bin17", "bin18",
    "bin19", "bin20", "bin21", "bin22", "bin23", 
    "opc.bin0", "opc.bin1", "opc.bin2", "opc.bin3", "opc.bin4", "opc.bin5",
    "opc.bin6", "opc.bin7", "opc.bin8", "opc.bin9", "opc.bin10", "opc.bin11",
    "opc.bin12", "opc.bin13", "opc.bin14", "opc.bin15", "opc.bin16", "opc.bin17",
    "opc.bin18", "opc.bin19", "opc.bin20", "opc.bin21", "opc.bin22", "opc.bin23",
    "bin1MToF", "bin3MToF", "bin5MToF", "bin7MToF",
    "sample_period", "opc_sample_period",
    "sample_flow", "opc_sample_flow",
    "opc_pm1", "opc_pm25", "opc_pm10",
    "opcn3_pm1", "opcn3_pm25", "opcn3_pm10",
    "laser_status", "opc_laser_status",
    "opc_temp", "opc_rh", 
]

_NEPH_COLUMNS = [
    "pm1_std", "pm25_std", "pm10_std", 
    "pm1_env", "pm25_env", "pm10_env",
    "neph_pm1_std", "neph_pm25_std", "neph_pm10_std", 
    "neph_pm1_env", "neph_pm25_env", "neph_pm10_env",
    "neph_bin0", "neph_bin1", "neph_bin2", "neph_bin3", "neph_bin4", "neph_bin5",
]

_RHT_COLUMNS = [
    "sample_rh", "sample_temp", "rh", "temp"
]

_CO_COLUMNS = [
    "co", 
    "co_we", "co_ae", "co_diff", 
    "gases.co.we", "gases.co.ae", "gases.co.diff"
]

_NO_COLUMNS = [
    "no", 
    "no_we", "no_ae", "no_diff", 
    "gases.no.we", "gases.no.ae", "gases.no.diff"
]

_NO2_COLUMNS = [
    "no2", 
    "no2_we", "no2_ae", "no2_diff", 
    "gases.no2.we", "gases.no2.ae", "gases.no2.diff"
]

_O3_COLUMNS = [
    "o3",
    "ox_we", "ox_ae", "ox_diff",
    "o3_we", "o3_ae", "o3_diff",
    "gases.o3.we", "gases.o3.ae", "gases.o3.diff" 
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
        Gap(gap_in_seconds=60 * 60, post_gap_flag_length_seconds=4 * 60 * 60),
        # warmup_min_lipo_soc defaults to None here
    ],
    "FLAG_RHT": [
        # any one of these individually out-of-range
        Range(column="sample_rh", lo=0.0, hi=100.0),
        Range(column="sample_temp", lo=-60.0, hi=85.0),
        Range(column="rh", lo=0.0, hi=100.0),
        Range(column="temp", lo=-60.0, hi=85.0),

        # OR: both sample_rh and sample_temp are exactly 0.0
        Multiple(
            criteria=(
                Single(column="sample_rh", op="==", value=0.0),
                Single(column="sample_temp", op="==", value=0.0),
            ),
            logical_operator="AND",
            ),

        # OR: both rh and temp are exactly 0.0 (AND)
        Multiple(
            criteria=(
                Single(column="rh", op="==", value=0.0),
                Single(column="temp", op="==", value=0.0),
            ),
            logical_operator="AND",
            ),

        # QUESTION: do we need/want to flag when sample_temp/temp or sample_rh/rh are nan?
    ],
    }

CLOUDAPI_CRITERIA = {
    # flag criteria for cloudapi are the same as database
    **DATABASE_CRITERIA, 
}

RAWSD_CRITERIA = {
    **DATABASE_CRITERIA,
    # flag criteria for rawsd are similar to database, except for FLAG_STARTUP and FLAG_OPC
    "FLAG_STARTUP": [
        Gap(gap_in_seconds=60 * 60, post_gap_flag_length_seconds=4 * 60 * 60, warmup_min_lipo_soc=0.1)
    ],
}

FLAG_CRITERIA = {
    "database": DATABASE_CRITERIA,
    "cloudapi": CLOUDAPI_CRITERIA,
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
