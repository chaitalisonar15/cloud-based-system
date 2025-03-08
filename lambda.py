import json
import pandas as pd
import boto3
from datetime import datetime

# Initialize S3 and DynamoDB clients
s3_client = boto3.client('s3', endpoint_url='http://localhost:4566')
dynamodb_client = boto3.client('dynamodb', endpoint_url='http://localhost:4566')

def lambda_handler(event, context):
    # Get file details from event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    
    # Download the CSV file from S3
    file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    csv_data = file_obj['Body'].read().decode('utf-8')
    
    # Read CSV into a pandas DataFrame
    df = pd.read_csv(pd.compat.StringIO(csv_data))

    # Extract metadata
    metadata = {
        'filename': file_key,
        'upload_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'file_size_bytes': file_obj['ContentLength'],
        'row_count': len(df),
        'column_count': len(df.columns),
        'column_names': list(df.columns)
    }

    # Store metadata in DynamoDB
    table_name = 'CsvMetadata'
    dynamodb_client.put_item(
        TableName=table_name,
        Item={
            'filename': {'S': metadata['filename']},
            'upload_timestamp': {'S': metadata['upload_timestamp']},
            'file_size_bytes': {'N': str(metadata['file_size_bytes'])},
            'row_count': {'N': str(metadata['row_count'])},
            'column_count': {'N': str(metadata['column_count'])},
            'column_names': {'SS': metadata['column_names']}
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(metadata)
    }
