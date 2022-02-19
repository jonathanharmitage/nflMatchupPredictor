import os

import pandas as pd
from dotenv import load_dotenv


class DataLoader:
    def __init__(self, verbose=False):
        self.verbose = verbose

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
            file_name = "/start{}.csv".format(nfl_year)
            for_verbose = "production"
        else:
            file_name = "/schedule{}.csv".format(nfl_year)
            for_verbose = "schedule"

        full_path = self.local_data_raw_dir + file_name
        data_tbl = pd.read_csv(full_path)

        if self.verbose:
            print(f"\n-- Data Source: {for_verbose} | Year: {nfl_year} | Rows: {data_tbl.shape[0]} --\n")

        return data_tbl

    def load_abbrev_table(self):
        """
        Load NFL team abbrevations.

        Returns
        -------
        dict
            _description_
        """
        abbrev_data_name = self.local_data_raw_dir + "/tm_abbrev.csv"
        abbrev_data = pd.read_csv(abbrev_data_name)
        to_dt = dict(zip(abbrev_data["team_name_a"], abbrev_data["team_name_b"]))

        return to_dt
