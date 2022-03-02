import io
import os

# import boto3
import pandas as pd
from dotenv import load_dotenv


class AWSModule:
    def __init__(self, verbose=False):
        """
        Instantiates class.

        Parameters
        ----------
        verbose : boolean
            specifies whether certain statements should be
            logged to the console.
        """

        self.verbose = verbose

        load_dotenv()
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.local_data_dir = os.getenv("LOCAL_DATA_DIR")

        # self.client = boto3.client(
        #     "s3",
        #     aws_access_key_id=self.aws_access_key,
        #     aws_secret_access_key=self.aws_secret_access_key,
        # )

    def list_parquet(self, use_prefix=None):
        if use_prefix is None:
            use_prefix = "prefix place holder"

        obj = self.client.list_objects_v2(
            Bucket="bucket place holder", Prefix=use_prefix
        )

        obj_dt = obj.get("Contents")
        print("\n-- File: {} --\n\n".format(list(obj.keys())))

        print("\n-- FileTwo: {} --\n".format(len(obj_dt)))

        print("\n-- FileTwoKeys: {} --\n\n".format(list(obj_dt[0].keys())))

        object_lst = []
        for i in obj_dt:
            tmp_ = i["Key"]
            print("\n-- Key: {} --\n".format(tmp_))
            object_lst.append(tmp_)

        return object_lst

    def get_object(self, bucket=None, key=None):
        """
        get_object Retrieve data object from S3 bucket.

        Parameters
        ----------
        bucket : str, optional
            _description_, by default None
        key : str, optional
            _description_, by default None

        Returns
        -------
        DataFrame
            _description_
        """
        if bucket is None:
            bucket = "bucket place holder"

        if key is None:
            key = "key place holder"

        aws_object = self.client.get_object(
            Bucket=bucket,
            Key=key,
        )

        if ".csv" in key:
            data_object = pd.read_csv(aws_object["Body"])
        elif ".parquet" in key:
            bytes_object = io.BytesIO(aws_object["Body"].read())
            data_object = pd.read_parquet(bytes_object)

        return data_object

    def get_parquet_object(self, bucket=None, key=None):
        if bucket is None:
            bucket = "bucket place holder"

        if key is None:
            key = "key place holder"

        aws_object = self.client.get_object(
            Bucket=bucket,
            Key=key,
        )

        bytes_object = io.BytesIO(aws_object["Body"].read())
        data_parquet = pd.read_parquet(bytes_object)

        upd_key = key.replace("raw/", "processed/")
        upd_key = upd_key.replace(".parquet", "-all.parquet")
        print("\n-- Key: {} --\n".format(upd_key))
        self.process_path_key = "s3://{}/{}".format(bucket, upd_key)

        return data_parquet

    def upload_file(self, data_object):
        # wr.s3.to_parquet(df=data_object, path=self.process_path_key)

        print("\n-- COMPLETE --\n")


if __name__ == "__main__":

    clsAWS = AWSModule()
