#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 10:36:08 2022

@author: willmaethner
"""

import pandas as pd


from Scraping.GeneralDataScraper import GeneralDataScraper
from DataLoaders.DataLoader import DataLoader


class BaseModelDataLoader:
    def __init__(self):
        gds = GeneralDataScraper()
        self.team_abbs = set(gds.get_all_teams().values())
        self.raw = pd.DataFrame()
        self.cumulative = pd.DataFrame()
        self.average = pd.DataFrame()
        self.indexed_average = {}

    def load_data(self, seasons):
        dl = DataLoader()

        for year in seasons:
            self.indexed_average[year] = {}
            for abb in self.team_abbs:
                data, cumulative, average = self.load_format_data(dl, abb, year)

                self.raw = pd.concat((self.raw, data))
                self.cumulative = pd.concat((self.cumulative, cumulative))
                self.average = pd.concat((self.average, average))

                self.indexed_average[year][abb] = average

    def get_train_data(self, seasons):
        raise NotImplementedError

    def get_prediction_data(self, game_series, season):
        dl = DataLoader()
        team_map = dl.team_to_abbrev_map()

        week = game_series.loc["week"]
        home_is_winner = game_series.loc["home_away"] == "@"
        home_team = (
            game_series.loc["winner_tie"]
            if home_is_winner
            else game_series.loc["loser_tie"]
        )
        away_team = (
            game_series.loc["loser_tie"]
            if home_is_winner
            else game_series.loc["winner_tie"]
        )

        home_data = self.get_teams_stats_by_week(team_map[home_team], season, int(week))
        away_data = self.get_teams_stats_by_week(team_map[away_team], season, int(week))

        return home_data, away_data, 0 if home_is_winner else 1

    def load_format_data(self, dl, team_abb, year):
        raise NotImplementedError

    def get_teams_stats_by_week(self, team_abb, year, week):
        data = self.indexed_average[year][team_abb]
        return data.loc[week - 1]


class BaseModel:
    def __init__(self):
        pass

    def train(self, train_data):
        raise NotImplementedError

    def make_prediction(self, home_data, away_data):
        raise NotImplementedError
