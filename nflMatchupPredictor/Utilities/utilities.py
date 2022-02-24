import os

import pandas as pd
from dotenv import load_dotenv


class Utilities:
    def __init__(self, verbose=False):
        self.verbose = verbose

        load_dotenv()
        self.local_data_raw_dir = os.getenv("LOCAL_RAW_DATA_DIR")

    def meta_features(self):

        meta_features = [
            "week",
            "predicting_for_week",
            "data_through_week_home",
            "home_team_name",
            "home_team_abbrev",
            "away_team_name",
            "away_team_abbrev",
            "home_team_wins",
            "agg_type",
        ]

        remove_features = ["away_team_name_abbrev", "data_through_week_away", "home_team_name_abbrev"]

        return meta_features, remove_features

    def arrange_features(self, data_object):
        meta_features, remove_features = self.meta_features()
        keep_feats_one = [i for i in data_object if i not in meta_features + remove_features]
        return meta_features + keep_feats_one

    def load_local(self, file_name):
        if ".csv" not in file_name:
            file_name += ".csv"

        return pd.read_csv(self.local_data_raw_dir + "/" + file_name)

    def write_local(self, data_object, write_name):
        if ".csv" not in write_name:
            write_name += ".csv"

        data_object.to_csv(self.local_data_raw_dir + "/" + write_name, index=False)
