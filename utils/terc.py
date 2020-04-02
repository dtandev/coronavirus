
'''
Command line utility to extend currently existing records with TARC designators
Usage:

$ python utils/terc.py "data/

'''
import sys
from functools import partial
import pandas as pd

printerr = partial(print, file=sys.stderr)

woj_dict = {'Dolnośląskie': 2,
 'Kujawsko-pomorskie': 4,  # TODO: cleanup main CSV for consistency
 'Lubelskie': 6,
 'Lubuskie': 8,
 'Łódzkie': 10,
 'Małopolskie': 12,
 'Mazowieckie': 14,
 'Opolskie': 16,
 'Podkarpackie': 18,
 'Podlaskie': 20,
 'Pomorskie': 22,
 'Śląskie': 24,
 'Świętokrzyskie': 26,
 'Warmińsko-Mazurskie': 28,
 'Wielkopolskie': 30,
 'Zachodniopomorskie': 32}

def extend_woj(df):
    """Map WOJ codes to Provinces and insert them before Province column"""
    if "WOJ" not in df:
        province_index = list(df.columns).index("Province")
        df.insert(province_index,"WOJ", len(df) * [None])
    col_woj_name = df["Province"].apply(lambda p: woj_dict.get(p, None))
    df["WOJ"] = col_woj_name
    return df

if __name__ == "__main__":
    # printerr(sys.argv)
    if len(sys.argv) < 2:
        printerr("Supply file as argument")
        exit()
    path = sys.argv[1]
    df = pd.read_csv(path)
    df = extend_woj(df)
    df.to_csv(path, index=False)
