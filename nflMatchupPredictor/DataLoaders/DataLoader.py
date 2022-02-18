import os

import numpy as np
import pandas as pd
from dotenv import load_dotenv


class DataLoader:
    def __init__(self, verbose=False):
        self.verbose = verbose

        load_dotenv()
        self.local_data_raw_dir = os.getenv("LOCAL_RAW_DATA_DIR")

    def load_data_by_year(self, nfl_year, prod=True):
        # abbrev_data_name = "/Users/jonathanarmitage/Documents/dt-internal-projects/nfl-matchup-predictor/data/raw/start{}.csv"
        if prod:
            file_name = "/start{}.csv".format(nfl_year)
            for_verbose = "production"
        else:
            file_name = "/schedule{}.csv".format(nfl_year)
            for_verbose = "schedule"

        full_path = self.local_data_raw_dir + file_name
        data = pd.read_csv(full_path)

        if self.verbose:
            print(
                f"\n-- Data Source: {for_verbose} | Year: {nfl_year} | Rows: {data.shape[0]} --\n"
            )
        return data

    def load_abbrev_table(self):
        # abbrev_data_name = "/Users/jonathanarmitage/Documents/dt-internal-projects/nfl-matchup-predictor/data/raw/tm_abbrev.csv"
        abbrev_data_name = self.local_data_raw_dir + "/tm_abbrev.csv"
        abbrev_data = pd.read_csv(abbrev_data_name)
        to_dt = dict(zip(abbrev_data["team_name_a"], abbrev_data["team_name_b"]))
        return to_dt

    def dot_main_load_data(self, nfl_year):
        abbrev_dt = self.load_abbrev_table()
        data_tbl = self.load_data_by_year(nfl_year=nfl_year)
        data_tbl.rename(
            columns={"nfl_team": "nfl_team_abbrev", "opp": "opp_name"}, inplace=True
        )

        data_tbl["opp_abbrev"] = data_tbl["opp_name"].map(abbrev_dt)
        data_tbl["nfl_team_name"] = data_tbl["nfl_team_abbrev"].map(abbrev_dt)

        data_tbl["home_team_equals"] = np.where(
            data_tbl["home_away"] == "home",
            data_tbl["nfl_team_abbrev"],
            data_tbl["opp_abbrev"],
        )

        data_tbl["away_team_equals"] = np.where(
            data_tbl["home_away"] == "home",
            data_tbl["opp_abbrev"],
            data_tbl["nfl_team_abbrev"],
        )

        data_tbl["source_data"] = data_tbl["nfl_team_name"]
        data_tbl["winning_team"] = np.where(
            data_tbl["win_loss"] == "W",
            data_tbl["nfl_team_abbrev"],
            data_tbl["opp_abbrev"],
        )

        data_tbl["winning_team_equals_home_team"] = np.where(
            data_tbl["home_team_equals"] == data_tbl["winning_team"], "yes", "no"
        )

        return data_tbl
