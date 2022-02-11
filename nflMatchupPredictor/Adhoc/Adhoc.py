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
            "oti": "Tennessee Titans",
            "Tennessee Titans": "oti",
            "cin": "Cincinnati Bengals",
            "Cincinnati Bengals": "cin",
            "ram": "Los Angeles Rams",
            "Los Angeles Rams": "ram",
            "rai": "Las Vegas Raiders",
            "Las Vegas Raiders": "rai",
            "sdg": "San Diego Chargers",
            "San Diego Chargers": "sdg",
            "was": "Washington Football Team",
            "Washington Football Team": "was",
        }

        return tmp_dt
