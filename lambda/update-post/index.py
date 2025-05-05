import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
import re

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE')
table = dynamodb.Table(table_name)

# Initialize S3 client
s3 = boto3.client('s3')
assets_bucket = os.environ.get('ASSETS_BUCKET')

def handler(event, context):
    """
    Lambda function to update an existing blog post.
    Accepts post data in the request body and updates it in DynamoDB.
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
        
        # Parse request body
        body = event.get('body')
        if not body:
            return {
                'statusCode': 400,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Missing request body'})
            }
        
        # Parse JSON body
        try:
            post_data = json.loads(body)
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': get_headers(),
                'body': json.dumps({'error': 'Invalid JSON in request body'})
            }
        
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
        
        # Get the existing post
        existing_post = items[0]
        post_id = existing_post['id']
        
        # Process content for embedded images if content is being updated
        image_urls = existing_post.get('images', [])
        if 'content' in post_data:
            content, new_image_urls = process_images(post_data['content'], post_id)
            post_data['content'] = content
            if new_image_urls:
                image_urls.extend(new_image_urls)
                post_data['images'] = image_urls
        
        # Update timestamp
        post_data['updatedAt'] = datetime.utcnow().isoformat()
        
        # Check if slug is being changed
        new_slug = post_data.get('slug')
        if new_slug and new_slug != slug:
            # Check if the new slug already exists
            response = table.query(
                IndexName='SlugIndex',
                KeyConditionExpression=Key('slug').eq(new_slug)
            )
            
            if response.get('Items'):
                return {
                    'statusCode': 409,
                    'headers': get_headers(),
                    'body': json.dumps({'error': 'A post with this slug already exists'})
                }
        
        # Build update expression and attribute values
        update_expression = "SET updatedAt = :updatedAt"
        expression_attribute_values = {
            ":updatedAt": post_data['updatedAt']
        }
        
        # Add all other fields to update
        for key, value in post_data.items():
            if key not in ['id', 'createdAt', 'updatedAt']:
                update_expression += f", {key} = :{key}"
                expression_attribute_values[f":{key}"] = value
        
        # Update the item in DynamoDB
        table.update_item(
            Key={
                'id': post_id,
                'createdAt': existing_post['createdAt']
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
        )
        
        # Get the updated post
        if new_slug and new_slug != slug:
            # If slug changed, query by the new slug
            response = table.query(
                IndexName='SlugIndex',
                KeyConditionExpression=Key('slug').eq(new_slug)
            )
        else:
            # Otherwise, query by the original slug
            response = table.query(
                IndexName='SlugIndex',
                KeyConditionExpression=Key('slug').eq(slug)
            )
        
        updated_post = response.get('Items', [])[0]
        
        return {
            'statusCode': 200,
            'headers': get_headers(),
            'body': json.dumps(updated_post, default=datetime_serializer)
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def process_images(content, post_id):
    """
    Process embedded base64 images in content, upload to S3,
    and replace with URLs.
    """
    # Pattern to find base64 encoded images
    pattern = r'data:image\/([a-zA-Z]+);base64,([^"\']*)'
    image_urls = []
    
    def replace_image(match):
        image_type = match.group(1)
        base64_data = match.group(2)
        
        try:
            # Decode base64 data
            import base64
            image_data = base64.b64decode(base64_data)
            
            # Generate a unique filename
            filename = f"{post_id}-{len(image_urls)}.{image_type}"
            
            # Upload to S3
            s3.put_object(
                Bucket=assets_bucket,
                Key=f"posts/{post_id}/{filename}",
                Body=image_data,
                ContentType=f"image/{image_type}",
                ACL='public-read'
            )
            
            # Generate the URL
            url = f"https://{assets_bucket}.s3.amazonaws.com/posts/{post_id}/{filename}"
            image_urls.append(url)
            
            return url
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return match.group(0)  # Return original string if processing fails
    
    # Replace all base64 images with URLs
    new_content = re.sub(pattern, replace_image, content)
    
    return new_content, image_urls

def get_headers():
    """Return standard headers for API responses"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'PUT, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
    }

def datetime_serializer(obj):
    """Helper function to serialize datetime objects to ISO format strings"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")