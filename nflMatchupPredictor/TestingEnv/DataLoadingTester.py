#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 14:00:08 2022

@author: willmaethner
"""

import pandas as pd

# from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader
# from nflMatchupPredictor.Utilities.Utilities import *
# from nflMatchupPredictor.Scraping.Scraping import Scraping
# from nflMatchupPredictor.Scraping.BaseScraper import BaseScraper
# from nflMatchupPredictor.Scraping.TeamDataScraper import TeamDataScraper
# from nflMatchupPredictor.Scraping.GeneralDataScraper import GeneralDataScraper
from nflMatchupPredictor.Models.CorrelationModels import (
    CorrelationDataLoader,
    CorrelationModel,
)
from nflMatchupPredictor.Models.ModelAnalyzer import ModelAnalyzer


def main():
    pd.set_option("display.max_columns", None)
    # dl = DataLoader()
    # util = Utilities()
    # scrape = Scraping()
    # tds = TeamDataScraper('crd')
    # gds = GeneralDataScraper()

    cdl = CorrelationDataLoader()
    cm = CorrelationModel()

    ma = ModelAnalyzer(cm, cdl)
    result = ma.analyze([2019, 2020], [2021])

    print(f"{result} = {result[0]/result[1]}")
    return


if __name__ == "__main__":
    main()
