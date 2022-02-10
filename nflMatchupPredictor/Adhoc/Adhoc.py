class Adhoc:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def abbrev_tbl(self):
        tmp_dt = {
            "Houston Texans": "htx",
            "Cleveland Browns": "cle",
            "Jacksonville Jaguars": "jax",
            "Carolina Panthers": "car",
            "Buffalo Bills": "buf",
            "htx": "Houston Texans",
            "cle": "Cleveland Browns",
            "jax": "Jacksonville Jaguars",
            "car": "Carolina Panthers",
            "buf": "Buffalo Bills",
        }

        return tmp_dt
