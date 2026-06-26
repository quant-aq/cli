###############################################################################

"""variables.py 

Per-model data-quality flags.

Each flag has a name, an integer bitmask value, and the set of columns to set
to NaN when the flag is raised:

  * a list of column names -> NaN just those columns
  * an empty list          -> flag carries no column-level action
  * None                   -> NaN the entire row
"""
from collections import namedtuple

Flag = namedtuple("Flag", ["name", "value", "nan_columns"])

# Shared column groups, factored out so the per-model tables stay readable and
# the lists can't silently drift out of sync.
_OPC_COLUMNS_V1 = ["bin0", "bin1", "bin2", "bin3", "bin4", "bin5", "opc_flow"]

_OPC_COLUMNS = [
    "bin0", "bin1", "bin2", "bin3", "bin4", "bin5", "bin6", "bin7", "bin8", "bin9",
    "bin10", "bin11", "bin12", "bin13", "bin14", "bin15", "bin16", "bin17", "bin18", "bin19",
    "bin20", "bin21", "bin22", "bin23", "bin1MToF", "bin3MToF", "bin5MToF", "bin7MToF",
    "sample_period", "sample_flow", "opc_temp", "opc_rh", "opc_pm1", "opc_pm25", "opc_pm10",
    "laser_status",
]

_NEPH_COLUMNS = [
    "pm1_std", "pm25_std", "pm10_std", "pm1_env", "pm25_env", "pm10_env",
    "neph_bin0", "neph_bin1", "neph_bin2", "neph_bin3", "neph_bin4", "neph_bin5",
]

FLAGS = {}

FLAGS["v100"] = [
    Flag("FLAG_STARTUP", 1, []),
    Flag("FLAG_OPC", 2, _OPC_COLUMNS_V1),
    Flag("FLAG_TOTAL_COUNTS", 4, [
        "voc_raw", "pressure", "temp_manifold", "rh_manifold", "temp_box",
        "dew_point", "noise", "solar", "wind_dir", "wind_speed",
        "sample_time", "opc_flow", "manifold_temp", "manifold_rh",
    ]),
    Flag("FLAG_CO", 8, ["co_we", "co_ae"]),
    Flag("FLAG_NO", 16, ["no_we", "no_ae"]),
    Flag("FLAG_NO2", 32, ["no2_we", "no2_ae"]),
    Flag("FLAG_O3", 64, ["o3_we", "o3_ae"]),
    Flag("FLAG_OPC_RECORD_NUM", 128, _OPC_COLUMNS_V1),
    Flag("FLAG_CO2", 256, ["co2_raw"]),
    # Flag("FLAG_PP", 512, [...]),
    Flag("FLAG_ROW", 1024, None),
]

# v200 flags are identical to the v100 flags.
FLAGS["v200"] = FLAGS["v100"]

FLAGS["modulair_pm"] = [
    Flag("FLAG_STARTUP", 1, []),
    Flag("FLAG_OPC", 2, _OPC_COLUMNS),
    Flag("FLAG_NEPH", 4, _NEPH_COLUMNS),
    Flag("FLAG_RHTP", 8, ["sample_rh", "sample_temp", "sample_pres"]),
    Flag("FLAG_ROW", 1024, None),
]

FLAGS["modulair"] = [
    Flag("FLAG_STARTUP", 1, []),
    Flag("FLAG_OPC", 2, _OPC_COLUMNS),
    Flag("FLAG_NEPH", 4, _NEPH_COLUMNS),
    Flag("FLAG_RHT", 8, ["sample_rh", "sample_temp"]),
    Flag("FLAG_CO", 16, ["co_we", "co_ae", "co_diff"]),
    Flag("FLAG_NO", 32, ["no_we", "no_ae", "no_diff"]),
    Flag("FLAG_NO2", 64, ["no2_we", "no2_ae", "no2_diff"]),
    Flag("FLAG_O3", 128, ["ox_we", "ox_ae", "ox_diff", "o3_diff"]),
    Flag("FLAG_CO2", 256, ["co2_raw"]),
    Flag("FLAG_SO2", 512, ["so2_we", "so2_ae", "so2_diff"]),
    Flag("FLAG_H2S", 1024, ["h2s_we", "h2s_ae", "h2s_diff"]),
    Flag("FLAG_BAT", 2048, ["bat_voltage", "soc", "vbat"]),
]

SUPPORTED_MODELS = FLAGS.keys()

###############################################################################

Range = namedtuple("Range", ["column", "lo", "hi"])
Gap = namedtuple("Gap", ["gap_in_seconds", "post_gap_flag_length_seconds"])

FLAG_CRITERIA = {
    "database": {
        "default": { # for DB flags, criteria are consistent across all QuantAQ products
            "FLAG_STARTUP": [Gap(60 * 60, 60 * 60)],
            "FLAG_CO":  [Range("co_ae", 535.0, 800.0)],
            "FLAG_NO":  [Range("no_ae", 640.0, 900.0)],
            "FLAG_NO2": [Range("no2_ae", 1600.0, 1700.0)],
            "FLAG_O3":  [Range("o3_ae", 1600.0, 1700.0)],
            "FLAG_CO2": [Range("co2_raw", 1000.0, 5000.0)],
            "FLAG_OPC": [Range("bin0", 0.0, 1e6)],
            "FLAG_RHT": [
                Range("sample_rh", 0.0, 100.0),
                Range("sample_temp", -60.0, 85.0),
            ],
        },
    },
    "rawsd": { # for rawSD flags, criteria are NOT consistent
        #"modulair": { 
        #    "FLAG_STARTUP": [Gap(60 * 60, 60 * 60)], # placeholder
        #},
        #"modulair-x": { 
        #    "NO_FLAG_STARTUP": [Gap(60 * 60, 60 * 60)], # placeholder
        #},
    },
}

SUPPORTED_SOURCES = FLAG_CRITERIA.keys()


def get_flag_criteria(source, model):
    """
    source = 'rawsd' or 'database'
    model = 'default', 'modulair', 'modulair-x'
    """
    by_model = FLAG_CRITERIA[source]
    return by_model[model]
