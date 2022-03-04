#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 16:25:15 2022

@author: willmaethner
"""

import requests

from pandas import DataFrame
from bs4 import BeautifulSoup


class BaseScraper:
    def __init__(self):
        self.base_url = "https://www.pro-football-reference.com"

    def parse_page(self, url_route, *args):
        response = requests.get(self.__full_url(url_route, *args))
        return BeautifulSoup(response.content, "lxml")

    def get_table(self, soup_object, table_name):
        return soup_object.select(f"table#{table_name}")[0]

    def format_data_frame(self,
                          df: DataFrame,
                          rename_columns=None,
                          to_lower=False):

        if rename_columns is not None:
            df.rename(columns=rename_columns, inplace=True)

        if to_lower:
            df.columns = [x.lower() for x in df.columns]

        return df

    def __full_url(self, url_route, *args):
        formatted_route = url_route.format(*args)
        return f"{self.base_url}/{formatted_route}"
