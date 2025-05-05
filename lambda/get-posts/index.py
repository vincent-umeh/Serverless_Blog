import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE')
table = dynamodb.Table(table_name)

def handler(event, context):
    """
    Lambda function to get all blog posts.
    Returns a list of blog posts sorted by creation date (newest first).
    """
    try:
        # Get query parameters for pagination if they exist
        query_params = event.get('queryStringParameters', {}) or {}
        limit = int(query_params.get('limit', 10))
        last_evaluated_key = query_params.get('nextToken')
        
        # Convert last_evaluated_key from string to dict if it exists
        if last_evaluated_key:
            try:
                last_evaluated_key = json.loads(last_evaluated_key)
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': get_headers(),
                    'body': json.dumps({'error': 'Invalid nextToken format'})
                }
        
        # Query parameters for the scan operation
        scan_params = {
            'Limit': limit,
        }
        
        # Add LastEvaluatedKey if it exists
        if last_evaluated_key:
            scan_params['ExclusiveStartKey'] = last_evaluated_key
        
        # Scan the table
        response = table.scan(**scan_params)
        
        # Prepare the response
        items = response.get('Items', [])
        
        # Sort items by createdAt in descending order (newest first)
        items.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        # Prepare pagination info
        result = {
            'posts': items,
            'count': len(items),
            'total': response.get('Count', 0)
        }
        
        # Add nextToken if LastEvaluatedKey exists
        if 'LastEvaluatedKey' in response:
            result['nextToken'] = json.dumps(response['LastEvaluatedKey'])
        
        return {
            'statusCode': 200,
            'headers': get_headers(),
            'body': json.dumps(result, default=datetime_serializer)
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def get_headers():
    """Return standard headers for API responses"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
    }

def datetime_serializer(obj):
    """Helper function to serialize datetime objects to ISO format strings"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")