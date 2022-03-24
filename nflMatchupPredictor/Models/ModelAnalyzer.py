#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 11:10:24 2022

@author: willmaethner
"""

from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader
from nflMatchupPredictor.Scraping.GeneralDataScraper import GeneralDataScraper


class ModelAnalyzer:
    def __init__(self, model, data_loader):
        dl = DataLoader()
        self.model = model
        self.data_loader = data_loader
        self.team_map = dl.team_to_abbrev_map()

    def analyze(self, train_years, test_years):
        gds = GeneralDataScraper()
        self.data_loader.load_data(train_years + test_years)
        self.model.train(self.data_loader.get_data_by_years(train_years))

        total, correct = 0, 0
        for year in test_years:
            schedule = gds.get_schedule(year)

            for index, row in schedule.iterrows():
                week = row.loc["week"]
                # TODO: Currently skipping post season games
                if not str(week).isnumeric():
                    continue

                winner = row.loc["winner_tie"]
                loser = row.loc["loser_tie"]

                winner_data = self.data_loader.get_teams_stats_by_week(
                    self.team_map[winner], year, int(week))
                loser_data = self.data_loader.get_teams_stats_by_week(
                    self.team_map[loser], year, int(week))

                result = self. model.make_prediction(winner_data, loser_data)

                total += 1
                correct += 1 if result[0] > result[2] else 0

        return correct, total
