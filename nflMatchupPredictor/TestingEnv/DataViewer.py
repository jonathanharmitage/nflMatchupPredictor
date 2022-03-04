#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 11:43:35 2022

@author: willmaethner
"""
import os

from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader
from nflMatchupPredictor.Scraping.TeamDataScraper import (TeamDataScraper)
from nflMatchupPredictor.Scraping.GeneralDataScraper import (
    GeneralDataScraper)


def display_options(options):
    os.system('clear')
    while True:
        print('')
        mapper = {str(index+1): options[key]
                  for index, key in enumerate(options.keys())}
        for index, opt in enumerate(options.keys()):
            print(f'{index+1}. {opt}')
        val = input('Selection: ')
        if val == 'q':
            break
        elif val in mapper.keys():
            mapper[val]()
        else:
            print('Invalid choice')


def view_teams_to_abbrev():
    dl = DataLoader()
    teams = dl.team_to_abbrev_map()
    for team, abb in teams.items():
        print(f'{team}: {abb}')
    input()


def view_abbrev_to_team_list():
    dl = DataLoader()
    teams = dl.abbrev_to_team_list_map()
    for team, abb in teams.items():
        print(f'{team}: {abb}')
    input()


def view_teams():
    options = {'Teams-to-Abbrev': view_teams_to_abbrev,
               'Abbrev-to-Team-List': view_abbrev_to_team_list}
    display_options(options)


def view_team_data_scraping():
    team_abb = input("Team Abbreviation: ")
    year = input("Year: ")

    tds = TeamDataScraper(team_abb)
    data = tds.get_schedule(year)

    print(data)
    input()


def view_general_schedule():
    year = input("Year: ")
    gds = GeneralDataScraper()
    schedule = gds.get_schedule(year)

    print(schedule)
    input()


def view_general_teams():
    gds = GeneralDataScraper()
    teams = gds.get_all_teams()
    for team, abb in teams.items():
        print(f'{team}: {abb}')
    input()


def view_general_data_scraping():
    options = {"View Schedule": view_general_schedule,
               "View Teams": view_general_teams}

    display_options(options)


def view_data_scraping():
    options = {'Team Data Scraping': view_team_data_scraping,
               'General Data Scraping': view_general_data_scraping}
    display_options(options)


def main():
    options = {'View Teams': view_teams,
               "Data Scraping Functions": view_data_scraping}
    os.system('clear')

    display_options(options)

    return


if __name__ == "__main__":
    main()
