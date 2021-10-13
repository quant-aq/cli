"""
Flags are in format (name, value, columns to NaN)
"""
FLAGS = dict()

FLAGS["v100"] = [
    ("FLAG_STARTUP", 1, []),
    ("FLAG_OPC", 2, ["bin0", "bin1", "bin2", "bin3", "bin4", "bin5", "opc_flow"]),
    ("FLAG_TOTAL_COUNTS", 4, ["voc_raw", "pressure", "temp_manifold", "rh_manifold", "temp_box", 
                                "dew_point", "noise", "solar", "wind_dir", "wind_speed", 
                                "sample_time", "opc_flow", "manifold_temp", "manifold_rh"]),
    ("FLAG_CO", 8, ["co_we", "co_ae"]),
    ("FLAG_NO", 16, ["no_we", "no_ae"]),
    ("FLAG_NO2", 32, ["no2_we", "no2_ae"]),
    ("FLAG_O3", 64, ["o3_we", "o3_ae"]),
    ("FLAG_OPC_RECORD_NUM", 128, ["bin0", "bin1", "bin2", "bin3", "bin4", "bin5", "opc_flow"]),
    ("FLAG_CO2", 256 , ["co2_raw"]),
    # ("FLAG_PP", 512, ),
    ("FLAG_ROW", 1024, None)
]

# flags for the v200 are the same as the v100
FLAGS["v200"] = FLAGS["v100"]

FLAGS["modulair_pm"] = [
    ("FLAG_STARTUP", 1, []),
    ("FLAG_OPC", 2, ["bin0", "bin1", "bin2", "bin3", "bin4", "bin5", "bin6", "bin7", "bin8", "bin9",
                        "bin10", "bin11", "bin12", "bin13", "bin14", "bin15", "bin16", "bin17", "bin18", "bin19",
                        "bin20", "bin21", "bin22", "bin23", "bin1MToF", "bin3MToF", "bin5MToF", "bin7MToF",
                        "sample_period", "sample_flow", "opc_temp", "opc_rh", "opc_pm1", "opc_pm25", "opc_pm10", "laser_status"]),
    ("FLAG_NEPH", 4, ["pm1_std", "pm25_std", "pm10_std", "pm1_env", "pm25_env", "pm10_env", 
                        "neph_bin0", "neph_bin1", "neph_bin2", "neph_bin3", "neph_bin4", "neph_bin5"]),
    ("FLAG_RHTP", 8, ["sample_rh", "sample_temp", "sample_pres"]),
    ("FLAG_ROW", 1024, None)
]

FLAGS["modulair"] = [
    ("FLAG_STARTUP", 1, []),
    ("FLAG_OPC", 2, ["bin0", "bin1", "bin2", "bin3", "bin4", "bin5", "bin6", "bin7", "bin8", "bin9",
                        "bin10", "bin11", "bin12", "bin13", "bin14", "bin15", "bin16", "bin17", "bin18", "bin19",
                        "bin20", "bin21", "bin22", "bin23", "bin1MToF", "bin3MToF", "bin5MToF", "bin7MToF",
                        "sample_period", "sample_flow", "opc_temp", "opc_rh", "opc_pm1", "opc_pm25", "opc_pm10", "laser_status"]),
    ("FLAG_NEPH", 4, ["pm1_std", "pm25_std", "pm10_std", "pm1_env", "pm25_env", "pm10_env", 
                        "neph_bin0", "neph_bin1", "neph_bin2", "neph_bin3", "neph_bin4", "neph_bin5"]),
    ("FLAG_RHT", 8, ["sample_rh", "sample_temp"]),
    ("FLAG_CO", 16, ["co_we", "co_ae", "co_diff"]),
    ("FLAG_NO", 32, ["no_we", "no_ae", "no_diff"]),
    ("FLAG_NO2", 64, ["no2_we", "no2_ae", "no2_diff"]),
    ("FLAG_O3", 128, ["ox_we", "ox_ae", "ox_diff", "o3_diff"]),
    ("FLAG_CO2", 256, ["co2_raw"]),
    ("FLAG_SO2", 512, ["so2_we", "so2_ae", "so2_diff"]),
    ("FLAG_H2S", 1024, ["h2s_we", "h2s_ae", "h2s_diff"]),
    ("FLAG_BAT", 2048, ["bat_voltage", "soc", "vbat"]),
]

SUPPORTED_MODELS = FLAGS.keys()