#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 14:00:08 2022

@author: willmaethner
"""

# import pandas as pd

from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader
from nflMatchupPredictor.Utilities.utilities import *
from nflMatchupPredictor.Scraping.Scraping import (Scraping)
from nflMatchupPredictor.Scraping.BaseScraper import (BaseScraper)
from nflMatchupPredictor.Scraping.TeamDataScraper import (TeamDataScraper)

def main():
    pd.set_option('display.max_columns', None)
    dl = DataLoader()
    util = Utilities()
    scrape = Scraping()
    tds = TeamDataScraper('crd')

    tds.get_schedule(2021)

    # print(dl.abbrev_to_team_list_map())



if __name__ == "__main__":
    main()
