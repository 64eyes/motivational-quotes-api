import boto3 # type: ignore
import json
from botocore.exceptions import ClientError # type: ignore

# Initialize DynamoDB resource and specify table name
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('MotivationalQuotes')

# Load quotes from a JSON file
def load_quotes_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file) 

# Function to upload quotes to DynamoDB
def upload_quotes(quotes):
    for quote in quotes:
        try:
            # Ensure each quote has a unique ID (e.g., UUID or auto-increment)
            response = table.put_item(Item=quote)
            print(f"Uploaded: {quote['quote_id']}")
        except ClientError as e:
            print(f"Error uploading quote: {e.response['Error']['Message']}")

if __name__ == "__main__":
    quotes = load_quotes_from_json("quotes.json")
    upload_quotes(quotes)