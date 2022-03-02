import os

import pandas as pd

from dotenv import load_dotenv
from pathlib import Path
from enum import Enum, auto


class FileFormat(Enum):
    CSV = auto()
    Pickle = auto()
    NA = auto()


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

    def load_local(self, file_name, file_format=FileFormat.CSV):
        """
        Load data from local directory.

        Parameters
        ----------
        file_name : str
            Name of file to be loaded. Do not include the residing directory.
        file_format : FileFormat, optional
            Format of the file to load from the FileFormat enum.
            The default is FileFormat.CSV.

        Raises
        ------
        NotImplementedError
            _description_

        Returns
        -------
        DataFrame
            _description_

        """

        file_name = self.__format_filename(file_name, file_format)

        if file_format is FileFormat.CSV:
            return pd.read_csv(self.__full_filepath(file_name))
        elif file_format is FileFormat.Pickle:
            return pd.read_pickle(self.__full_filepath(file_name))

        raise NotImplementedError(f"File format {file_format} not implemented")

    def write_local(self, data_object, file_name, file_format=FileFormat.CSV):
        """
        Write data to a local directory in the specified file format.

        Parameters
        ----------
        data_object : DataFrame
        file_name : str
            Name of file to be saved. Do not include the residing directory.
        file_format : FileFormat, optional
            Format of the file to write from the FileFormat enum.
            The default is FileFormat.CSV.

        """

        file_name = self.__format_filename(file_name, file_format)
        if not os.path.exists(self.local_data_raw_dir):
            os.makedirs(self.local_data_raw_dir)

        if file_format is FileFormat.CSV:
            data_object.to_csv(self.__full_filepath(file_name), index=False)
        elif file_format is FileFormat.Pickle:
            data_object.to_pickle(self.__full_filepath(file_name))

    def file_exists(self, file_name, file_format=FileFormat.CSV):
        """
        Checks if the file exists

        Parameters
        ----------
        file_name : str
            Filename to check for.
        file_format : FileFormat, optional
            Format of the file to check.
            The default is FileFormat.CSV.

        Returns
        -------
        bool
            True if the file exists, otherwise False.

        """
        file_name = self.__format_filename(file_name, file_format)
        filepath = Path(f"{self.local_data_raw_dir}/{file_name}")
        return filepath.exists()

    def __format_filename(self, file_name, file_format):
        if self.__file_extension(file_format) not in file_name:
            file_name += self.__file_extension(file_format)

        return file_name

    def __file_extension(self, file_format):
        if file_format == FileFormat.CSV:
            return ".csv"
        elif file_format == FileFormat.Pickle:
            return ".pkl"

        raise NotImplementedError(f"File format {file_format} not implemented")

    def __full_filepath(self, file_name):
        return self.local_data_raw_dir + "/" + file_name
