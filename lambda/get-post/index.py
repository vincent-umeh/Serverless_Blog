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
    Lambda function to get a single blog post by slug.
    Returns the blog post details or 404 if not found.
    """
    try:
        # Get the slug from the path parameters
        path_parameters = event.get('pathParameters', {})
        if not path_parameters or 'slug' not in path_parameters:
            return {
                'statusCode': 400,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Missing slug parameter'})
            }
        
        slug = path_parameters['slug']
        
        # Query the post by slug using the GSI
        response = table.query(
            IndexName='SlugIndex',
            KeyConditionExpression=Key('slug').eq(slug)
        )
        
        # Check if post exists
        items = response.get('Items', [])
        if not items:
            return {
                'statusCode': 404,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Post not found'})
            }
        
        # Return the first (and should be only) post with this slug
        post = items[0]
        
        return {
            'statusCode': 200,
            'headers': get_headers(),
            'body': json.dumps(post, default=datetime_serializer)
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