import os
import glob
from build_df import preprocess_grouping, build_final_df

from build_df_config import TXT_FILE


if os.path.isdir(TXT_FILE):
    path_list = glob.glob(os.path.join(TXT_FILE, "*"))
    df = preprocess_grouping(path_list)
elif os.path.splitext(TXT_FILE)[-1] == ".txt":
    df = preprocess_grouping(TXT_FILE)
else:
    raise Exception("'TXT_FILE'은 디렉토리 혹은 .txt 파일이어야 합니다!")

final_df = build_final_df(df)
final_df["지점"] = final_df["지점"].apply(lambda x: x.zfill(2))
final_df["방향"] = final_df["방향"].apply(lambda x: x.zfill(2))
final_df.sort_values(by=["지점", "방향", "차종", "h", "m"], inplace=True)
# object_col = final_df.select_dtypes(['object'])
# final_df[object_col.columns] = object_col.apply(lambda x: x.astype('category'))
final_df = final_df.reset_index()
agg_d = {
    "지점":"first",
    "연월일":"first",
    "일":"first",
    "h":"first",
    "m":"first",
    "hm":"first",
    "방향":"first",
    "차종":"first",
    "교통량":"sum"
    }
fifteen_df = final_df.groupby(final_df.index // 15).agg(agg_d)
fifteen_final_df = fifteen_df.pivot_table(index=["지점",
"hm", "차종"], columns=["방향"], values="교통량", fill_value=0).reset_index()
fifteen_final_df.rename_axis(None, axis=1, inplace=True) # axis_1 의 축이름 제거 ("방향" -> None)
# for spot in fifteen_final_df["지점"].unique():
#     print(f"{spot}지점 : {len(fifteen_final_df.loc[fifteen_final_df['지점'] == spot])}rows")
print("dd")