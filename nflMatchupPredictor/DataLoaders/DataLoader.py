import os

import pandas as pd

from dotenv import load_dotenv
from nflMatchupPredictor.Scraping.Scraping import Scraping
from nflMatchupPredictor.Utilities.utilities import (Utilities)

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

    def load_abbrev_table(self):
        """
        Load NFL team abbrevations.

        Returns
        -------
        dict
            _description_
        """
        if self.utils.file_exists('tm_abbrev'):
            abbrev_data = self.utils.load_local('tm_abbrev')
            return dict(zip(abbrev_data["Team Name"], abbrev_data["Team Abbr"]))
        
        teams = Scraping().get_teams()
        df = pd.DataFrame({'Team Name': teams.keys(), 'Team Abbr': teams.values()})
        self.utils.write_local(df, 'tm_abbrev')
        return teams
        
