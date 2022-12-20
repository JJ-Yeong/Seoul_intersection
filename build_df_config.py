############################## 성남(서울대 실증) 데이터 ##############################
"""
주의사항

1. 한 달 내의 데이터만 분석 가능
    ※ 다른 달 데이터가 들어가게 되면 DAY나 TIME이 같을 경우 정렬 과정에서 꼬일 수 있음

2. PH_YEAR, PH_MONTH, PH_DAY, PH_TIME, PH_SPOT_MOVE_DICT은 build_empty_df(교통량 0인 placeholder를 만들기 위한 함수)에서 사용함
    ※ df.unique().tolist()를 사용하지 않고 config로 따로 받는 이유?
        > df에 누락이 발생할 경우 특정 cond조합 자체가 placeholder에 반영되지 않을 수 있기 때문에 zero_outlier검수가 제대로 이루어지지 않을 우려가 있음
"""

# TXT_FILE: .txt파일|디렉토리
# ARBITRARY_DATE: True 또는 False. True입력 시 .txt파일 내용을 데이터프레임으로 만들 때 임의의 날짜를 대신 사용함 (현재 0000년 00월 00일로 하드코딩 되어있음)
# PH_YEAR: 정수|문자열. None 입력시 해당 파일의 날짜를 그대로 가져옴. ex) 2022 | "2022"
# PH_MONTH: 정수|문자열. None 입력시 해당 파일의 날짜를 그대로 가져옴. ex) 6 | "6" | "06"
# PH_DAY: 정수|문자열로 구성된 리스트. None 입력시 해당 파일의 날짜를 그대로 가져옴. ex) [9, 10, 11] | [i for i range(9, 12)] | ["9", "10", "11"] | ["09", "10", "11"]
# PH_VTYPE: 문자열로 구성된 리스트. ex) ["car", "bus_s", "bus_m", "truck_s", "truck_m", "truck_x"]
# PH_TIME: 정수|문자열로 구성된 리스트, 또는 딕셔너리.
# PH_SPOT_MOVE_DICT: key로 지점번호, value로 방향(movement)을 받는 딕셔너리   /   지점번호: 정수|문자열 , 방향: 정수|문자열로 구성된 리스트

TXT_FILE = "movement_after"

ARBITRARY_DATE = False
PH_YEAR = None
PH_MONTH = None
PH_DAY = None
PH_VTYPE = ["small", "large"]
PH_TIME = {
    "07": range(30, 60),
    "08": range(0, 60),
    "09": range(0, 30),
    "14": range(0, 60),
    "15": range(0, 60),
    "17": range(30, 60),
    "18": range(0, 60),
    "19": range(0, 30)
    }

PH_SPOT_MOVE_DICT = {
    2: [11],
    3: [12],
    7: [11],
    9: [12],
    15: [11],
    18: [9],
    19: [10],
    20: [8, 9],
    22: [1, 12],
    23: [6],
    26: [12],
    28: [9],  # 12 못잡음
    34: [12], # 4 못잡음
    37: [9],
    39: [9],
    }


# TXT_FILE = "movement_after"

# PH_VTYPE = ["small", "large"]
# PH_YEAR = None
# PH_MONTH = None
# PH_DAY = None
# PH_TIME = {
#     "07": range(30, 60),
#     "08": range(0, 60),
#     "09": range(0, 30),
#     "14": range(0, 60),
#     "15": range(0, 60),
#     "17": range(30, 60),
#     "18": range(0, 60),
#     "19": range(0, 30)
#     }
# PH_SPOT_MOVE_DICT = {
#     1: [i for i in range(1, 13)],
#     2: [i for i in range(1, 13)],
#     3: [i for i in range(1, 13)],
#     4: [i for i in range(1, 13)],
#     5: [i for i in range(1, 13)],
#     6: [i for i in range(1, 13)],
#     7: [i for i in range(1, 13)],
#     8: [i for i in range(1, 13)],
#     9: [i for i in range(1, 13)],
#     10: [i for i in range(1, 13)],
#     11: [i for i in range(1, 13)],
#     12: [i for i in range(1, 13)],
#     13: [i for i in range(1, 13)],
#     14: [i for i in range(1, 15)],  # 5지 교차로
#     15: [i for i in range(1, 13)],
#     16: [i for i in range(1, 13)],
#     17: [i for i in range(1, 13)],
#     18: [i for i in range(1, 13)],
#     19: [3, 9, 10],                 # 3, 9, 10 밖에 못잡음
#     20: [i for i in range(1, 13)],
#     21: [i for i in range(1, 13)],
#     22: [i for i in range(1, 13)],
#     23: [i for i in range(1, 13)],
#     24: [1, 2, 5, 6, 7, 8, 9, 11, 12], # 3, 4, 10 못잡음
#     25: [i for i in range(1, 13)],
#     26: [i for i in range(1, 13)],
#     27: [i for i in range(1, 13)],
#     28: [i for i in range(1, 12)],  # 12 못잡음
#     29: [i for i in range(1, 13)],  
#     30: [4, 5, 6, 7, 10, 12],   # 3지 교차로
#     31: [1, 2, 3, 6, 10, 11],   # 3지 교차로
#     32: [1, 3, 6, 10, 11],      # 2 못잡음
#     33: [i for i in range(1, 13)],
#     34: [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12], # 4 못잡음
#     35: [i for i in range(1, 13)], 
#     36: [i for i in range(1, 13)],
#     37: [i for i in range(1, 13)],
#     38: [i for i in range(1, 13)],
#     39: [i for i in range(1, 13)],
#     40: [i for i in range(1, 13)],
#     }