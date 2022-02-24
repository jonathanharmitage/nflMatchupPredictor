import os

import pandas as pd
from dotenv import load_dotenv


class Utilities:
    def __init__(self, verbose=False):
        self.verbose = verbose

        load_dotenv()
        self.local_data_raw_dir = os.getenv("LOCAL_RAW_DATA_DIR")

    def meta_features(self):
        """
        Categorize features as **meta** as well as flag certain features fro removal.

        Returns
        -------
        List
            Features that serve as identifiers.
        List
            Features flagged for removal.
        """

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

        remove_features = [
            "away_team_name_abbrev",
            "data_through_week_away",
            "home_team_name_abbrev",
        ]

        return meta_features, remove_features

    def arrange_features(self, data_object):
        """
        Arrange features (columns) in a logical ordering.

        Parameters
        ----------
        data_object : DataFrame

        Returns
        -------
        List
            Features from `data_object` arranged in a logical order.
        """
        meta_features, remove_features = self.meta_features()
        keep_feats_one = [
            i for i in data_object if i not in meta_features + remove_features
        ]
        return meta_features + keep_feats_one

    def features_need(self):
        """
        Relevant features to be utilized for downstream tasks.

        Returns
        -------
        dict
        """
        id_feats = ["nfl_season", "week", "nfl_team"]

        score_feats = ["score_tm", "score_opp"]

        offense_feats = [
            "offense_1std",
            "offense_totyd",
            "offense_passy",
            "offense_rushy",
            "offense_to",
        ]
        defense_feats = [
            "defense_1std",
            "defense_totyd",
            "defense_passy",
            "defense_rushy",
            "defense_to",
        ]

        engineer_feats = [
            "score_diff_home_team",
            "scored_more_than_opp_home_team",
            "score_diff_away_team",
            "scored_more_than_opp_away_team",
            "turnover_diff_home_team",
            "turnover_diff_binary_home_team",
            "turnover_diff_away_team",
            "turnover_diff_binary_away_team",
            "offense_totyd_diff_home_vs_away",
            "defense_totyd_diff_home_vs_away",
        ]

        dt = {
            "all_need": id_feats + score_feats + offense_feats + defense_feats,
            "all_prod": score_feats + offense_feats + defense_feats,
            "diff_prod": engineer_feats,
        }

        return dt

    def load_local(self, file_name):
        """
        Load data from local directory.

        Parameters
        ----------
        file_name : str
            Name of file to be loaded. Do not include the residing directory.

        Returns
        -------
        DataFrame
            _description_
        """
        if ".csv" not in file_name:
            file_name += ".csv"

        return pd.read_csv(self.local_data_raw_dir + "/" + file_name)

    def write_local(self, data_object, write_name):
        """
        Write data to a local directory as a CSV.

        Parameters
        ----------
        data_object : DataFrame
        write_name : str
            Name of file to be saved. Do not include the residing directory.
        """
        if ".csv" not in write_name:
            write_name += ".csv"

        data_object.to_csv(self.local_data_raw_dir + "/" + write_name, index=False)
