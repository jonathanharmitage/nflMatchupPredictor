import os

from dotenv import load_dotenv


class Utilities:
    def __init__(self, verbose=False):
        self.verbose = verbose

        load_dotenv()
        self.local_data_raw_dir = os.getenv("LOCAL_RAW_DATA_DIR")

    def write_local(self, data_object, write_name):
        if ".csv" not in write_name:
            write_name += ".csv"

        data_object.to_csv(self.local_data_raw_dir + "/" + write_name, index=False)
