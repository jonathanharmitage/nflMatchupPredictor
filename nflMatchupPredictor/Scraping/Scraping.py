import warnings

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

warnings.simplefilter("ignore")


class Scraping:
    def __init__(self, verbose=False):
        self.verbose = verbose

        self.base_url = "https://www.pro-football-reference.com"

    def feature_helper(self):
        feat_dt = {
            "Unnamed: 3_level_1": "game_time",
            "Unnamed: 4_level_1": "boxscore",
            "Unnamed: 5_level_1": "win_loss",
            "Unnamed: 8_level_1": "home_away",
        }
        return feat_dt

    def rename_features(self):
        dt = {
            "expected points_offense": "expected_points_offense",
            "expected points_defense": "expected_points_defense",
            "expected points_sp. tms": "expected_points_special_tms",
        }

        return dt

    def win_loss_helper(self):
        win_loss_dt = {"W": 1, "L": 0, "T": 0.5, "bye_week": 0}
        return win_loss_dt

    def make_request(self, team_abbr, year):
        update_url = self.base_url + f"/teams/{team_abbr}/{year}.htm"
        return requests.get(update_url)

    def make_soup(self, team_abbr, year):
        req = self.make_request(team_abbr=team_abbr, year=year)
        return BeautifulSoup(req.content, "lxml")

    def get_table(self, soup_object):
        html_table = soup_object.select("table#games")[0]
        html_to_df = pd.read_html(str(html_table))[0]

        # the table has two levels of column names
        #  get the first level and set as the "only" column names for "html_to_df"
        columns_level_zero = html_to_df.columns.get_level_values(0)
        columns_level_one = html_to_df.columns.get_level_values(1)

        join_cols = []
        for i, j in zip(columns_level_zero[10:], columns_level_one[10:]):
            join_cols.append(i + "_" + j)

        upd_cols = columns_level_one[:10].tolist() + join_cols
        html_to_df.columns = upd_cols
        html_to_df.rename(columns=self.feature_helper(), inplace=True)

        html_to_df.columns = [i.lower() for i in html_to_df.columns]

        return html_to_df

    def format_table(self, table_object):

        check_idx = np.argwhere(table_object["date"].values == "Playoffs")
        if len(check_idx) == 0:
            playoffs_idx = table_object.shape[0]
        else:
            playoffs_idx = check_idx[0][0]
            playoffs_tbl = table_object.iloc[playoffs_idx : table_object.shape[0], :]

            playoffs_tbl["offense_to"].fillna(0.0, inplace=True)
            playoffs_tbl["defense_to"].fillna(0.0, inplace=True)
            playoffs_tbl["ot"].fillna(0.0, inplace=True)

            playoffs_tbl["home_away"].fillna("playoffs", inplace=True)
            playoffs_tbl["season_source"] = "playoffs"
            playoffs_tbl.fillna("playoffs", inplace=True)
            playoffs_tbl.reset_index(drop=True, inplace=True)

        regular_season_tbl = table_object.iloc[:playoffs_idx, :]

        bye_week_tbl = regular_season_tbl.loc[regular_season_tbl["opp"] == "Bye Week"]
        bye_week_tbl.fillna("bye_week", inplace=True)
        bye_week_tbl.reset_index(drop=True, inplace=True)

        game_week_tbl = regular_season_tbl.loc[regular_season_tbl["opp"] != "Bye Week"]

        game_week_tbl["offense_to"].fillna(0.0, inplace=True)
        game_week_tbl["defense_to"].fillna(0.0, inplace=True)
        game_week_tbl["ot"].fillna(0.0, inplace=True)

        game_week_tbl["home_away"].fillna("home", inplace=True)
        game_week_tbl["home_away"] = game_week_tbl["home_away"].str.replace("@", "away")
        game_week_tbl.reset_index(drop=True, inplace=True)

        game_week_tbl = pd.concat([game_week_tbl, bye_week_tbl], axis=0)
        game_week_tbl["season_source"] = "regular"

        game_week_tbl["week"] = game_week_tbl["week"].astype(int)
        game_week_tbl.sort_values(["week"], ascending=True, inplace=True)
        game_week_tbl["win_loss_as_int"] = game_week_tbl["win_loss"].map(
            self.win_loss_helper()
        )

        if len(check_idx) > 0:
            game_week_tbl = pd.concat([game_week_tbl, playoffs_tbl], axis=0)

        game_week_tbl.rename(columns=self.rename_features(), inplace=True)
        game_week_tbl.reset_index(drop=True, inplace=True)

        return game_week_tbl

    def scrape_dot_main(self, team_abbr, year):
        soup = self.make_soup(team_abbr=team_abbr, year=year)
        tmp_tbl = self.get_table(soup_object=soup)
        tmp_tbl = self.format_table(table_object=tmp_tbl)
        tmp_tbl["nfl_team"] = team_abbr
        tmp_tbl["nfl_season"] = year
        return tmp_tbl
