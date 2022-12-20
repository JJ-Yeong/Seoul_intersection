import os
import pandas as pd
import json
import time
from IPython.display import display
from tqdm import tqdm
from pandas.core.frame import DataFrame as DF
# from copy import deepcopy

# ============================= Config ===================================
ROOT_BEFORE = "movement_before"
ROOT_AFTER = "movement_after"

RENAME_COLUMNS = {
    0: "time",
    1: "spot",
    2: "movement",
    3: "speed",
    4: "vtype"
}

RENAME_VTYPE = {
    "car": "small",
    "bus_s": "small",
    "bus_m": "large",
    "truck_s": "small",
    "truck_m": "large",
    "truck_x": "large",
}
# =========================================================================



with open("movement_postprocessing_dict.json", "r", encoding="utf-8") as j:
    json_file = json.load(j)

is_seperated = False
is_initialized = False
previous_path = None
concat_df = None
file_list = os.listdir(ROOT_BEFORE)
for file in file_list:
    day, spot = file.split("_a_")
    file_name, ext = os.path.splitext(spot)
    if not ext == ".txt":
        continue
    if file_name.endswith(")"):
        is_seperated = True
    if is_seperated and not file_name.endswith(")"):
        is_seperated = False
        is_initialized = True
    if isinstance(concat_df, DF) and file_name.endswith("1)"):
        is_initialized = True

    if is_initialized:
        concat_df.to_csv(previous_path, header=None, index=False, encoding="utf-8")
        print(f"Saved!! >>> {previous_path}")
        is_initialized = False
        concat_df = None

    rename_movement = json_file[file_name]
    file_path_before = os.path.join(ROOT_BEFORE, file)
    file_path_after = os.path.join(ROOT_AFTER, file)

    df = pd.read_csv(file_path_before, header=None, encoding="utf-8")
    df = df.rename(columns=RENAME_COLUMNS)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.replace({"movement":rename_movement})
    df = df.applymap(lambda x: str(x) if isinstance(x, int) else x)
    df = df.replace({"vtype":RENAME_VTYPE})
    # if file_name == "9.이수역(1)":
    #     df = df.replace({"spot":{"23":"9"}})
    # if file_name == "23.서초3동(2)":
    #     df = df.replace({"spot":{"9":"23"}})
    df_final = df[~df['movement'].str.contains("->", na=False, case=False)]

    if is_seperated:
        if file_name.endswith("(1)"):
            concat_df = df_final.copy()
        elif not file_name.endswith("(1)") and file_name.endswith(")"): 
            concat_df = pd.concat([concat_df, df_final])
            previous_file = day + "_a_" + file_name.split("(")[0] + ext
            previous_path = os.path.join(ROOT_AFTER, previous_file)
    else:
        # if file_name.endswith("1)"):
        #     continue
        df_final.to_csv(file_path_after, header=None, index=False, encoding="utf-8")
        print(f"Saved!! >>> {file_path_after}")
    concat_df.sort_values(by="time", inplace=True)
    
if is_seperated:
    concat_df.sort_values(by="time", inplace=True)
    concat_df.to_csv(previous_path, header=None, index=False, encoding="utf-8")
    print(f"Saved!! >>> {previous_path}")

