import boto3
from botocore.exceptions import ClientError

class BucketManager:
    def __init__(self, endpoint_url, access_key, secret_key):
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key

        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )

        print(f"Connected to MinIO at {self.endpoint_url}")

    def bucket_exists(self, bucket_name):
        response = self.s3_client.list_buckets()
        for bucket in response['Buckets']:
            if bucket['Name'] == bucket_name:
                return True
            else:
                return False

    def create_bucket(self, bucket_name):
        try:
            response = self.s3_client.create_bucket(Bucket=bucket_name)
            return response
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyOwnedByYou':
                print(f"The bucket {bucket_name} already exists and is owned by you")
            elif error_code == 'BucketAlreadyExists':
                print(f"The bucket {bucket_name} already exists but is owned by someone else")


    def list_buckets(self):
            response = self.s3_client.list_buckets()
            buckets = []
            for bucket in response['Buckets']:
                buckets.append(bucket['Name'])
            print(buckets)
