#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 11:43:35 2022

@author: willmaethner
"""
import os

from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader

def display_options(options):
    os.system('clear')
    
    while True:
        print('')
        
        mapper = {str(index+1):options[key] for index,key in enumerate(options.keys())}
        for index,opt in enumerate(options.keys()):
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
    for team,abb in teams.items():
        print(f'{team}: {abb}')
    input()
    
def view_abbrev_to_team_list():
    dl = DataLoader() 
    teams = dl.abbrev_to_team_list_map()
    for team,abb in teams.items():
        print(f'{team}: {abb}')
    input()

def view_teams():
    options = {'Teams-to-Abbrev': view_teams_to_abbrev, 
               'Abbrev-to-Team-List': view_abbrev_to_team_list}
    
    display_options(options)
    
    return

def main():
    options = {'View Teams': view_teams}
    os.system('clear')
    
    display_options(options)
    
    return
   

if __name__ == "__main__":
    main()
