#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 11:19:26 2022

@author: willmaethner
"""

from scipy.stats import norm
import pandas as pd
import numpy as np

from nflMatchupPredictor.Scraping.GeneralDataScraper import GeneralDataScraper
from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader


class CorrelationDataLoader:
    # TODO: Make base data loader class (interface) for other models to follow. So
    #       analyzer can run on all models
    def __init__(self):
        gds = GeneralDataScraper()
        self.team_abbs = set(gds.get_all_teams().values())
        self.raw = pd.DataFrame()
        self.cumulative = pd.DataFrame()
        self.average = pd.DataFrame()
        self.indexed_average = {}

    def load_data(self, years):
        dl = DataLoader()

        for year in years:
            self.indexed_average[year] = {}
            for abb in self.team_abbs:
                data, cumulative, average = self.load_format_data(dl, abb, year)

                self.raw = pd.concat((self.raw, data))
                self.cumulative = pd.concat((self.cumulative, cumulative))
                self.average = pd.concat((self.average, average))

                self.indexed_average[year][abb] = average

    def columns_to_drop(self):
        return ["week", "day", "date", "game_time", "boxscore", "ot", "rec", "opp",
                "expected points_offense", "expected points_defense",
                "expected points_sp. tms"]

    def get_data_by_years(self, years):
        data = pd.DataFrame()
        for year in years:
            for abb in self.team_abbs:
                data = pd.concat((data, self.indexed_average[year][abb]))
        return data

    def get_teams_stats_by_week(self, team_abb, year, week):
        data = self.indexed_average[year][team_abb]
        return data.loc[week-1]

    def load_format_data(self, dl, team_abb, year):
        data = dl.load_data_by_team_and_year(team_abb, year)

        # Drop rows and columns
        data = data.loc[data["opp"] != "Bye Week"]
        data.drop(columns=self.columns_to_drop(), inplace=True)

        # Format columns to numbers
        data.loc[:, "win_loss"] = data.apply(
            lambda row: 1 if row["win_loss"] == "W" else 0, axis=1)
        data.loc[:, "home_away"] = data.apply(
            lambda row: 0 if row["home_away"] == "@" else 1, axis=1)
        data.fillna(0, inplace=True)

        # Calculate cumulative and cumulative average data
        cumulative = data.cumsum()
        cumulative.loc[:, "home_away"] = data.loc[:, "home_away"]

        average = data.expanding().mean()
        average.loc[:, "home_away"] = data.loc[:, "home_away"]

        return data, cumulative, average


class CorrelationModel:
    # TODO: Make base model class (interface) for other models to follow. So analyzer
    #       can run on all models
    def __init__(self):
        pass

    def train(self, train_data):
        """


        Parameters
        ----------
        train_data : DataFrame
            DataFrame containing game data used for training. Should be in the form:
                Win | Home | Score data | Offense data | Defense data
                -----------------------------------------------------
                - row 1
                - row 2
                - ...
                - row n
        """
        corr = train_data.corr()
        self.win_corr = corr.iloc[0, 1:]
        self.all_scores = [self.calculate_team_score(
            train_data.iloc[i]) for i in range(len(train_data))]
        self.norm = norm(loc=np.mean(self.all_scores), scale=np.std(self.all_scores))

    # TODO: make the return value a class perhaps?
    def make_prediction(self, team_a_data, team_b_data):
        """


        Parameters
        ----------
        team_a_data : Panda.Series
            Averaged data for a team up to the week of the matchup.
        team_b_data : Panda.Series
            Averaged data for a team up to the week of the matchup.

        Returns
        -------
        tuple
            Score for team a, probability for team a,
            Score for team b, probability for team b.

        """
        a_score = self.calculate_team_score(team_a_data)
        b_score = self.calculate_team_score(team_b_data)
        return a_score, self.norm.cdf(a_score), b_score, self.norm.cdf(b_score)

    def calculate_team_score(self, team_data):
        score = 0
        for key, value in self.win_corr.items():
            score += value * team_data[key]
        return score
