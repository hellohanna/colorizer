import boto3, botocore
import os

S3_BUCKET   = os.environ.get("S3_BUCKET")
S3_KEY      = os.environ.get("S3_KEY")
S3_SECRET   = os.environ.get("S3_SECRET_ACCESS_KEY")
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)


client = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET
)

def upload(file, filename):
    client.upload_fileobj(
        file,
        S3_BUCKET,
        filename,
        ExtraArgs={
            "ACL": "public-read",
            "ContentType": file.content_type
        }
    )

def url_for(filename):
    """Create url for file in s3"""
    return "{}{}".format(S3_LOCATION, filename)