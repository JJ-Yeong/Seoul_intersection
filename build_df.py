from rich.progress import track
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame as DF
from IPython.display import display
import itertools
import time

from build_df_config import *


def dataloader(
    path: str,                      # 파일 경로
    isin_list: list=None            # 특정 방향에 대해서만 볼 때 사용 (방향 표기가 화살표 형식일 경우에만 사용)
    ) -> DF:
    '''
    input: 파일 경로
    output: 한 프레임당 한 컬럼
    '''

    df_raw = pd.read_csv(path, encoding="utf-8", header=None, low_memory=False)
    df_raw.rename(columns={0:"연월일시간", 1:"지점", 2:"방향", 3:"속도", 4:"차종"}, inplace=True)
    df_raw["연월일"] = df_raw["연월일시간"].apply(lambda x: x.split(" ")[0])
    df_raw["일"] = df_raw["연월일"].apply(lambda x: x.split("-")[2])
    df_raw["시간"] = df_raw["연월일시간"].apply(lambda x: x.split(" ")[1])
    df_raw["h"] = df_raw["시간"].apply(lambda x: x.split(":")[0])
    df_raw["m"] = df_raw["시간"].apply(lambda x: x.split(":")[1])
    
    try:
        df_raw["s"] = df_raw["시간"].apply(lambda x: x.split(":")[2].split(".")[0])
        df_raw["ms"] = df_raw["시간"].apply(lambda x: x.split(":")[2].split(".")[1])
    except:
        # 원래 00.00 식으로 밀리초가 표시되는데 간혹 00으로만 끝나서 밀리초가 제공되지 않는 경우가 있음
        print(f"밀리초 단위가 생략되었습니다! >>> {path}")
        df_raw["s"] = df_raw["시간"].apply(lambda x: x.split(":")[2])
        df_raw["ms"] = "00"

    df_raw["hm"] = df_raw["h"] + ":" + df_raw["m"]
    df_raw["교통량"] = 1
    df_raw["차종"] = df_raw["차종"].apply(lambda x: x.strip())
    df_raw["방향"] = df_raw["방향"].apply(lambda x: str(x).strip())
    df_raw["지점"] = df_raw["지점"].astype(str)
    if ARBITRARY_DATE:
        df_raw["연월일"] = "0000-00-00"
        df_raw["일"] = "00"

    df_raw.reset_index(drop=True, inplace=True)

    if isin_list: df_raw = df_raw.loc[df_raw["방향"].isin(isin_list)]
    df = df_raw[["연월일", "일", "h", "m", "s", "ms", "hm", "지점", "방향", "차종", "교통량"]].reset_index(drop=True)

    return df


# 한 프레임당 한 컬럼
def preprocess_grouping(
    path: str,                  # 디렉토리 혹은 파일 경로
    isin_list: list=None,       # 특정 방향에 대해서만 볼 때 사용 (방향 표기가 화살표 형식일 경우에만 사용)
    ) -> DF:
    '''
    input: 디렉토리 혹은 파일 경로
    output: 1분당 1컬럼 + 교통량0 표현X
    '''
    print("\n[Step1] 분단위로 grouping 수행...")
    if isinstance(path, list) and isin_list is None: # path: 여러 파일, isin_list: 사용X
        df = dataloader(path[0])
        for p in path[1:]:
            df = pd.concat([df, dataloader(p)])
    elif isinstance(path, list) and np.array(isin_list).ndim == 2:  # path: 여러 파일, isin_list: 사용O
        assert len(path) == len(isin_list), "isin_list의 개수는 path의 개수와 같아야 합니다."
        df = dataloader(path[0], isin_list[0])
        for p, isin in zip(path[1:], isin_list[1:]):
            df = pd.concat([df, dataloader(p, isin)])
    elif isinstance(path, str): # path: 한 파일, isin_list: 유무 상관없음
        df = dataloader(path, isin_list)
    else:
        Exception("path가 리스트일 때 isin_list는 2차원 리스트여야 합니다!")

    grouped_df = df.groupby(["연월일", "일", "h", "m", "hm", "지점", "방향", "차종"], as_index=False).agg({"교통량":lambda x:np.sum(x)})
    grouped_df.reset_index(drop=True, inplace=True)
    return grouped_df


