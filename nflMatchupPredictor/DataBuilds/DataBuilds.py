# from nflMatchupPredictor.Adhoc.Adhoc import Adhoc
import warnings

import pandas as pd

from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader
from nflMatchupPredictor.Features.Features import Features

warnings.simplefilter("ignore")


class DataBuilds:
    def __init__(self, week_nbr=None, verbose=False):
        self.week_nbr = week_nbr
        self.abbrev_dt = DataLoader().load_abbrev_table()
        self.verbose = verbose

    def filter_to_regular(self, data_object):
        """
        Filter data to include only games that occurred in the regular season.

        Parameters
        ----------
        data_object : DataFrame
            Raw NFL game data

        Returns
        -------
        DataFrame
            NFL game data filtered to include only games that occurred in the regular season
        """
        tmp_regular_season = data_object.loc[data_object["season_source"] != "playoffs"]
        tmp_regular_season = tmp_regular_season.loc[tmp_regular_season["score_tm"] != "bye_week"]

        if tmp_regular_season["week"].dtype == "O":
            tmp_regular_season["week"] = tmp_regular_season["week"].astype(int)

        all_prod_ = self.features_need().get("all_prod")
        for i in all_prod_:
            if tmp_regular_season[i].dtype == "O":
                tmp_regular_season[i] = tmp_regular_season[i].astype(float)

        return tmp_regular_season

    def truncate_schedule(self, data_schedule):
        """
        Trim NFL schedule data to include relevant columns.

        Parameters
        ----------
        data_schedule : DataFrame
            Raw NFL schedule data

        Returns
        -------
        DataFrame
            NFL schedule data truncated to include only relevant columns.

        """
        cols = ["week", "home_team_name", "away_team_name", "home_team_wins"]
        tmp_schedule = data_schedule.loc[:, cols]
        tmp_schedule["home_team_abbrev"] = tmp_schedule["home_team_name"].map(self.abbrev_dt)
        tmp_schedule["away_team_abbrev"] = tmp_schedule["away_team_name"].map(self.abbrev_dt)

        return tmp_schedule

    def features_need(self):
        """
        Relevant features to be utilized for downstream tasks.

        Returns
        -------
        dict
        """
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

        diffs_ = [
            "score_diff_home_team",
            "scored_more_than_opp_home_team",
            "score_diff_away_team",
            "scored_more_than_opp_away_team",
            "turnover_diff_home_team",
            "turnover_diff_binary_home_team",
            "turnover_diff_away_team",
            "turnover_diff_binary_away_team",
            "offense_totyd_diff_home_vs_away",
            "defense_totyd_diff_home_vs_away",
        ]

        dt = {
            "all_need": meta_ + score_ + offense_ + defense_,
            "all_prod": score_ + offense_ + defense_,
            "diff_prod": diffs_,
        }

        return dt

    def filter_and_truncate(self, data_schedule, data_production):
        """
        Wrapper that first filters relevant NFL production data and then
        truncates NFL schedule data.

        Parameters
        ----------
        data_schedule : DataFrame
            _description_
        data_production : DataFrame
            _description_

        Returns
        -------
        DataFrame
            NFL game data filtered to include only games that occurred in the regular season

        DataFrame
            NFL schedule data truncated to include only relevant columns.
        """
        prod_regular = self.filter_to_regular(data_object=data_production)
        trunc_schedule = self.truncate_schedule(data_schedule=data_schedule)

        return prod_regular, trunc_schedule

    def design_matrix_by_week(self, data_schedule, data_production, week, mean_prod=False):
        """
        Generate a design matrix that can be partitioned into train and test sets.

        Parameters
        ----------
        data_schedule : DataFrame
            _description_
        data_production : DataFrame
            _description_
        week : int
            Represents the week of the NFL season that predictions are to be made.
        mean_prod : bool, optional
            If True production metrics are aggregated by taking the mean, else aggregation is accomplished via summing over all relevant values, by default False.

        Returns
        -------
        DataFrame
            Dataset where all production metrics are aggregated up to (but not including) `week`

        Todo
        ----
        Better naming
        """
        # tmp_schedule = data_schedule.copy()
        tmp_schedule = data_schedule.loc[data_schedule["week"] == str(week)]
        tmp_schedule.reset_index(drop=True, inplace=True)
        # week3_upd == data_schedule
        tmp_prod = data_production.copy()
        # s2020 == data_prod

        all_need_ = self.features_need().get("all_need")
        all_prod_ = self.features_need().get("all_prod")

        hld_df = pd.DataFrame()
        for i in range(tmp_schedule.shape[0]):
            h_ = tmp_schedule["home_team_abbrev"].iloc[i]
            a_ = tmp_schedule["away_team_abbrev"].iloc[i]

            h_w1w2 = tmp_prod.loc[(tmp_prod["nfl_team"] == h_) & (tmp_prod["week"] < week), all_need_]
            a_w1w2 = tmp_prod.loc[(tmp_prod["nfl_team"] == a_) & (tmp_prod["week"] < week), all_need_]

            # Home team data
            if mean_prod:
                h_agg_w1w2 = pd.DataFrame(h_w1w2[all_prod_].mean()).T
                agg_type = "mean"
            else:
                h_agg_w1w2 = pd.DataFrame(h_w1w2[all_prod_].sum()).T
                agg_type = "sum"

            h_agg_w1w2.columns = [c + "_home_team" for c in h_agg_w1w2]
            h_agg_w1w2["home_team_name_abbrev"] = h_
            h_agg_w1w2["data_through_week_home"] = "through_week_" + str(week - 1)

            # Away team data
            if mean_prod:
                a_agg_w1w2 = pd.DataFrame(a_w1w2[all_prod_].mean()).T
                agg_type = "mean"
            else:
                a_agg_w1w2 = pd.DataFrame(a_w1w2[all_prod_].sum()).T
                agg_type = "sum"

            a_agg_w1w2.columns = [c + "_away_team" for c in a_agg_w1w2]
            a_agg_w1w2["away_team_name_abbrev"] = a_
            a_agg_w1w2["data_through_week_away"] = "through_week_" + str(week - 1)

            h_vs_a_w3 = pd.concat([h_agg_w1w2, a_agg_w1w2], axis=1)

            w_upd = tmp_schedule.iloc[i : i + 1, :]
            w_upd.reset_index(drop=True, inplace=True)

            final_h_vs_a_w3 = pd.concat([w_upd, h_vs_a_w3], axis=1)
            final_h_vs_a_w3["predicting_for_week"] = "predicting_for_week_" + str(week)
            final_h_vs_a_w3["agg_type"] = agg_type

            hld_df = hld_df.append(final_h_vs_a_w3)

        return hld_df

    def design_dot_main(self, data_schedule, data_production, week, mean_prod=False):
        """
        Wrapper that encapsulates the necessary logic to generate one week of NFL data that is temporally correct.

        Parameters
        ----------
        data_schedule : DataFrame
            _description_
        data_production : DataFrame
            _description_
        week : _type_
            _description_
        mean_prod : bool, optional
            _description_, by default False

        Returns
        -------
        DataFrame
            _description_
        """
        design_matrix = self.design_matrix_by_week(
            data_schedule=data_schedule,
            data_production=data_production,
            week=week,
            mean_prod=mean_prod,
        )

        design_matrix = Features().features_dot_main(data_object=design_matrix)

        return design_matrix

    def design_train_iter_dot_main(self, data_schedule, data_production, min_week=2, max_week=None, mean_prod=False):
        """
        Wrapper that encapsulates the neccessary method(s) to generate many weeks of training data

        Parameters
        ----------
        data_schedule : DataFrame
            _description_
        data_production : DataFrame
            _description_
        min_week : int, optional
            _description_, by default 2
        max_week : _type_, optional
            _description_, by default None
        mean_prod : bool, optional
            _description_, by default False

        Returns
        -------
        DataFrame
            _description_
        """
        if max_week is None:
            max_weeks = data_production["week"].max()
            iter_range = range(min_week, max_weeks + 1)
        elif (type(max_week) is int) and (max_week > 17):
            iter_range = range(min_week, (17 + 1))
        elif type(max_week) is int:
            iter_range = range(min_week, max_week + 1)

        print(f"\n-- Training data for {list(iter_range)[-1] - 1} weeks --\n")

        hld_df = pd.DataFrame()
        for w in iter_range:
            tmp_design = self.design_dot_main(
                data_schedule=data_schedule,
                data_production=data_production,
                week=w,
                mean_prod=mean_prod,
            )
            hld_df = hld_df.append(tmp_design)

            if self.verbose:
                print(f"\n-- Week Complete: {w} --\n")

        return hld_df
