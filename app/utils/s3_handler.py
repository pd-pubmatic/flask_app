import boto3
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

class S3Handler:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
        )
        self.bucket = Config.S3_BUCKET
        self.folder = Config.S3_RESULTS_FOLDER

    async def upload_result(self, request_id: str, payload: dict):
        """Upload result JSON to S3 bucket."""
        try:
            file_name = f"{self.folder}{request_id}.json"
            json_data = json.dumps(payload)
            
            self.s3.put_object(
                Bucket=self.bucket,
                Key=file_name,
                Body=json_data,
                ContentType='application/json'
            )
            
            logger.info(f"Successfully uploaded results to S3: {file_name}")
        except Exception as e:
            logger.error(f"Error uploading to S3: {e}")


    def check_result_exists(self, request_id: str) -> bool:
        """Check if result exists in S3 for given request_id."""
        try:
            file_name = f"{self.folder}{request_id}.json"
            self.s3.head_object(
                Bucket=self.bucket,
                Key=file_name
            )
            return True
        except self.s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"Error checking S3 for request_id {request_id}: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error checking S3: {e}")
            raise 

    def get_result(self, request_id: str) -> dict:
        """Get result JSON from S3 bucket for given request_id."""
        try:
            file_name = f"{self.folder}{request_id}.json"
            response = self.s3.get_object(
                Bucket=self.bucket,
                Key=file_name
            )
            return json.loads(response['Body'].read().decode('utf-8'))
        except self.s3.exceptions.NoSuchKey:
            logger.warning(f"No result found for request_id: {request_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting result from S3: {e}")
            raise 