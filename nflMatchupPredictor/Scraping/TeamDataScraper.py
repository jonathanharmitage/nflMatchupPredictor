#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 16:01:35 2022

@author: willmaethner
"""

import pandas as pd

from nflMatchupPredictor.Scraping.BaseScraper import BaseScraper


class TeamDataScraper(BaseScraper):
    def __init__(self, team_abbrev):
        BaseScraper.__init__(self)

        self.team_abbrev = team_abbrev
        self.team_data_route = "/teams/{}/{}.htm"

    def feature_helper(self):
        feat_dt = {
            "Unnamed: 3_level_1": "game_time",
            "Unnamed: 4_level_1": "boxscore",
            "Unnamed: 5_level_1": "win_loss",
            "Unnamed: 8_level_1": "home_away",
        }
        return feat_dt

    def get_schedule(self, year):
        soup = super().parse_page(self.team_data_route, self.team_abbrev, year)
        table = super().get_table(soup, "games")
        df = pd.read_html(str(table))[0]

        columns_level_zero = [
            "" if "Unnamed" in x else x for x in df.columns.get_level_values(0)
        ]
        columns_level_one = df.columns.get_level_values(1)

        joined_cols = []
        for i, j in zip(columns_level_zero, columns_level_one):
            joined_cols.append(i + "_" + j)

        df.columns = [x[1:] if x[0] == "_" else x for x in joined_cols]

        df = super().format_data_frame(df, self.feature_helper(), True)

        return df
