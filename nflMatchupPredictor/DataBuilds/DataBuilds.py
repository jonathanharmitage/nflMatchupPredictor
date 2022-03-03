import warnings

import pandas as pd

from nflMatchupPredictor.Utilities.Utilities import Utilities
from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader


warnings.simplefilter("ignore")


class DataBuilds:
    def __init__(self, verbose=False):
        self.abbrev_dt = DataLoader().team_to_abbrev_map()
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
            NFL game data filtered to include only games that occurred in the
            regular season
        """
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
        tmp_schedule["home_team_abbrev"] = tmp_schedule["home_team_name"].map(
            self.abbrev_dt
        )
        tmp_schedule["away_team_abbrev"] = tmp_schedule["away_team_name"].map(
            self.abbrev_dt
        )

        return tmp_schedule

    def features_need(self):
        """
        Relevant features to be utilized for downstream tasks.

        Returns
        -------
        dict

        Notes
        -----
        Move to `Features` or `Utilities` class?
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
            Raw NFL schedule data
        data_production : DataFrame
            Raw NFL game data

        Returns
        -------
        DataFrame
            NFL game data filtered to include only games that occurred in the
            regular season

        DataFrame
            NFL schedule data truncated to include only relevant columns.
        """
        trunc_schedule = self.truncate_schedule(data_schedule=data_schedule)
        prod_regular = self.filter_to_regular(data_object=data_production)

        return trunc_schedule, prod_regular

    def design_matrix_by_week(
        self, data_schedule, data_production, week, mean_prod=False
    ):
        """
        Generate a design matrix that can be partitioned into train and test sets.

        Parameters
        ----------
        data_schedule : DataFrame
            Raw NFL schedule data
        data_production : DataFrame
            Raw NFL game data
        week : int
            Represents the week of the NFL season that predictions are to be made.
        mean_prod : bool, optional
            If True production metrics are aggregated by taking the mean, else aggregation
            is accomplished via summing over all relevant values, by default False.

        Returns
        -------
        DataFrame
            Dataset where all production metrics are aggregated up to (but not including) `week`

        Todo / Thoughts / Questions
        ---------------------------
        Add additional features here or later?
        """
        tmp_schedule = data_schedule.loc[data_schedule["week"] == str(week)]
        tmp_schedule.reset_index(drop=True, inplace=True)
        tmp_production = data_production.copy()

        all_need_ = Utilities().features_need().get("all_need")
        all_prod_ = Utilities().features_need().get("all_prod")

        hld_df = pd.DataFrame()
        for i in range(tmp_schedule.shape[0]):
            home_tm_abbrev = tmp_schedule["home_team_abbrev"].iloc[i]
            away_tm_abbrev = tmp_schedule["away_team_abbrev"].iloc[i]

            tmp_home = tmp_production.loc[
                (tmp_production["nfl_team"] == home_tm_abbrev)
                & (tmp_production["week"] < week),
                all_need_,
            ]
            tmp_away = tmp_production.loc[
                (tmp_production["nfl_team"] == away_tm_abbrev)
                & (tmp_production["week"] < week),
                all_need_,
            ]

            # Home team data
            if mean_prod:
                tmp_home_agg_prod = pd.DataFrame(tmp_home[all_prod_].mean()).T
                agg_type = "mean"
            else:
                tmp_home_agg_prod = pd.DataFrame(tmp_home[all_prod_].sum()).T
                agg_type = "sum"

            tmp_home_agg_prod.columns = [c + "_home_team" for c in tmp_home_agg_prod]
            tmp_home_agg_prod["home_team_name_abbrev"] = home_tm_abbrev
            tmp_home_agg_prod["data_through_week_home"] = "through_week_" + str(week - 1)

            # Away team data
            if mean_prod:
                tmp_away_agg_prod = pd.DataFrame(tmp_away[all_prod_].mean()).T
                agg_type = "mean"
            else:
                tmp_away_agg_prod = pd.DataFrame(tmp_away[all_prod_].sum()).T
                agg_type = "sum"

            tmp_away_agg_prod.columns = [c + "_away_team" for c in tmp_away_agg_prod]
            tmp_away_agg_prod["away_team_name_abbrev"] = away_tm_abbrev
            tmp_away_agg_prod["data_through_week_away"] = "through_week_" + str(week - 1)

            tmp_home_vs_tmp_away_w3 = pd.concat(
                [tmp_home_agg_prod, tmp_away_agg_prod], axis=1
            )

            tmp_week_upd = tmp_schedule.iloc[i : i + 1, :]
            tmp_week_upd.reset_index(drop=True, inplace=True)

            final_home_vs_away = pd.concat(
                [tmp_week_upd, tmp_home_vs_tmp_away_w3], axis=1
            )
            final_home_vs_away["predicting_for_week"] = "predicting_for_week_" + str(
                week
            )
            final_home_vs_away["agg_type"] = agg_type

            hld_df = hld_df.append(final_home_vs_away)

        # Add features?
        # hld_df = Features().features_dot_main(data_object=hld_df)

        return hld_df

    def design_iter_dot_main(
        self, data_schedule, data_production, min_week=2, max_week=None, mean_prod=False
    ):
        """
        Wrapper that encapsulates the neccessary method(s) to generate many weeks of training data.

        Parameters
        ----------
        data_schedule : DataFrame
            Raw NFL schedule data
        data_production : DataFrame
            Raw NFL game data
        min_week : int, optional
            Minimum regular season week to being to build training data, by default 2
        max_week : int, optional
            Maximum week to be included in the training dataset, by default None
        mean_prod : bool, optional
            If True production metrics are aggregated by taking the mean, else aggregation is
            accomplished via summing over all relevant values, by default False

        Returns
        -------
        DataFrame
            Dataset containing NFL matchups with production metrics mapped temporally.

        Example
        -------
        >>> trunc_schedule2020, production_regular2020 = dataBuildCls.filter_and_truncate(
        ...     data_schedule=schedule2020,
        ...     data_production=prod2020
        ... )

        >>> train2020 = dataBuildCls.design_iter_dot_main(
        ...     data_schedule=trunc_schedule2020,
        ...     data_production=production_regular2020,
        ...     min_week=3,
        ...     max_week=None,
        ...     mean_prod=True
        ... )
        """
        if max_week is None:
            max_weeks = data_production["week"].max()
            iter_range = range(min_week, max_weeks + 1)
        elif (type(max_week) is int) and (max_week > 17):
            iter_range = range(min_week, (17 + 1))
        elif type(max_week) is int:
            iter_range = range(min_week, max_week + 1)

        print(f"\n-- Training data for {list(iter_range)[-1] - 1} weeks --\n")

        design_matrix = pd.DataFrame()
        for w in iter_range:
            tmp_design_matrix = self.design_matrix_by_week(
                data_schedule=data_schedule,
                data_production=data_production,
                week=w,
                mean_prod=mean_prod,
            )

            design_matrix = design_matrix.append(tmp_design_matrix)

            if self.verbose:
                print(f"\n-- Week Complete: {w} --\n")

        design_matrix.reset_index(drop=True, inplace=True)

        # Purely for aesthetics
        rearrange_feats = Utilities().arrange_features(data_object=design_matrix)
        design_matrix = design_matrix.loc[:, rearrange_feats]

        return design_matrix
