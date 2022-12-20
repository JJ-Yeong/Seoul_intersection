# =========== 엑셀 파일 ===========

# EXCEL_FILE = "02 표준 2162 복정역-21년.xlsx"
EXCEL_FILE = None # None일 경우 INPUT_ROOT의 모든 파일에 대해 작업이 수행됨 
# INPUT_ROOT = "excel_input/total"
INPUT_ROOT = "excel_input/old"
OUTPUT_ROOT = "excel_output"

WRITE_SHEET1 = {
    "sheet_name": "조사시트1",
    "row_range1": range(21, 37),
    "col_range1": range(3, 15),
    "row_range2": range(39, 55),
    "col_range2": range(3, 15),
    }

WRITE_SHEET2 = {
    "sheet_name": "조사시트2",
    "row_range1": range(21, 37),
    "col_range1": range(3, 15),
    }

