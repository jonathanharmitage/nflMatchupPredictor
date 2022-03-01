#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 14:00:08 2022

@author: willmaethner
"""

import pandas as pd

from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader
from nflMatchupPredictor.Utilities.utilities import *
from nflMatchupPredictor.Scraping.Scraping import Scraping

def main():
    dl = DataLoader()
    util = Utilities()
    scrape = Scraping()
    
    util.__format_filename('test',FileFormat.CSV)
    
    print(dl.load_abbrev_table())
    

    

if __name__ == "__main__":
    main()