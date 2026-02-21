#read CSVs, return Python objects (dicts, lists, etc.) that can be used by the rest of the codebase
import pandas as pd

def load_data(path):
    x = pd.read_csv(path)
    y = x.to_dict(orient='records')
    return y