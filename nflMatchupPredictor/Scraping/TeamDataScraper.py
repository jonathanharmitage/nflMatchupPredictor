#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 16:01:35 2022

@author: willmaethner
"""

import pandas as pd

from nflMatchupPredictor.Scraping.BaseScraper import BaseScraper
from nflMatchupPredictor.Scraping.Scraping import Scraping


class TeamDataScraper(BaseScraper):
    
    def __init__(self, team_abbrev):
        BaseScraper.__init__(self)
        
        self.team_abbrev = team_abbrev
        self.team_data_route = '/teams/{}/{}.htm'
        
    def feature_helper(self):
        feat_dt = {
            "Unnamed: 3_level_1": "game_time",
            "Unnamed: 4_level_1": "boxscore",
            "Unnamed: 5_level_1": "win_loss",
            "Unnamed: 8_level_1": "home_away",
        }
        return feat_dt
    def get_schedule(self, year):
        soup = self.parse_page(self.team_data_route, self.team_abbrev, year)
        table = self.get_table(soup, 'games')
        df = pd.read_html(str(table))[0]
        
        sc = Scraping()
        print(sc.get_table(soup))
        
        
        # print(df)

    def get_season_stats(self, year):
        pass