import pandas as pd
import numpy as np
from IPython.display import display

arr = np.array(
    [
        [1, 10, 20],
        [2, 20, 40],
        [3, 30, 60],
        [4, 40, 80]
    ]
)

df = pd.DataFrame(arr, columns=["A", "B", "C"])

print("========================================")
display(df)
print("\naxis=0")
display(df.apply(lambda x: x.sum(), axis=0))
print("\naxis=0, result_type='broadcast'")
display(df.apply(lambda x: x.sum(), axis=0, result_type='broadcast'))
print("\naxis=0, result_type='expand'")
display(df.apply(lambda x: x.sum(), axis=0, result_type='expand'))
print("\naxis=0, result_type='reduce'")
display(df.apply(lambda x: x.sum(), axis=0, result_type='reduce'))

def cal_multi_col(row):
    a = row['A'] * 2
    b = row['B'] * 3
    c = f"{a}:{b}"
    return a, b, c

print("========================================")
display(df)
print("\naxis=1")
display(df.apply(cal_multi_col, axis=1))
# print("\naxis=1, result_type='broadcast'")
# display(df.apply(cal_multi_col, axis=1, result_type='broadcast')) # 오류 뜸 
print("\naxis=1, result_type='expand'")
display(df.apply(cal_multi_col, axis=1, result_type='expand'))
print("\naxis=1, result_type='reduce'")
display(df.apply(cal_multi_col, axis=1, result_type='reduce'))
print("final!")
result1 = df.apply(cal_multi_col, axis=1, result_type='expand')
df[["D", "E", "F"]] = result1
display(df)
print("split!")
df[["G", "H"]] = df.apply(lambda row: row["F"].split(":") , axis=1, result_type="expand")
display(df)