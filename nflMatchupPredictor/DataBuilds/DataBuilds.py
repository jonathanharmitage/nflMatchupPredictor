# from nflMatchupPredictor.Adhoc.Adhoc import Adhoc
from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader
from nflMatchupPredictor.Features.Features import Features


class DataBuilds:
    def __init__(self, week_nbr=None, verbose=False):
        self.week_nbr = week_nbr
        self.abbrev_dt = DataLoader().load_abbrev_table()
        self.verbose = verbose

    def home_away_helper(
        self, home_team, home_team_abbrev, away_team, away_team_abbrev
    ):
        if len(home_team) <= 4:
            full_home_team_name = home_team_abbrev
            abbrev_home = home_team

        else:
            full_home_team_name = home_team
            abbrev_home = home_team_abbrev

        if len(away_team) <= 4:
            full_away_team_name = away_team_abbrev
            abbrev_away = away_team
        else:
            full_away_team_name = away_team
            abbrev_away = away_team_abbrev

        dt_ = {
            "home_team": full_home_team_name,
            "home_team_abbrev": abbrev_home,
            "away_team": full_away_team_name,
            "away_team_abbrev": abbrev_away,
        }

        return dt_

    def filter_to_regular(self, data_object):
        tmp_regular_season = data_object.loc[data_object["season_source"] != "playoffs"]
        if tmp_regular_season["week"].dtype == "O":
            tmp_regular_season["week"] = tmp_regular_season["week"].astype(int)

        return tmp_regular_season

    def filter_to_week(self, data_object, is_exact=False):
        # tmp_regular_season = data_object.loc[data_object["season_source"] != "playoffs"]
        # tmp_regular_season["week"] = tmp_regular_season["week"].astype(int)
        tmp_data_object = data_object.copy()
        if "playoffs" in tmp_data_object["season_source"].tolist():
            tmp_data_object = tmp_data_object.loc[
                tmp_data_object["season_source"] != "playoffs"
            ]

        if tmp_data_object["week"].dtype == "O":
            tmp_data_object["week"] = tmp_data_object["week"].astype(int)

        if is_exact:
            tmp_data_object = tmp_data_object.loc[
                tmp_data_object["week"] == self.week_nbr
            ]
        else:
            tmp_data_object = tmp_data_object.loc[
                tmp_data_object["week"] <= self.week_nbr
            ]

        return tmp_data_object

    def dot_filter_main(self, data_object, is_exact=False):
        tmp_regular_season = self.filter_to_regular(data_object=data_object)
        tmp_regular_season = self.filter_to_week(
            data_object=tmp_regular_season, is_exact=is_exact
        )
        return tmp_regular_season

    def determine_home_away_team(self, data_object, team):
        home_away = data_object.loc[
            (data_object["nfl_team"] == team) & (data_object["week"] == self.week_nbr)
        ]
        if home_away["home_away"].iloc[0] == "home":
            home_team = team
            # home_team_abbrev = Adhoc().abbrev_tbl().get(home_team)
            home_team_abbrev = self.abbrev_dt.get(home_team)
            away_team = home_away["opp"].iloc[0]
            # away_team_abbrev = Adhoc().abbrev_tbl().get(away_team)
            away_team_abbrev = self.abbrev_dt.get(away_team)
            result = home_away["win_loss"].iloc[0]

            if result == "W":
                res = team + " is home team and won"
                winner = "home_team"
            else:
                res = team + " is home team and lost"
                winner = "away_team"

            final_dt = self.home_away_helper(
                home_team=home_team,
                home_team_abbrev=home_team_abbrev,
                away_team=away_team,
                away_team_abbrev=away_team_abbrev,
            )

            final_dt["winner"] = winner
            final_dt["result"] = res

        else:
            home_team = home_away["opp"].iloc[0]
            # home_team_abbrev = Adhoc().abbrev_tbl().get(home_team)
            home_team_abbrev = self.abbrev_dt.get(home_team)

            away_team = team
            # away_team_abbrev = Adhoc().abbrev_tbl().get(away_team)
            away_team_abbrev = self.abbrev_dt.get(away_team)

            result = home_away["win_loss"].iloc[0]
            if result == "W":
                res = team + " is away team and won"
                winner = "away_team"

            else:
                res = team + " is away team and lost"
                winner = "home_team"

            final_dt = self.home_away_helper(
                home_team=home_team,
                home_team_abbrev=home_team_abbrev,
                away_team=away_team,
                away_team_abbrev=away_team_abbrev,
            )

            final_dt["winner"] = winner
            final_dt["result"] = res

        # if Adhoc().abbrev_tbl().get(home_team) is not None:
        #     home_team = Adhoc().abbrev_tbl().get(home_team)

        # if Adhoc().abbrev_tbl().get(away_team) is not None:
        #     away_team = Adhoc().abbrev_tbl().get(away_team)

        # home_away_dt = {"home_team": home_team, "away_team": away_team}
        self.matchup_dt = final_dt

        # return final_dt

    def make_home_team_data(self, data_object):
        tmp_data_object = data_object.copy()

        home_team = self.matchup_dt.get("home_team_abbrev")
        home_tbl = tmp_data_object.loc[
            (tmp_data_object["nfl_team"] == home_team)
            & (tmp_data_object["week"] < self.week_nbr)
        ]

        home_tbl.reset_index(drop=True, inplace=True)

        return home_tbl

    def make_away_team_data(self, data_object):
        tmp_data_object = data_object.copy()

        # away_team = home_away_team_dt.get("away_team")
        away_team = self.matchup_dt.get("away_team_abbrev")

        away_tbl = tmp_data_object.loc[
            (tmp_data_object["nfl_team"] == away_team)
            & (tmp_data_object["week"] < self.week_nbr)
        ]
        away_tbl.reset_index(drop=True, inplace=True)

        return away_tbl

    def produce_features(self, team=None):
        tmp_meta_features = Features().meta_features(team=team)
        tmp_production_features = Features().production_features(team=team)
        return tmp_meta_features, tmp_production_features

    def produce_data_matrix(self, data_object):
        nfl_team = data_object["nfl_team"].unique()[0]
        rev_ha_dt = {v: k for k, v in self.matchup_dt.items()}
        lkup_home_away = rev_ha_dt.get(nfl_team)
        suffix = nfl_team + "_is_" + lkup_home_away.replace("_abbrev", "")

        tmp_meta_features, tmp_production_features = self.produce_features(team=suffix)

        tmp_data_object = data_object.copy()
        upd_data_cols = [i + "_" + suffix for i in tmp_data_object.columns]
        tmp_data_object.columns = upd_data_cols

        upd_meta_tbl = tmp_data_object.loc[:, tmp_meta_features]
        upd_prod_tbl = tmp_data_object.loc[:, tmp_production_features]

        for i in upd_prod_tbl.columns.tolist():
            if upd_prod_tbl[i].dtype == "O":
                upd_prod_tbl[i] = upd_prod_tbl[i].astype(float)

        return upd_meta_tbl, upd_prod_tbl

    def produce_data_dot_main(self, data_object, team):
        self.determine_home_away_team(data_object=data_object, team=team)
        home_tbl = self.make_home_team_data(data_object=data_object)
        home_meta_tbl, home_prod_tbl = self.produce_data_matrix(data_object=home_tbl)

        away_tbl = self.make_away_team_data(data_object=data_object)
        away_meta_tbl, away_prod_tbl = self.produce_data_matrix(data_object=away_tbl)

        final_data_dt = {
            "home_meta_tbl": home_meta_tbl,
            "home_prod_tbl": home_prod_tbl,
            "away_meta_tbl": away_meta_tbl,
            "away_prod_tbl": away_prod_tbl,
        }

        return final_data_dt

    # def rename_
