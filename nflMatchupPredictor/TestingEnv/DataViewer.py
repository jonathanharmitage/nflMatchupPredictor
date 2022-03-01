#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 11:43:35 2022

@author: willmaethner
"""
import os

from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader

def viewTeams():
    options = ['Teams-to-Abbrev', 'Abbrev-to-Team-List']
    dl = DataLoader()    
    os.system('clear')
    
    while True:
        print('')
        
        for index,opt in enumerate(options):
            print(f'{index+1}. {opt}')
            
        val = input('Selection: ')
        
        if val == '1':
            teams = dl.team_to_abbrev_map()
            for team,abb in teams.items():
                print(f'{team}: {abb}')
        elif val == '2':
            teams = dl.abbrev_to_team_list_map()
            for team,abb in teams.items():
                print(f'{team}: {abb}')
        elif val == 'q':
            break

def main():
    options = ['View Teams']
    os.system('clear')
    
    while True:
        print('')
        
        for index,opt in enumerate(options):
            print(f'{index+1}. {opt}')
            
        val = input('Selection: ')
        
        if val == '1':
            viewTeams()
        elif val == 'q':
            break
    

if __name__ == "__main__":
    main()
