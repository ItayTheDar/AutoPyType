import pandas as pd


def get_data_frame_from_path(path_to_csv, num_to_return):
    df = pd.read_csv(path_to_csv)
    return df.sample(n=num_to_return)
