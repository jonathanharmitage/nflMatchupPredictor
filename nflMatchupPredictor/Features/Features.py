class Features:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def rename_features(self):
        dt = {"expected points_sp. tms": "expected points_sp_tms"}

        return dt

    def meta_features(self, team=None):
        meta_features = [
            "nfl_team",
            "nfl_team_abbrev",
            "nfl_team_name",
            "nfl_season",
            "season_source",
            "week",
            "day",
            "date",
            "game_time",
            "boxscore",
            "score_tm",
            "score_opp",
            "win_loss",
            "win_loss_as_int",
            "ot",
            "rec",
            "home_away",
            "opp",
            "opp_name",
            "opp_abbrev",
            "winning_team",
            "winning_team_equals_home_team",
            "expected_points_offense",
            "expected_points_defense",
            "expected_points_special_tms",
        ]

        if (team is not None) and (type(team) is str):
            meta_features = [i + "_" + team for i in meta_features]

        return meta_features

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
