from collections import namedtuple

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
    "neph_pm1_env", "neph_pm25_env", "neph_pm10_env"
    "neph_bin0", "neph_bin1", "neph_bin2", "neph_bin3", "neph_bin4", "neph_bin5",
]

_RHTP_COLUMNS = [
    "sample_rh", "sample_temp", "sample_pres", "rh", "temp"
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
    Flag("FLAG_STARTUP", 1, []),
    Flag("FLAG_OPC", 2, _OPC_COLUMNS),
    Flag("FLAG_NEPH", 4, _NEPH_COLUMNS),
    Flag("FLAG_RHTP", 8, _RHTP_COLUMNS),
    Flag("FLAG_CO", 16, _CO_COLUMNS),
    Flag("FLAG_NO", 32, _NO_COLUMNS),
    Flag("FLAG_NO2", 64, _NO2_COLUMNS),
    Flag("FLAG_O3", 128, _O3_COLUMNS),
    Flag("FLAG_CO2", 256, ["co2_raw", "co2"]),
    Flag("FLAG_SO2", 512, ["so2_we", "so2_ae", "so2_diff", "so2"]),
    Flag("FLAG_H2S", 1024, ["h2s_we", "h2s_ae", "h2s_diff", "h2s"]),
    Flag("FLAG_BAT", 2048, ["bat_voltage", "soc", "vbat"]),
]

SUPPORTED_MODELS = ("modulair", "modulair-x", "modulair-pm", "modulair-x-pm")

# Types of flag criteria
Range = namedtuple("Range", ["column", "lo", "hi"])
Gap = namedtuple("Gap", ["gap_in_seconds", "post_gap_flag_length_seconds"])

FLAG_CRITERIA = {
    "database": {
        "default": {
            "FLAG_STARTUP": [
                Gap(60 * 60, 60 * 60)],
            "FLAG_CO":  [
                Range("co_ae", 535.0, 800.0),
                Range("gases.co.ae", 535.0, 800.0)
                ],
            "FLAG_NO":  [
                Range("no_ae", 640.0, 900.0),
                Range("gases.no.ae", 640.0, 900.0)
                ],
            "FLAG_NO2": [
                Range("no2_ae", 1600.0, 1700.0),
                Range("gases.no2.ae", 1600.0, 1700.0)
                ],
            "FLAG_O3":  [
                Range("o3_ae", 1600.0, 1700.0),
                Range("gases.o3.ae", 1600.0, 1700.0),
                ],
            "FLAG_CO2": [
                Range("co2_raw", 1000.0, 5000.0)],
            "FLAG_OPC": [
                Range("bin0", 0.0, 1e6),
                Range("opc.bin0", 0.0, 1e6)
                ],
            #"FLAG_NEPH": [],
            "FLAG_RHTP": [
                Range("sample_rh", 0.0, 100.0),
                Range("sample_temp", -60.0, 85.0),
                Range("rh", 0.0, 100.0),
                Range("temp", -60.0, 85.0),
            ]},
        },
    "rawsd": {} # different logic applies
    }

# Assume all quant-aq products share the same database flagging criteria.
for _model in SUPPORTED_MODELS:
    FLAG_CRITERIA["database"][_model] = FLAG_CRITERIA["database"]["default"]

# Assume cloudapi uses the same flag criteria as database
# (besides name of column to be flagged)
FLAG_CRITERIA["cloudapi"] = FLAG_CRITERIA["database"]

SUPPORTED_SOURCES = FLAG_CRITERIA.keys()

def get_flag_criteria(source, model):
    """
    source = 'rawsd' or 'database'
    model = 'default', 'modulair', 'modulair-x'
    """
    if source == 'rawsd':
        logger.debug("{!r} flag criteria are not yet defined", source)
        raise NotImplementedError
    by_model = FLAG_CRITERIA[source]
    return by_model[model]
