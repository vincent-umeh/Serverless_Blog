import json
import os
import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE')
table = dynamodb.Table(table_name)

def handler(event, context):
    """
    Lambda function to delete a blog post by slug.
    Removes the post from DynamoDB.
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
        
        # Find the post by slug
        response = table.query(
            IndexName='SlugIndex',
            KeyConditionExpression=Key('slug').eq(slug)
        )
        
        items = response.get('Items', [])
        if not items:
            return {
                'statusCode': 404,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Post not found'})
            }
        
        # Get the post ID and createdAt for the primary key
        post = items[0]
        post_id = post['id']
        created_at = post['createdAt']
        
        # Delete the post
        table.delete_item(
            Key={
                'id': post_id,
                'createdAt': created_at
            }
        )
        
        return {
            'statusCode': 200,
            'headers': get_headers(),
            'body': json.dumps({'message': 'Post deleted successfully'})
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
        'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
    }