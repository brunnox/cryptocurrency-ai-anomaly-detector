import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import json

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

        if self.s3_client:
            print(f"Connected to MinIO at {self.endpoint_url}")
        else:
            print("Cannot connect to MinIO")

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

    def store_json_file(self, bucket_name, file_path, data):
        try:
            json_data = json.dumps(data, indent=2,  default=str)
            print(f"JSON conversion successful, size: {len(json_data)} bytes")

            print(f"Uploading to bucket: {bucket_name}, path: {file_path}")
            response = self.s3_client.put_object(
                Body=json_data,
                Bucket=bucket_name,
                Key=file_path
            )
            print(f"Upload successful! Response: {response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")
            return True

        except Exception as e:
            print(f"Error in store_json_file: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            return False


    def _generate_partition_path(self, data_type, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        partition_path = f"raw/{data_type}/year={timestamp.year}/month={timestamp.month:02d}/day={timestamp.day:02d}/hour={timestamp.hour:02d}"
    
        return partition_path

    def _generate_filename(self, data_type, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        filename = f"{data_type}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        return filename

    def list_files(self, bucket_name, prefix=""):
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )

            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
                print(f"Found {len(files)} files with prefix '{prefix}'")
                return files
            else:
                print(f"No files found with prefix '{prefix}'")
                return []

        except Exception as e:
            print(f"Failed to list files: {e}")
            return []

    def store_crypto_data(self, bucket_name, crypto_data):
        timestamp_str = crypto_data['collection_metadata']['timestamp']

        if timestamp_str.endswith('Z'):
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            timestamp = datetime.fromisoformat(timestamp_str)

        partition_path = self._generate_partition_path('crypto_prices', timestamp)
        filename = self._generate_filename('crypto_prices', timestamp)
        full_path = f"{partition_path}/{filename}"

        success = self.store_json_file(bucket_name, full_path, crypto_data)
        
        if success:
            print(f"Stored crypto data at: {full_path}")
            return full_path
        else:
            print(timestamp)
            print(full_path)
            return None