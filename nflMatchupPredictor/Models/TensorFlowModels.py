#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 10:22:26 2022

@author: willmaethner
"""

import pandas as pd
import tensorflow as tf
import numpy as np

from nflMatchupPredictor.Scraping.GeneralDataScraper import GeneralDataScraper
from nflMatchupPredictor.Models.BaseModel import BaseModel, BaseModelDataLoader
from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader


class TensorFlowDataLoader(BaseModelDataLoader):
    def __init__(self):
        gds = GeneralDataScraper()
        self.team_abbs = set(gds.get_all_teams().values())
        self.raw = pd.DataFrame()
        self.cumulative = pd.DataFrame()
        self.average = pd.DataFrame()
        self.indexed_average = {}

    def columns_to_drop(self):
        return [
            "week",
            "day",
            "date",
            "game_time",
            "boxscore",
            "ot",
            "rec",
            "opp",
            "win_loss",
            "home_away",
            "expected points_offense",
            "expected points_defense",
            "expected points_sp. tms",
        ]

    def load_format_data(self, dl, team_abb, year):
        data = dl.load_data_by_team_and_year(team_abb, year)

        # Drop rows and columns
        data = data.loc[data["opp"] != "Bye Week"]
        data.drop(columns=self.columns_to_drop(), inplace=True)

        data.fillna(0, inplace=True)

        cumulative = data.cumsum()
        average = data.expanding().mean()

        return data, cumulative, average

    def get_train_data(self, seasons):
        dl = DataLoader()
        gds = GeneralDataScraper()

        team_map = dl.team_to_abbrev_map()

        data = []
        results = []

        for season in seasons:
            schedule = gds.get_schedule(season)
            for index, row in schedule.iterrows():

                week = row.loc["week"]
                # TODO: Currently skipping post season games
                if not str(week).isnumeric():
                    continue

                home_is_winner = row.loc["home_away"] != "@"
                home_team = (
                    row.loc["winner_tie"] if home_is_winner else row.loc["loser_tie"]
                )
                away_team = (
                    row.loc["loser_tie"] if home_is_winner else row.loc["winner_tie"]
                )

                home_data = self.get_teams_stats_by_week(
                    team_map[home_team], season, int(week)
                )
                away_data = self.get_teams_stats_by_week(
                    team_map[away_team], season, int(week)
                )

                data.append(
                    [home_data.to_numpy().tolist() + away_data.to_numpy().tolist()]
                )
                results.append(0 if home_is_winner else 1)

        return {"data": data, "results": results}


class TensorFlowModel(BaseModel):
    def __init__(self):
        super().__init__()

    def train(self, train_data):
        """


        Parameters
        ----------
        train_data : dict
            Dictionary containing two arrays under the keys 'data' and 'results'.

            The 'data' node should include the normal game data points (scores, offense,
            defense, etc) in the order of home team then away team.

            The 'results' node should be an array of 0 for a home team win and 1 for
            an away team win.

        Returns
        -------
        None.

        """
        self.model = tf.keras.models.Sequential(
            [
                tf.keras.layers.Flatten(input_shape=(1, 24)),
                tf.keras.layers.Dense(64, activation="relu"),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(2),
            ]
        )

        self.model.compile(
            optimizer="adam",
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=["accuracy"],
        )

        self.model.fit(
            train_data["data"], train_data["results"], epochs=50, verbose=False
        )
        self.probability_model = tf.keras.Sequential(
            [self.model, tf.keras.layers.Softmax()]
        )

    def make_prediction(self, home_data, away_data):
        data = home_data.tolist() + away_data.tolist()
        data_exp = np.expand_dims([data], 0)
        result = self.probability_model.predict(np.array(data_exp))[0]

        return np.argmax(result), (result[0], result[1])