def build_empty_df(ph_vtype, ph_year, ph_month, ph_day, ph_time, ph_spot_move_dict) -> DF:
    '''
    output: 1분당 한 컬럼 + 교통량 0 표현을 위한 placeholder
    '''
    print("\n[Step2] placeholder 생성...")
    list_vtype = ph_vtype
    placeholder_year = str(ph_year)
    placeholder_month = str(ph_month).zfill(2)
    list_day = list(map(lambda x: str(x).zfill(2), ph_day)) if isinstance(ph_day, list) else [str(ph_day)]
    placeholder_time = [str(ph_time).zfill(2)] if isinstance(ph_time, (str, int)) else ph_time
    move_dict = {str(key): list(map(lambda x: str(x), val)) for key, val in ph_spot_move_dict.items()}

    list_hm = []
    list_spot = list(move_dict.keys())
    if isinstance(placeholder_time, list): 
        for h in placeholder_time:
            list_hm.extend([f"{str(h).zfill(2)}:{str(m).zfill(2)}" for m in range(60)])
    elif isinstance(placeholder_time, dict):
        for h, list_m in placeholder_time.items():
            list_hm.extend([f"{str(h).zfill(2)}:{str(m).zfill(2)}" for m in list_m])
    else:
        if not isinstance(placeholder_time, (str, int)):
            raise Exception("PH_TIME은 리스트, 딕셔너리, 문자열, 정수만 받습니다!")

    empty_df = pd.DataFrame(columns=['지점','일', 'h', 'm', '방향', '차종'])
    for spot in track(list_spot):
        list_move = move_dict[spot]
        lists = [[spot], list_day, list_hm, list_move, list_vtype]
        # combinations = [p for p in itertools.product(*lists)]
        combinations = []
        for s, day, hm, move, vtype in itertools.product(*lists):
            hour, minute = hm.split(":")
            combinations.append([s, day, hour, minute, hm, move, vtype])
        empty = pd.DataFrame(combinations, columns=['지점','일', 'h', 'm', 'hm', '방향', '차종']) # 연월일, h, m, 교통량 추가 필요
        empty_df = pd.concat([empty_df, empty])

    # 이 부분은 apply하는거보다 product 돌리면서 수행하는게 훨씬 빠름
    # start = time.time()
    # empty_df[["h", "m"]] = empty_df.apply(lambda row: row["hm"].split(":"), axis=1, result_type="expand")
    # lead_time_1 = time.time() - start
    # print(f"apply1 : 소요시간 {lead_time_1//60}분 {lead_time_1%60}초")

    start = time.time()
    empty_df["연월일"] = empty_df["일"].apply(lambda x: f"{placeholder_year}-{placeholder_month}-{x}")
    lead_time_2 = time.time() - start
    print(f"apply2 : 소요시간 {lead_time_2//60}분 {lead_time_2%60:.2f}초")

    empty_df["교통량"] = 0
    empty_df = empty_df[['지점', '연월일', '일', 'h', 'm', 'hm', '방향', '차종', '교통량']]
    return empty_df


def build_final_df(grouped_df: DF, print_result: bool=False) -> DF:
    '''
    input: 1분당 1컬럼 + 교통량0 표현X
    output: 1분당 1컬럼 + 교통량0 표현O
    '''

    year, month, day = grouped_df["연월일"].unique().tolist()[0].split("-")

    ph_vtype = PH_VTYPE
    ph_year = PH_YEAR if PH_YEAR else year
    ph_month = PH_MONTH if PH_MONTH else month
    ph_day = PH_DAY if PH_DAY else day
    ph_time = PH_TIME
    ph_spot_move_dict = PH_SPOT_MOVE_DICT
        
    empty_df = build_empty_df(ph_vtype, ph_year, ph_month, ph_day, ph_time, ph_spot_move_dict)
    print("\n[Step3] 최종 df 형성...")
    # final_df = pd.merge(empty_df.drop(columns="교통량"), grouped_df, on=['지점', '연월일', '일', 'h', 'm', 'hm', '방향', '차종'], how="left")
    final_df = pd.merge(empty_df.drop(columns="교통량"), grouped_df.drop(columns=["연월일", "일"]), on=['지점', 'h', 'm', 'hm', '방향', '차종'], how="left")
    final_df.reset_index(drop=True, inplace=True)

    if print_result:
        print(f"※ 전체 {len(final_df)}개의 row 중 {final_df['교통량'].notnull().sum()}개가 덧씌워졌습니다!")
        # display(final_df["교통량"].value_counts().to_frame().transpose())
        # display(grouped_df["교통량"].value_counts().to_frame().transpose())
        merge_df = pd.merge(final_df, grouped_df, how="outer", indicator=True) #, on=["연월일", "일", "h", "m", "hm", "지점", "방향"])
        ignored_df = merge_df.query("_merge == 'right_only'")
        print(f"※ 무시된 데이터: {len(ignored_df)}개")
        display(ignored_df)

    final_df["교통량"].fillna(0, inplace=True)

    return final_df