import json
import boto3
import os
from openai import OpenAI
from botocore.exceptions import ClientError
from decimal import Decimal
import requests
import uuid
import time

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("MotivationalQuotes")
favorites_table = boto3.resource("dynamodb", region_name="us-east-1").Table("FavoritesTable")
history_table = boto3.resource("dynamodb", region_name="us-east-1").Table("HistoryTable")

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

def get_user_id(event):
    try:
        return event["requestContext"]["authorizer"]["claims"]["sub"]
    except Exception:
        return None

def add_quote(event, context):
    user_id = get_user_id(event)
    try:
        body = json.loads(event["body"])
        # Required fields: quote_text, author, year (category, image_url optional)
        quote_text = body.get("quote_text")
        author = body.get("author")
        year = body.get("year")
        category = body.get("category")
        image_url = body.get("image_url")
        if not quote_text or not author or not year:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "quote_text, author, and year are required"})
            }
        # Generate a unique quote_id
        quote_id = str(uuid.uuid4())
        # Store in DynamoDB
        item = {
            "quote_id": quote_id,
            "quote_text": quote_text,
            "author": author,
            "year": int(year)
        }
        if category:
            item["category"] = category
        if image_url:
            item["image_url"] = image_url
        table.put_item(Item=item)
        # Generate embedding using OpenAI
        embedding_response = client.embeddings.create(
            input=quote_text,
            model="text-embedding-3-small"
        )
        embedding = embedding_response.data[0].embedding
        # Send embedding to FAISS microservice
        faiss_url = os.getenv("FAISS_SERVICE_URL", "http://localhost:5000/add_embedding")
        faiss_payload = {"quote_id": quote_id, "embedding": embedding}
        faiss_resp = requests.post(faiss_url, json=faiss_payload)
        if faiss_resp.status_code != 200:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Failed to add embedding to FAISS service"})
            }
        return {
            "statusCode": 201,
            "body": json.dumps({"quote_id": quote_id, "message": "Quote added successfully"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def semantic_search(event, context):
    user_id = get_user_id(event)
    try:
        body = json.loads(event["body"])
        query = body.get("query")
        top_k = int(body.get("top_k", 5))
        if not query:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "query is required"})
            }
        # Generate embedding for the query
        embedding_response = client.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        )
        embedding = embedding_response.data[0].embedding
        # Send embedding to FAISS microservice for search
        faiss_url = os.getenv("FAISS_SERVICE_URL", "http://localhost:5000/search")
        faiss_payload = {"embedding": embedding, "top_k": top_k}
        faiss_resp = requests.post(faiss_url, json=faiss_payload)
        if faiss_resp.status_code != 200:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Failed to search FAISS service"})
            }
        result_ids = faiss_resp.json().get("results", [])
        # Fetch quotes from DynamoDB
        quotes = []
        for quote_id in result_ids:
            resp = table.get_item(Key={"quote_id": quote_id})
            item = resp.get("Item")
            if item:
                quotes.append(convert_decimal(item))
        return {
            "statusCode": 200,
            "body": json.dumps({"quotes": quotes})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def personalized_recommendations(event, context):
    user_id = get_user_id(event)
    try:
        body = json.loads(event["body"])
        # Accept either a 'profile' string or a 'history' list of strings
        profile = body.get("profile")
        history = body.get("history")
        top_k = int(body.get("top_k", 5))
        if profile:
            user_text = profile
        elif history and isinstance(history, list):
            user_text = " ".join(history)
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "profile (string) or history (list of strings) is required"})
            }
        # Generate embedding for the user
        embedding_response = client.embeddings.create(
            input=user_text,
            model="text-embedding-3-small"
        )
        embedding = embedding_response.data[0].embedding
        # Send embedding to FAISS microservice for search
        faiss_url = os.getenv("FAISS_SERVICE_URL", "http://localhost:5000/search")
        faiss_payload = {"embedding": embedding, "top_k": top_k}
        faiss_resp = requests.post(faiss_url, json=faiss_payload)
        if faiss_resp.status_code != 200:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Failed to search FAISS service"})
            }
        result_ids = faiss_resp.json().get("results", [])
        # Fetch quotes from DynamoDB
        quotes = []
        for quote_id in result_ids:
            resp = table.get_item(Key={"quote_id": quote_id})
            item = resp.get("Item")
            if item:
                quotes.append(convert_decimal(item))
        return {
            "statusCode": 200,
            "body": json.dumps({"quotes": quotes})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def batch_upload_quotes(event, context):
    user_id = get_user_id(event)
    try:
        body = json.loads(event["body"])
        quotes = body.get("quotes")
        if not quotes or not isinstance(quotes, list):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "'quotes' (list) is required"})
            }
        successes = []
        failures = []
        for quote in quotes:
            try:
                quote_text = quote.get("quote_text")
                author = quote.get("author")
                year = quote.get("year")
                category = quote.get("category")
                image_url = quote.get("image_url")
                if not quote_text or not author or not year:
                    raise ValueError("quote_text, author, and year are required")
                quote_id = str(uuid.uuid4())
                item = {
                    "quote_id": quote_id,
                    "quote_text": quote_text,
                    "author": author,
                    "year": int(year)
                }
                if category:
                    item["category"] = category
                if image_url:
                    item["image_url"] = image_url
                table.put_item(Item=item)
                embedding_response = client.embeddings.create(
                    input=quote_text,
                    model="text-embedding-3-small"
                )
                embedding = embedding_response.data[0].embedding
                faiss_url = os.getenv("FAISS_SERVICE_URL", "http://localhost:5000/add_embedding")
                faiss_payload = {"quote_id": quote_id, "embedding": embedding}
                faiss_resp = requests.post(faiss_url, json=faiss_payload)
                if faiss_resp.status_code != 200:
                    raise Exception("Failed to add embedding to FAISS service")
                successes.append(quote_id)
            except Exception as e:
                failures.append({"quote": quote, "error": str(e)})
        return {
            "statusCode": 200,
            "body": json.dumps({"successes": successes, "failures": failures})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def favorite_quote(event, context):
    user_id = get_user_id(event)
    quote_id = event["pathParameters"]["id"]
    try:
        favorites_table.put_item(Item={"user_id": user_id, "quote_id": quote_id})
        return {"statusCode": 200, "body": json.dumps({"message": "Favorited"})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

def unfavorite_quote(event, context):
    user_id = get_user_id(event)
    quote_id = event["pathParameters"]["id"]
    try:
        favorites_table.delete_item(Key={"user_id": user_id, "quote_id": quote_id})
        return {"statusCode": 200, "body": json.dumps({"message": "Unfavorited"})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

def get_favorites(event, context):
    user_id = get_user_id(event)
    try:
        resp = favorites_table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key("user_id").eq(user_id))
        quote_ids = [item["quote_id"] for item in resp.get("Items", [])]
        # Fetch quote details from main table
        quotes = []
        for quote_id in quote_ids:
            q = table.get_item(Key={"quote_id": quote_id}).get("Item")
            if q:
                quotes.append(convert_decimal(q))
        return {"statusCode": 200, "body": json.dumps({"favorites": quotes})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

def add_to_history(event, context):
    user_id = get_user_id(event)
    quote_id = event["pathParameters"]["id"]
    timestamp = str(int(time.time()))
    try:
        history_table.put_item(Item={"user_id": user_id, "timestamp": timestamp, "quote_id": quote_id})
        return {"statusCode": 200, "body": json.dumps({"message": "History updated"})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

def get_history(event, context):
    user_id = get_user_id(event)
    try:
        resp = history_table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key("user_id").eq(user_id), ScanIndexForward=False, Limit=20)
        items = resp.get("Items", [])
        # Fetch quote details from main table
        quotes = []
        for item in items:
            q = table.get_item(Key={"quote_id": item["quote_id"]}).get("Item")
            if q:
                quotes.append(convert_decimal(q))
        return {"statusCode": 200, "body": json.dumps({"history": quotes})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}