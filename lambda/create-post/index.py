import json
import os
import uuid
import boto3
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
    Lambda function to create a new blog post.
    Accepts post data in the request body and stores it in DynamoDB.
    """
    try:
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
        
        # Validate required fields
        required_fields = ['title', 'content']
        for field in required_fields:
            if field not in post_data:
                return {
                    'statusCode': 400,
                    'headers': get_headers(),
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }
        
        # Generate a slug from the title if not provided
        slug = post_data.get('slug')
        if not slug:
            slug = generate_slug(post_data['title'])
        
        # Check if slug already exists
        response = table.query(
            IndexName='SlugIndex',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('slug').eq(slug)
        )
        
        if response.get('Items'):
            return {
                'statusCode': 409,
                'headers': get_headers(),
                'body': json.dumps({'error': 'A post with this slug already exists'})
            }
        
        # Generate timestamp and ID
        timestamp = datetime.utcnow().isoformat()
        post_id = str(uuid.uuid4())
        
        # Process content for embedded images
        content, image_urls = process_images(post_data['content'], post_id)
        
        # Create the post item
        post_item = {
            'id': post_id,
            'slug': slug,
            'title': post_data['title'],
            'content': content,
            'createdAt': timestamp,
            'updatedAt': timestamp
        }
        
        # Add optional fields if they exist
        optional_fields = ['author', 'excerpt', 'coverImage', 'tags', 'status']
        for field in optional_fields:
            if field in post_data:
                post_item[field] = post_data[field]
        
        # Add image URLs if any were processed
        if image_urls:
            post_item['images'] = image_urls
        
        # Save to DynamoDB
        table.put_item(Item=post_item)
        
        return {
            'statusCode': 201,
            'headers': get_headers(),
            'body': json.dumps(post_item, default=datetime_serializer)
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_headers(),
            'body': json.dumps({'error': str(e)})
        }

def generate_slug(title):
    """Generate a URL-friendly slug from a title"""
    # Convert to lowercase and replace spaces with hyphens
    slug = title.lower().strip()
    # Remove special characters
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    return slug

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
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
    }

def datetime_serializer(obj):
    """Helper function to serialize datetime objects to ISO format strings"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")