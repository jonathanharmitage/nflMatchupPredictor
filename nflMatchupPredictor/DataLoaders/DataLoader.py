import os

import pandas as pd

from dotenv import load_dotenv
from nflMatchupPredictor.Scraping.Scraping import Scraping
from nflMatchupPredictor.Utilities.Utilities import Utilities


class DataLoader:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.utils = Utilities()

        load_dotenv()
        self.local_data_raw_dir = os.getenv("LOCAL_RAW_DATA_DIR")

    def load_data_by_year(self, nfl_year, production=True):
        """
        Load relevant raw data.

        Parameters
        ----------
        nfl_year : int
            _description_
        production : bool, optional
            _description_, by default True

        Returns
        -------
        DataFrame
            _description_
        """
        if production:
            file_name = "/start{}_new.csv".format(nfl_year)
            for_verbose = "production"
        else:
            file_name = "/schedule{}.csv".format(nfl_year)
            for_verbose = "schedule"

        full_path = self.local_data_raw_dir + file_name
        data_tbl = pd.read_csv(full_path)

        if self.verbose:
            print(
                f"\n-- Data Source: {for_verbose} | Year: {nfl_year} | Rows: {data_tbl.shape[0]} --\n"
            )

        return data_tbl

    def team_to_abbrev_map(self):
        """
        Loads a map of NFL team names to their abbreviations on pro-football-reference

        Returns
        -------
        dict
            Map from team name (e.g. 'Indianapolis Colts') to their abbreviation
            (e.g. 'clt').

        """
        abbrev_data = self.__load_abbrev_df()
        abbrev_data.columns = ["Team Name", "Team Abbr"]
        # return abbrev_data
        return dict(zip(abbrev_data["Team Name"], abbrev_data["Team Abbr"]))

    def abbrev_to_team_list_map(self):
        """
        Loads a map of NFL team abbreviations on pro-football-reference to a list
        of team names associated with that abbreviation. This includes old team
        names such as the Washington Redskins

        Returns
        -------
        team_list_map : dict
            Map from team abbreviation (e.g. 'clt') to a list of team names
            (e.g. ['Indianapolis Colts', 'Baltimore Colts']).

        """
        team_list_map = {}
        abbrev_data = self.__load_abbrev_df()

        for index in range(len(abbrev_data)):
            if abbrev_data.iloc[index, 1] not in team_list_map.keys():
                team_list_map[abbrev_data.iloc[index, 1]] = []
            team_list_map[abbrev_data.iloc[index, 1]].append(abbrev_data.iloc[index, 0])
        return team_list_map

    def __load_abbrev_df(self):
        if self.utils.file_exists("tm_abbrev"):
            abbrev_data = self.utils.load_local("tm_abbrev")
            return abbrev_data

        teams = Scraping().get_teams()
        df = pd.DataFrame({"Team Name": teams.keys(), "Team Abbr": teams.values()})
        return df


if __name__ == "__main__":
    clsDataLoader = DataLoader()
    # data_dt = clsDataLoader.team_to_abbrev_map()
    # print(f"\n\n-- Data DT: {list(data_dt.keys())} --\n\n")
    # print(data_dt)
