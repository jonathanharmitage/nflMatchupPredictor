import os

import pandas as pd


from dotenv import load_dotenv
from Scraping.GeneralDataScraper import GeneralDataScraper
from Scraping.TeamDataScraper import TeamDataScraper
from Utilities.Utilities import Utilities, FileFormat


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

    def load_data_by_team_and_year(self, team_abb, year, reload=False):
        """
        Loads teams schedule and game data by year. Loads from a file when available
        otherwise scrapes the data and saves it to the file for quicker access later.

        Parameters
        ----------
        team_abb : str
            Teams abbreviation used by PFR.
        year : int
            Year to get data from.
        reload : bool, optional
            If true the data will be rescraped from PFR even if it is present in the
            file. Mainly used for current year data that will be added to.
            The default is False.

        Returns
        -------
        DataFrame
            DESCRIPTION.

        """
        updated = False
        if self.utils.file_exists(team_abb, file_format=FileFormat.Pickle):
            data = self.utils.load_local(team_abb, file_format=FileFormat.Pickle)
        else:
            data = pd.DataFrame()

        if reload:
            data.drop(year, inplace=True)

        if year not in data.index.unique(0).array:
            tds = TeamDataScraper(team_abb)
            year_data = tds.get_schedule(year)
            data = pd.concat([data, pd.concat({year: year_data})])
            updated = True

        if updated:
            self.utils.write_local(data, team_abb, file_format=FileFormat.Pickle)

        return data.loc[year]

    def team_to_abbrev_map(self):
        """
        Loads a map of NFL team names to their abbreviations on
        pro-football-reference

        Returns
        -------
        dict
            Map from team name (e.g. 'Indianapolis Colts') to their
            abbreviation (e.g. 'clt').

        """
        abbrev_data = self.__load_abbrev_df()
        abbrev_data.columns = ["Team Name", "Team Abbr"]
        # return abbrev_data
        return dict(zip(abbrev_data["Team Name"], abbrev_data["Team Abbr"]))

    def abbrev_to_team_list_map(self):
        """
        Loads a map of NFL team abbreviations on pro-football-reference to a
        list of team names associated with that abbreviation. This includes
        old team names such as the Washington Redskins

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

        teams = GeneralDataScraper().get_all_teams()

        df = pd.DataFrame({"Team Name": teams.keys(), "Team Abbr": teams.values()})
        self.utils.write_local(df, "tm_abbrev")

        return df


if __name__ == "__main__":
    clsDataLoader = DataLoader()
    # data_dt = clsDataLoader.team_to_abbrev_map()
    # print(f"\n\n-- Data DT: {list(data_dt.keys())} --\n\n")
    # print(data_dt)
