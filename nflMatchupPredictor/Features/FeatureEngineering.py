import numpy as np


class FeatureEngineering:
    def __init__(self, verbose=False):
        self.verbose = verbose

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

        def make_turnover_diff(self, data_object):
            tmp_data_object = data_object.copy()

            tmp_data_object["turnover_diff_home_team"] = (
                tmp_data_object["offense_to_home_team"] - tmp_data_object["defense_to_home_team"]
            )

            tmp_data_object["turnover_diff_binary_home_team"] = np.where(tmp_data_object["turnover_diff_home_team"] <= 0, 1, 0)

            tmp_data_object["turnover_diff_away_team"] = (
                tmp_data_object["offense_to_away_team"] - tmp_data_object["defense_to_away_team"]
            )

            tmp_data_object["turnover_diff_binary_away_team"] = np.where(tmp_data_object["turnover_diff_away_team"] <= 0, 1, 0)

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
