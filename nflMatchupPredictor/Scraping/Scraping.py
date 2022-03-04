import warnings
from collections import Counter

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

# from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader

warnings.simplefilter("ignore")


class Scraping:
    def __init__(self, nfl_year=None, verbose=False):
        self.nfl_year = nfl_year
        self.verbose = verbose

        self.base_url = "https://www.pro-football-reference.com"

    def get_full_url(self, url_key):
        return self.base_url + self.finish_url().get(url_key)

    def finish_url(self):
        dt = {"by_team": "/teams/{}/{}.htm",
              "by_schedule": "/years/{}/games.htm",
              'teams': "/teams/"}

        return dt

    def feature_helper(self):
        feat_dt = {
            "Unnamed: 3_level_1": "game_time",
            "Unnamed: 4_level_1": "boxscore",
            "Unnamed: 5_level_1": "win_loss",
            "Unnamed: 8_level_1": "home_away",
        }
        return feat_dt

    def rename_features(self):
        dt = {
            "expected points_offense": "expected_points_offense",
            "expected points_defense": "expected_points_defense",
            "expected points_sp. tms": "expected_points_special_tms",
        }

        return dt

    def counter_helper(self, data_object):
        cols = ["winner_tie", "loser_tie", "home_team_name"]
        tmp_data_object = data_object.loc[:, cols]
        tmp_data_object.reset_index(drop=True, inplace=True)

        a_team = []
        for i in range(tmp_data_object.shape[0]):
            tmp_counter = Counter(tmp_data_object.iloc[i].tolist())
            for tm, item in tmp_counter.items():
                if item == 1:
                    a_team.append(tm)

        return a_team

    def win_loss_helper(self):
        win_loss_dt = {"W": 1, "L": 0, "T": 0.5, "bye_week": 0}
        return win_loss_dt

    def make_request2(self, url_key, *args):
        url = self.get_full_url(url_key).format(*args)
        return requests.get(url)

    def make_request(self, team_abbr=None):
        """
        Request website

        Parameters
        ----------
        team_abbr : str, optional
            Abbrevation of NFL team, by default None

        Returns
        -------
        HTTP request object
            _description_
        """
        if team_abbr:
            update_url = self.base_url + self.finish_url().get("by_team").format(
                team_abbr, self.nfl_year
            )
        else:
            update_url = self.base_url + self.finish_url().get("by_schedule").format(
                self.nfl_year
            )
        return requests.get(update_url)

    def make_soup2(self, url_key, *args):
        req = self.make_request2(url_key, *args)
        return BeautifulSoup(req.content, "lxml")

    def make_soup(self, team_abbr=None, load_teams=False):
        """
        Instantiate a BeautifulSoup object

        Parameters
        ----------
        team_abbr : str, optional
            Abbrevation of NFL team, by default None

        Returns
        -------
        BeautifulSoup object
            _description_
        """
        req = self.make_request(team_abbr=team_abbr)
        return BeautifulSoup(req.content, "lxml")

    def get_boxscore_url(self, soup_object):
        """
        Parse boxscore link.

        Parameters
        ----------
        soup_object : BeautifulSoup object
            _description_

        Returns
        -------
        list
            _description_
        """
        td_center = soup_object.select("td.center")

        bx = []
        for i in td_center:
            try:
                f_href = i.find("a").get("href")
                bx.append(f_href)
            except AttributeError:
                bx.append("no_data")

        tm_abbrev = []
        for item in bx:
            if item != "no_data":
                len_item = len(item)
                f_item = item[(len_item - 7) :]
                tm_abbrev.append(f_item.split(".")[0])
            else:
                tm_abbrev.append("no_data")

        return tm_abbrev

    def get_schedule(self, soup_object):
        """
        Fetch NFL schedule data.

        Parameters
        ----------
        soup_object : BeautifulSoup object
            _description_

        Returns
        -------
        DataFrame
            _description_

        Notes
        -----
        Move renaming of columns to utility class.
        """
        html_table = soup_object.select("table#games")[0]
        html_to_df = pd.read_html(str(html_table))[0]
        html_to_df = html_to_df.loc[html_to_df["Week"] != "Week"]

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

        html_to_df.rename(columns=rename_dt, inplace=True)

        html_to_df.reset_index(drop=True, inplace=True)

        return html_to_df

    def get_teams(self):
        soup = self.make_soup2('teams')
        table = soup.select("table#teams_active")[0]
        body = table.find('tbody')
        rows = body.find_all('tr')

        teams_abbr = {}
        current_abbr = ''
        for row in rows:
            th_tag = row.find('th')
            classes = row.attrs.get('class')
            if (not classes is None) and ('partial_table' in classes):
                team_name = th_tag.get_text()
            else:
                current_abbr = th_tag.a.get('href').split('/')[-2]
                team_name = th_tag.a.get_text()
            teams_abbr[team_name] = current_abbr
        return teams_abbr

    def get_table(self, soup_object):
        html_table = soup_object.select("table#games")[0]
        html_to_df = pd.read_html(str(html_table))[0]

        # the table has two levels of column names
        #  get the first level and set as the "only" column names for "html_to_df"
        columns_level_zero = html_to_df.columns.get_level_values(0)
        columns_level_one = html_to_df.columns.get_level_values(1)

        join_cols = []
        for i, j in zip(columns_level_zero[10:], columns_level_one[10:]):
            join_cols.append(i + "_" + j)

        upd_cols = columns_level_one[:10].tolist() + join_cols
        html_to_df.columns = upd_cols
        html_to_df.rename(columns=self.feature_helper(), inplace=True)

        html_to_df.columns = [i.lower() for i in html_to_df.columns]

        return html_to_df

    def format_table(self, table_object):

        check_idx = np.argwhere(table_object["date"].values == "Playoffs")
        if len(check_idx) == 0:
            playoffs_idx = table_object.shape[0]
        else:
            playoffs_idx = check_idx[0][0]
            playoffs_tbl = table_object.iloc[playoffs_idx : table_object.shape[0], :]

            playoffs_tbl["offense_to"].fillna(0.0, inplace=True)
            playoffs_tbl["defense_to"].fillna(0.0, inplace=True)
            playoffs_tbl["ot"].fillna(0.0, inplace=True)

            playoffs_tbl["home_away"].fillna("playoffs", inplace=True)
            playoffs_tbl["season_source"] = "playoffs"
            playoffs_tbl.fillna("playoffs", inplace=True)
            playoffs_tbl.reset_index(drop=True, inplace=True)

        regular_season_tbl = table_object.iloc[:playoffs_idx, :]

        bye_week_tbl = regular_season_tbl.loc[regular_season_tbl["opp"] == "Bye Week"]
        bye_week_tbl.fillna("bye_week", inplace=True)
        bye_week_tbl.reset_index(drop=True, inplace=True)

        game_week_tbl = regular_season_tbl.loc[regular_season_tbl["opp"] != "Bye Week"]

        game_week_tbl["offense_to"].fillna(0.0, inplace=True)
        game_week_tbl["defense_to"].fillna(0.0, inplace=True)
        game_week_tbl["ot"].fillna(0.0, inplace=True)

        game_week_tbl["home_away"].fillna("home", inplace=True)
        game_week_tbl["home_away"] = game_week_tbl["home_away"].str.replace("@", "away")
        game_week_tbl.reset_index(drop=True, inplace=True)

        game_week_tbl = pd.concat([game_week_tbl, bye_week_tbl], axis=0)
        game_week_tbl["season_source"] = "regular"

        game_week_tbl["week"] = game_week_tbl["week"].astype(int)
        game_week_tbl.sort_values(["week"], ascending=True, inplace=True)
        game_week_tbl["win_loss_as_int"] = game_week_tbl["win_loss"].map(
            self.win_loss_helper()
        )

        if len(check_idx) > 0:
            game_week_tbl = pd.concat([game_week_tbl, playoffs_tbl], axis=0)

        game_week_tbl.rename(columns=self.rename_features(), inplace=True)
        game_week_tbl.reset_index(drop=True, inplace=True)

        return game_week_tbl

    def scrape_schedule_dot_main(self, team_abbr=None, abbrev_tbl=None):
        """
        Wrapper that encapsulates the necessary logic to fetch a NFL team(s) schedule.

        Parameters
        ----------
        team_abbr : str, optional
            Abbrevation of NFL team, by default None

        Returns
        -------
        DataFrame
            _description_
        """
        soup = self.make_soup(team_abbr=team_abbr)
        get_tm_abbrev = self.get_boxscore_url(soup_object=soup)
        get_schedule_tbl = self.get_schedule(soup_object=soup)

        get_schedule_tbl["home_team"] = get_tm_abbrev
        get_schedule_tbl = get_schedule_tbl.loc[get_schedule_tbl["Date"] != "Playoffs"]

        # abbrev_tbl = DataLoader().load_abbrev_table()

        get_schedule_tbl["winner_abbrev"] = get_schedule_tbl["winner_tie"].map(
            abbrev_tbl
        )
        get_schedule_tbl["loser_abbrev"] = get_schedule_tbl["loser_tie"].map(abbrev_tbl)
        get_schedule_tbl["home_team_name"] = get_schedule_tbl["home_team"].map(
            abbrev_tbl
        )

        get_schedule_tbl["winner_home_away"] = np.where(
            get_schedule_tbl["home_team_name"] == get_schedule_tbl["winner_tie"],
            "home_wins",
            "away_wins",
        )
        get_schedule_tbl["home_team_wins"] = np.where(
            get_schedule_tbl["home_team_name"] == get_schedule_tbl["winner_tie"], 1, 0
        )

        get_schedule_tbl.reset_index(drop=True, inplace=True)

        find_away_team = self.counter_helper(data_object=get_schedule_tbl)
        if len(find_away_team) != len(get_schedule_tbl):
            return get_schedule_tbl, find_away_team
        else:
            get_schedule_tbl["away_team_name"] = find_away_team
            get_schedule_tbl["nfl_season"] = self.nfl_year
            get_schedule_tbl.columns = get_schedule_tbl.columns.str.lower()

            return get_schedule_tbl

    def scrape_dot_main(self, team_abbr):
        """
        Wrapper that encapsulates the necessary logic to fetch a NFL team(s) production data.

        Parameters
        ----------
        team_abbr : str
            Abbrevation of NFL team

        Returns
        -------
        DataFrame
            _description_
        """
        soup = self.make_soup(team_abbr=team_abbr)
        tmp_tbl = self.get_table(soup_object=soup)
        tmp_tbl = self.format_table(table_object=tmp_tbl)
        tmp_tbl["nfl_team"] = team_abbr
        tmp_tbl["nfl_season"] = self.nfl_year

        return tmp_tbl
