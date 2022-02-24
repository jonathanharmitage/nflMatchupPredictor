import numpy as np


class Features:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def rename_features(self):
        dt = {"expected points_sp. tms": "expected points_sp_tms"}

        return dt

    def meta_features(self):
        # meta_features = [
        #     "nfl_team",
        #     "nfl_team_abbrev",
        #     "nfl_team_name",
        #     "nfl_season",
        #     "season_source",
        #     "week",
        #     "day",
        #     "date",
        #     "game_time",
        #     "boxscore",
        #     "score_tm",
        #     "score_opp",
        #     "win_loss",
        #     "win_loss_as_int",
        #     "ot",
        #     "rec",
        #     "home_away",
        #     "opp",
        #     "opp_name",
        #     "opp_abbrev",
        #     "winning_team",
        #     "winning_team_equals_home_team",
        #     "expected_points_offense",
        #     "expected_points_defense",
        #     "expected_points_special_tms",
        # ]

        meta_features = [
            "week",
            "predicting_for_week",
            "data_through_week_home",
            "home_team_name",
            "home_team_abbrev",
            "away_team_name",
            "away_team_abbrev",
            "home_team_wins",
            "agg_type",
        ]

        # fmt: off
        remove_features = [
            "away_team_name_abbrev",
            "data_through_week_away",
            "home_team_name_abbrev"
        ]

        # if (team is not None) and (type(team) is str):
        #     meta_features = [i + "_" + team for i in meta_features]

        return meta_features, remove_features

    def arrange_features(self, data_object):
        meta_features, remove_features = self.meta_features()
        keep_feats_one = [i for i in data_object if i not in meta_features + remove_features]
        return meta_features + keep_feats_one

    def production_features(self, team=None):
        production_features = [
            "offense_1std",
            "offense_totyd",
            "offense_passy",
            "offense_rushy",
            "offense_to",
            "defense_1std",
            "defense_totyd",
            "defense_passy",
            "defense_rushy",
            "defense_to",
        ]

        if (team is not None) and (type(team) is str):
            production_features = [i + "_" + team for i in production_features]

        return production_features

    def make_score_diff(self, data_object):
        tmp_data_object = data_object.copy()

        tmp_data_object["score_diff_home_team"] = (
            tmp_data_object["score_tm_home_team"] - tmp_data_object["score_opp_home_team"]
        )

        tmp_data_object["score_rel_diff_home_team"] = (
            tmp_data_object["score_tm_home_team"] / tmp_data_object["score_opp_home_team"]
        )

        # fmt: off
        tmp_data_object["scored_more_than_opp_home_team"] = (
            np.where(tmp_data_object["score_diff_home_team"] >= 0, 1, 0)
        )

        tmp_data_object["score_diff_away_team"] = (
            tmp_data_object["score_tm_away_team"] - tmp_data_object["score_opp_away_team"]
        )

        tmp_data_object["score_rel_diff_away_team"] = (
            tmp_data_object["score_tm_away_team"] / tmp_data_object["score_opp_away_team"]
        )
        # fmt: off
        tmp_data_object["scored_more_than_opp_away_team"] = (
            np.where(tmp_data_object["score_diff_away_team"] >= 0, 1, 0)
        )

        tmp_data_object["score_rel_diff_home_team_vs_away_team"] = (
            tmp_data_object["score_rel_diff_home_team"] / tmp_data_object["score_rel_diff_away_team"]
        )

        return tmp_data_object

    # def make_turnover_diff(self, data_object):
    #     tmp_data_object = data_object.copy()

    #     tmp_data_object["turnover_diff_home_team"] = (
    #         tmp_data_object["offense_to_home_team"] - tmp_data_object["defense_to_home_team"]
    #     )

    #     tmp_data_object["turnover_diff_binary_home_team"] = (
    #         np.where(tmp_data_object["turnover_diff_home_team"] <= 0, 1, 0)
    #     )

    #     tmp_data_object["turnover_diff_away_team"] = (
    #         tmp_data_object["offense_to_away_team"] - tmp_data_object["defense_to_away_team"]
    #     )

    #     tmp_data_object["turnover_diff_binary_away_team"] = (
    #         np.where(tmp_data_object["turnover_diff_away_team"] <= 0, 1, 0)
    #     )

    #     return tmp_data_object

    def make_turnover_diff(self, data_object):
        tmp_data_object = data_object.copy()

        tmp_data_object["turnover_diff_home_team"] = (
            tmp_data_object["offense_to_home_team"]
            - tmp_data_object["defense_to_home_team"]
        )

        tmp_data_object["turnover_diff_binary_home_team"] = np.where(
            tmp_data_object["turnover_diff_home_team"] <= 0, 1, 0
        )

        tmp_data_object["turnover_diff_away_team"] = (
            tmp_data_object["offense_to_away_team"]
            - tmp_data_object["defense_to_away_team"]
        )

        tmp_data_object["turnover_diff_binary_away_team"] = np.where(
            tmp_data_object["turnover_diff_away_team"] <= 0, 1, 0
        )

        return tmp_data_object

    def make_yards_diff(self, data_object):
        tmp_data_object = data_object.copy()

        tmp_data_object["offense_totyd_diff_home_vs_away"] = (
            tmp_data_object["offense_totyd_home_team"] - tmp_data_object["offense_totyd_away_team"]
        )

        tmp_data_object["defense_totyd_diff_home_vs_away"] = (
            tmp_data_object["defense_totyd_home_team"] - tmp_data_object["defense_totyd_away_team"]
        )

        return tmp_data_object

    def features_dot_main(self, data_object):
        tmp_data_object = self.make_score_diff(data_object=data_object)
        tmp_data_object = self.make_turnover_diff(data_object=tmp_data_object)
        tmp_data_object = self.make_yards_diff(data_object=tmp_data_object)
        return tmp_data_object
