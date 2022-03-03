from nflMatchupPredictor.DataBuilds.DataBuilds import DataBuilds
from nflMatchupPredictor.DataLoaders.DataLoader import DataLoader


class TestEnv:
    def __init__(self, verbose=False):
        self.data_loader = DataLoader()
        self.data_build = DataBuilds()
        self.verbose = verbose

    def dot_main(self, nfl_year, min_week=2, max_week=None, mean_prod=False):
        """
        dot_main _summary_

        Parameters
        ----------
        nfl_year : int
            NFL season
        min_week : int, optional
            Minimum regular season week to being to build training data, by default 2
        max_week : int, optional
            Maximum week to be included in the training dataset, by default None
        mean_prod : bool, optional
            If True production metrics are aggregated by taking the mean, else aggregation
            is accomplished via summing over all relevant values, by default False

        Returns
        -------
        DataFrame
            Dataset containing NFL matchups with production metrics mapped temporally.

        Example
        -------
        >>> data_tbl = self.dot_main(
        ...     nfl_year=2020,
        ...     min_week=3,
        ...     max_week=None,
        ...     mean_prod=True
        ... )
        """
        data_schedule = self.data_loader.load_data_by_year(
            nfl_year=nfl_year, production=False
        )
        data_production = self.data_loader.load_data_by_year(
            nfl_year=nfl_year, production=True
        )
        schedule_regular, production_regular = self.data_build.filter_and_truncate(
            data_schedule=data_schedule, data_production=data_production
        )

        data_tbl = self.data_build.design_iter_dot_main(
            data_schedule=schedule_regular,
            data_production=production_regular,
            min_week=min_week,
            max_week=max_week,
            mean_prod=mean_prod,
        )

        return data_tbl


if __name__ == "__main__":
    clsTest = TestEnv()
    data_tbl = clsTest.dot_main(nfl_year=2020, min_week=3, max_week=None, mean_prod=True)

    if data_tbl.shape[0] > 0:
        print("\n\n-- Success --\n\n")
    else:
        print("\n\n-- Check Code --\n\n")
