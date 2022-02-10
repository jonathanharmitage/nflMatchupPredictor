from nflMatchupPredictor.Adhoc.Adhoc import Adhoc
from nflMatchupPredictor.Features.Features import Features


class DataBuilds:
    def __init__(self, verbose=False):
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

    def filter_data(self, data_object):
        tmp_regular_season = data_object.loc[data_object["season_source"] != "playoffs"]
        tmp_regular_season["week"] = tmp_regular_season["week"].astype(int)
        return tmp_regular_season

    def determine_home_away_team(self, data_object, team, week_nbr):
        home_away = data_object.loc[
            (data_object["nfl_team"] == team) & (data_object["week"] == week_nbr)
        ]
        if home_away["home_away"].iloc[0] == "home":
            home_team = team
            home_team_abbrev = Adhoc().abbrev_tbl().get(home_team)
            away_team = home_away["opp"].iloc[0]
            away_team_abbrev = Adhoc().abbrev_tbl().get(away_team)
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
            home_team_abbrev = Adhoc().abbrev_tbl().get(home_team)

            away_team = team
            away_team_abbrev = Adhoc().abbrev_tbl().get(away_team)

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

        return final_dt

    def make_home_team_data(self, data_object, week_nbr):
        tmp_data_object = data_object.copy()

        # home_team = home_away_team_dt.get("home_team")
        home_team = self.matchup_dt.get("home_team_abbrev")
        home_tbl = tmp_data_object.loc[
            (tmp_data_object["nfl_team"] == home_team)
            & (tmp_data_object["week"] < week_nbr)
        ]

        return home_tbl

    def make_away_team_data(self, data_object, week_nbr):
        tmp_data_object = data_object.copy()

        # away_team = home_away_team_dt.get("away_team")
        away_team = self.matchup_dt.get("away_team_abbrev")

        away_tbl = tmp_data_object.loc[
            (tmp_data_object["nfl_team"] == away_team)
            & (tmp_data_object["week"] < week_nbr)
        ]

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

        return upd_meta_tbl, upd_prod_tbl

    # def rename_
