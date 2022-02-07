import os

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv


class AzureModule:
    def __init__(self, ctn_name, verbose=False):
        """
        Instantiates class.

        Parameters
        ----------
        ctn_name : string
            name container of container
        verbose : boolean
            specifies whether certain statements should be
            logged to the console.
        """

        self.ctn_name = ctn_name
        self.verbose = verbose

        load_dotenv()
        self.azure_cnx_string = os.getenv("AZURE_CNX_STRING_ONE")
        self.local_data_dir = os.getenv("LOCAL_DATA_DIR")

    def azure_connect(self):
        """
        Connect to Azure resource group.
        """
        blob_service_client = BlobServiceClient.from_connection_string(
            self.azure_cnx_string
        )

        container_client = blob_service_client.get_container_client(
            container=self.ctn_name
        )

        return container_client

    def list_blobs(self, container_client):
        """
        List blobs that are contained within a container.

        Parameters
        ----------
        container_client : azure container client
            [description]
        """

        blob_list = container_client.list_blobs()
        for blobs in blob_list:
            print("\n-- ", blobs.name, " --\n")

    def fetch_blob(self, container_client, tbl_name):
        """
        Fetch table from blob storage.

        Parameters
        ----------
        container_client : azure container client
            [description]
        tbl_name : string
            name of table to be fetched.
        """
        blob_client = container_client.get_blob_client(tbl_name)
        download_to = self.local_data_dir + "/{}".format(tbl_name)

        with open(download_to, "wb") as azure_file:
            tmp_data = blob_client.download_blob()
            azure_file.write(tmp_data.readall())

        if self.verbose:
            print("\n-- ", os.listdir(self.local_data_dir), " --\n\n")
            print(
                "\n-- Number of Files == {} --\n".format(
                    len(os.listdir(self.local_data_dir))
                )
            )


if __name__ == "__main__":

    clsAzure = AzureModule()
    container_client = clsAzure.azure_connect()
    # clsAzure.fetch_blob(
    #     container_client=container_client,
    #     tbl_name="data_schema.csv")
