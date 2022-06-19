import logging
import os
import zipfile
from mimetypes import MimeTypes

from boto3.session import Session
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


class S3Manager:
    """
    Manage uploading files to and deleting files from S3 bucket.

    To run this manager, you should have AWS_KEY and AWS_SECRET in os environment variables
    Attributes:
        bucket_name :- this is the s3 bucket name.
    """

    _AWS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", None)
    _AWS_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
    _AWS_REGION = os.environ.get("AWS_REGION_NAME", None) or settings.AWS_S3_REGION_NAME

    def __init__(self, bucket_name):
        """Load session and bucket name for the S3 bucket."""
        self.bucket_name = bucket_name
        self._session = Session(
            aws_access_key_id=self._AWS_KEY,
            aws_secret_access_key=self._AWS_SECRET,
            region_name=self._AWS_REGION,
        )
        self.s3 = self._session.resource("s3")
        self.s3client = self._session.client("s3")

    def upload_file(self, file_name, filepath, acl="public-read"):
        """
        Do upload_file and return dict of url and key.

        Args
        ----
            file_name: this is string.
            filepath: this is the path of the file to upload.
            acl: public-read,public, public-write

        Returns
        -------
            {
                'url': Object url for uploaded file,
                'key': file location in S3 bucker,
                'public_url': url for viewing file
            }

        """
        mime_type = MimeTypes().guess_type(filepath)[0]
        with open(filepath, "rb") as data:
            s3_obj = self.s3.Bucket(self.bucket_name).put_object(
                Key=file_name, Body=data, ACL=acl, ContentType=mime_type
            )
        url = self.s3client.generate_presigned_url(
            "put_object", Params={"Bucket": self.bucket_name, "Key": s3_obj.key}
        )
        return {
            "url": url,
            "key": s3_obj.key,
            "public_url": f"https://{self.bucket_name}.s3.amazonaws.com/file_name",
        }

    def delete_file(self, file_name):
        """Do delete_file and return True."""
        obj = self.s3.Object(self.bucket_name, file_name)
        obj.delete()
        return True

    def download_file(self, file_name, downloaded_file_name=None):
        """Download the file in the current directory."""
        try:
            if not downloaded_file_name:
                downloaded_file_name = str(file_name.split("/")[-1])
            self.s3.Bucket(self.bucket_name).download_file(
                file_name, os.path.join(os.getcwd(), downloaded_file_name)
            )
            return downloaded_file_name
        except ClientError as e:
            logger.error(e)
            if e.response["Error"]["Code"] != "404":
                raise
            logger.error("The object does not exist.")

    def download_files_in_zip(self, file_object_key_list, zip_file_name):
        """
        Download the file and will make zip current directory.

        Args
        ----
            file_object_key_list: list of filekeyobject of s3.

        Returns
        -------
            zip file name with extension if successful, else raise error.

        Raises
        ------
            AWS Exception

        """
        # TODO: make it parallel download
        # TODO: handle name conflict
        for file in file_object_key_list:
            self.download_file(file)
        zip_file_name_with_ext = self._get_zip_file_name_with_ext(zip_file_name)
        zip_file_path = os.path.join(os.getcwd(), str(zip_file_name_with_ext))
        with zipfile.ZipFile(zip_file_path, "w") as zip_file:
            for file in file_object_key_list:
                file = file.split("/")[-1]
                zip_file.write(file)
        for file in file_object_key_list:
            os.remove(file.split("/")[-1])

        return zip_file_name_with_ext

    def _get_zip_file_name_with_ext(self, zip_file_name: str):
        ext = ".zip"
        return zip_file_name if zip_file_name.endswith(ext) else f"{zip_file_name}{ext}"

    def create_presigned_url(self, object_name, expiration=3600):
        """
        Generate a presigned URL to share an S3 object.

        Args
        ----
        object_name: string
        expiration: Time in seconds for the presigned URL to remain valid

        Returns
        -------
        Presigned URL as string. If error, returns None.

        """
        try:
            signed_url = self.s3client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_name},
                ExpiresIn=expiration,
            )
        except ClientError as e:
            logging.error(e)
            return None

        return signed_url
