import os
import boto3
from dotenv import load_dotenv
import toml

# Set parameters to create S3 bucket that will store the Weather API data we collected
load_dotenv()
ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
app_config = toml.load('config_file.toml')
bucket_name = app_config['aws']['bucket_name']
aws_region = app_config['aws']['aws_region']

# Connect to S3
session = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)
s3_client = session.client('s3')

# Create S3 bucket in the aws region we specified
s3_client.create_bucket(
    Bucket=bucket_name,  
    CreateBucketConfiguration={'LocationConstraint': aws_region} 
)
