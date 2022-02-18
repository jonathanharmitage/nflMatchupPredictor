# from nflMatchupPredictor.Adhoc.Adhoc import Adhoc
import pandas as pd

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
        tmp_regular_season = tmp_regular_season.loc[
            tmp_regular_season["score_tm"] != "bye_week"
        ]

        if tmp_regular_season["week"].dtype == "O":
            tmp_regular_season["week"] = tmp_regular_season["week"].astype(int)

        all_prod_ = self.features_need().get("all_prod")
        for i in all_prod_:
            if tmp_regular_season[i].dtype == "O":
                tmp_regular_season[i] = tmp_regular_season[i].astype(float)

        return tmp_regular_season

    def truncate_schedule(self, data_schedule):
        cols = ["week", "home_team_name", "away_team_name", "home_team_wins"]
        tmp_schedule = data_schedule.loc[:, cols]
        tmp_schedule["home_team_abbrev"] = tmp_schedule["home_team_name"].map(
            self.abbrev_dt
        )
        tmp_schedule["away_team_abbrev"] = tmp_schedule["away_team_name"].map(
            self.abbrev_dt
        )

        return tmp_schedule

    def features_need(self):
        meta_ = ["nfl_season", "week", "nfl_team"]
        score_ = ["score_tm", "score_opp"]
        offense_ = [
            "offense_1std",
            "offense_totyd",
            "offense_passy",
            "offense_rushy",
            "offense_to",
        ]
        defense_ = [
            "defense_1std",
            "defense_totyd",
            "defense_passy",
            "defense_rushy",
            "defense_to",
        ]

        dt = {
            "all_need": meta_ + score_ + offense_ + defense_,
            "all_prod": score_ + offense_ + defense_,
        }

        return dt

    def design_matrix_by_week(self, data_schedule, data_prod, week):
        tmp_schedule = data_schedule.copy()
        # week3_upd == data_schedule
        tmp_prod = data_prod.copy()
        # s2020 == data_prod

        all_need_ = self.features_need().get("all_need")
        all_prod_ = self.features_need().get("all_prod")

        hld_df = pd.DataFrame()
        for i in range(tmp_schedule.shape[0]):
            h_ = tmp_schedule["home_team_abbrev"].iloc[i]
            a_ = tmp_schedule["away_team_abbrev"].iloc[i]

            h_w1w2 = tmp_prod.loc[
                (tmp_prod["nfl_team"] == h_) & (tmp_prod["week"] < week), all_need_
            ]
            a_w1w2 = tmp_prod.loc[
                (tmp_prod["nfl_team"] == a_) & (tmp_prod["week"] < week), all_need_
            ]

            # Home team data
            h_agg_w1w2 = pd.DataFrame(h_w1w2[all_prod_].sum()).T
            h_agg_w1w2.columns = [c + "_home_team" for c in h_agg_w1w2]
            h_agg_w1w2["home_team_name_abbrev"] = h_
            h_agg_w1w2["through_week"] = "through_week_" + str(week - 1)

            # Away team data
            a_agg_w1w2 = pd.DataFrame(a_w1w2[all_prod_].sum()).T
            a_agg_w1w2.columns = [c + "_away_team" for c in a_agg_w1w2]
            a_agg_w1w2["away_team_name_abbrev"] = a_
            a_agg_w1w2["through_week"] = "through_week_" + str(week - 1)

            h_vs_a_w3 = pd.concat([h_agg_w1w2, a_agg_w1w2], axis=1)

            w_upd = tmp_schedule.iloc[i : i + 1, :]
            w_upd.reset_index(drop=True, inplace=True)

            final_h_vs_a_w3 = pd.concat([w_upd, h_vs_a_w3], axis=1)
            hld_df = hld_df.append(final_h_vs_a_w3)

        return hld_df

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
