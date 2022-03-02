#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 09:51:33 2022

@author: willmaethner
"""

class GeneralDataScraper:
    
    def __init__(self, team_abbrev):
        self.team_abbrev = team_abbrev
        self.team_data_route = "/teams/{}/{}.htm",
        
        
    def get_schedule(self, year):
        pass

    def get_all_teams(self):
        pass