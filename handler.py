import json
import boto3
import os
from openai import OpenAI
from botocore.exceptions import ClientError
from decimal import Decimal

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("MotivationalQuotes")

# OpenAI API Key (store securely in environment variables)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Helper function to convert Decimal to int or float
def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)  # Convert to int if whole number, else float
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]  # Convert lists recursively
    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}  # Convert dicts recursively
    return obj

# Function to get all quotes
def get_motivational_quotes(event, context):
    try:
        response = table.scan()
        
        # Convert Decimal values before returning JSON
        quotes = convert_decimal(response.get("Items", []))

        return {
            "statusCode": 200,
            "body": json.dumps({"quotes": quotes})
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": e.response["Error"]["Message"]})
        }

# Function to get quotes by year
def get_motivational_quotes_by_year(event, context):
    year = int(event["pathParameters"]["year"])  # Ensure it's an integer

    try:
        response = table.scan(
            FilterExpression="#yr = :year",
            ExpressionAttributeNames={"#yr": "year"},
            ExpressionAttributeValues={":year": year}  
        )
        
        # Convert Decimal values before returning JSON
        quotes = convert_decimal(response.get("Items", []))
        
        return {
            "statusCode": 200,
            "body": json.dumps({"quotes": quotes})
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": e.response["Error"]["Message"]})
        }

# Function to generate an AI explanation for a given quote
def generate_quote_explanation(event, context):
    try:
        body = json.loads(event["body"])
        quote_id = body.get("quote_id")
        if not quote_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "quote_id is required"})
            }

        # Fetch the quote from DynamoDB
        response = table.get_item(Key={"quote_id": quote_id})
        quote_item = response.get("Item")
        if not quote_item:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Quote not found"})
            }
        quote_item = convert_decimal(quote_item)

        # Create a prompt using the quote_text field (make sure your DynamoDB items use the field name "quote_text")
        prompt = f"Explain this motivational quote in simple terms: \"{quote_item['quote_text']}\""

        # Generate the AI explanation using the new client interface
        ai_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )

        # Use dot notation to access the returned message content
        explanation = ai_response.choices[0].message.content.strip()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "quote_id": quote_id,
                "quote_text": quote_item["quote_text"],
                "explanation": explanation
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    
# Function to search quotes by keyword
def search_quotes(event, context):
    keyword = event["queryStringParameters"].get("keyword", "").lower()

    if not keyword:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Keyword query parameter is required."})
        }

    try:
        response = table.scan()
        all_quotes = response.get("Items", [])

        # Filter quotes that contain the keyword in text
        filtered_quotes = [
            quote for quote in all_quotes if keyword in quote.get("quote_text", "").lower()
        ]

        return {
            "statusCode": 200,
            "body": json.dumps({"quotes": convert_decimal(filtered_quotes)})
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": e.response["Error"]["Message"]})
        }

# Function to filter quotes by category
def filter_quotes_by_category(event, context):
    category = event["queryStringParameters"].get("category", "").lower()

    if not category:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Category query parameter is required."})
        }

    try:
        response = table.scan(
            FilterExpression="contains(#cat, :category)",
            ExpressionAttributeNames={"#cat": "category"},
            ExpressionAttributeValues={":category": category}
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"quotes": convert_decimal(response.get("Items", []))})
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": e.response["Error"]["Message"]})
        }
    
def filter_quotes_by_author(event, context):
    author = event["queryStringParameters"].get("author", "").lower()

    if not author:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Author query parameter is required."})
        }

    try:
        response = table.scan(
            FilterExpression="contains(#auth, :author)",
            ExpressionAttributeNames={"#auth": "author"},
            ExpressionAttributeValues={":author": author}
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"quotes": convert_decimal(response.get("Items", []))})
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": e.response["Error"]["Message"]})
        }

# Function to filter quotes by year
def filter_quotes_by_year(event, context):
    year = event["queryStringParameters"].get("year", "")

    if not year.isdigit():
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Year query parameter must be a valid integer."})
        }

    year = int(year)

    try:
        response = table.scan(
            FilterExpression="#yr = :year",
            ExpressionAttributeNames={"#yr": "year"},
            ExpressionAttributeValues={":year": year}
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"quotes": convert_decimal(response.get("Items", []))})
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": e.response["Error"]["Message"]})
        }