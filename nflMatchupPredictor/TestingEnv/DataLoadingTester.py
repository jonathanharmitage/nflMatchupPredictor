#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 14:00:08 2022

@author: willmaethner
"""

# import pandas as pd

from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader

# from nflMatchupPredictor.Utilities.Utilities import *
# from nflMatchupPredictor.Utilities.Utilities import Utilities
# from nflMatchupPredictor.Scraping.Scraping import Scraping


def main():
    dl = DataLoader()
    # util = Utilities()
    # scrape = Scraping()

    print(dl.abbrev_to_team_list_map())


if __name__ == "__main__":
    main()
