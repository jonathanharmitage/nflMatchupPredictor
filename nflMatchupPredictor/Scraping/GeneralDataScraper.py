#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 09:51:33 2022

@author: willmaethner
"""

import pandas as pd

from nflMatchupPredictor.Scraping.BaseScraper import BaseScraper


class GeneralDataScraper(BaseScraper):
    def __init__(self):
        super().__init__()

        self.schedule_route = "/years/{}/games.htm"
        self.teams_route = "/teams/"

    def column_rename(self):
        rename_dt = {
            "PtsW": "pts_winner",
            "PtsL": "pts_loser",
            "YdsW": "yards_winner",
            "YdsL": "yards_loser",
            "TOW": "turnovers_winner",
            "TOL": "turnovers_loser",
            "Winner/tie": "winner_tie",
            "Loser/tie": "loser_tie",
            "Unnamed: 5": "home_away",
            "Unnamed: 7": "boxscore",
        }
        return rename_dt

    def get_schedule(self, year):
        """
        Gets the full yearly schedule and returns it as a DataFrame

        Parameters
        ----------
        year : int
            Year to get the schedule for.

        Returns
        -------
        df : DataFrame
            _description.
        """
        soup = super().parse_page(self.schedule_route, year)
        table = super().get_table(soup, "games")
        df = pd.read_html(str(table))[0]

        df = df.loc[df["Week"] != "Week"]
        df.reset_index(inplace=True, drop=True)

        df = super().format_data_frame(df, rename_columns=self.column_rename(), to_lower=True)

        return df

    def get_all_teams(self):
        """
        Gets all of the active teams and their PFR abbreviations.

        Returns
        -------
        teams_abbr : dict
            Map from the team name to the abbreviation.

        """
        soup = super().parse_page(self.teams_route)
        table = super().get_table(soup, "teams_active")
        body = table.find('tbody')
        rows = body.find_all('tr')

        teams_abbr = {}
        current_abbr = ''
        for row in rows:
            th_tag = row.find('th')
            classes = row.attrs.get('class')
            if (classes is not None) and ('partial_table' in classes):
                team_name = th_tag.get_text()
            else:
                current_abbr = th_tag.a.get('href').split('/')[-2]
                team_name = th_tag.a.get_text()
            teams_abbr[team_name] = current_abbr
        return teams_abbr
