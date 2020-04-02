import sys
from functools import partial
import pandas as pd
import numpy as np

import terc

printerr = partial(print, file=sys.stderr)

df_simc = pd.read_csv("./utils/SIMC_Urzedowy_2020-03-30.csv", delimiter=";")

def extend_sympod(df, on=["WOJ"]):
    """Add unambigous SYMPOD to Cities, insert SYMPOD row after City column"""
    df = df.copy()
    for i, row in df[df["SYMPOD"].isnull()].iterrows():
        # for o in on:
            # printerr(row[o])
            # printerr(df_simc[o] == row[o])
        matches = df_simc[lambda df_simc:
            (df_simc[on[0]] == row[on[0]]) &
            (df_simc["SYM"] == df_simc["SYMPOD"]) &
            (df_simc["NAZWA"] == row["City"])
        ]
        if len(matches) == 1:
            # printerr(matches.iloc[0]["SYMPOD"])
            df.loc[i, "SYMPOD"] = matches.iloc[0]["SYMPOD"]
        if len(matches) > 1:
            printerr("### CONFLICT", row["City"], len(matches))
            printerr(matches)
    return df

if __name__ == "__main__":
    # printerr(sys.argv)
    if len(sys.argv) < 2:
        printerr("Supply file as argument")
        exit()
    path = sys.argv[1]

    df = pd.read_csv(path)
    print(df)
    if "SYMPOD" not in df:
        city_index = list(df.columns).index("City")
        df.insert(city_index + 1,"SYMPOD", np.nan)

    del_woj = False
    if "WOJ" not in df:
        df["WOJ"] = np.nan
        df = terc.extend_woj(df)
        del_woj = True

    df_modified = extend_sympod(df)

    # insights
    df_diff = df_modified[(df_modified["SYMPOD"] != df["SYMPOD"]) & df_modified["SYMPOD"].notnull()]
    printerr("Records with missing SYMPOD:  ", len(df_modified[df_modified["SYMPOD"].isnull()]))
    printerr("Records with modified SYMPOD: ", len(df_diff))

    # cleanup before saving
    if del_woj:
        del df_modified["WOJ"]

    ans = input("Write to original file? [y/N]: ")
    if not ans.lower().startswith("y"):
        exit()
    printerr("Writing to", path)
    df_modified.to_csv(path, index=False)