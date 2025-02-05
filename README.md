# Motivational Quotes API

A **serverless API** that serves motivational quotes and provides functionalities such as retrieving all quotes, filtering and searching by parameters (author, year, category, etc.), and generating AI-powered explanations for quotes using OpenAI’s GPT models. This API is built using **AWS Lambda**, **API Gateway**, and **DynamoDB**, and is deployed using the **Serverless Framework**.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Endpoints](#endpoints)
- [Installation](#installation)
- [Deployment](#deployment)
- [Usage](#usage)
- [Development](#development)
- [Future Enhancements](#future-enhancements)
- [License](#license)

## Overview

The Motivational Quotes API provides a scalable and accessible way to deliver daily motivational quotes. It supports filtering, searching, and generating AI-powered explanations for quotes. The API is intended to be used as a backend service for mobile apps, websites, or any application that requires daily inspirational content.

## Features

- **Retrieve Quotes:** Fetch all motivational quotes from a DynamoDB table.
- **Filter & Search:** Filter quotes by year, author, or category, and search by keywords.
- **AI Explanations:** Generate human-like explanations for quotes using OpenAI's GPT models.
- **Serverless Architecture:** Built using AWS Lambda and API Gateway for a scalable and cost-effective solution.
- **Easy Deployment:** Managed via the Serverless Framework for rapid deployment and updates.

## Architecture

- **AWS Lambda:** Hosts Python functions that implement your API endpoints.
- **API Gateway:** Exposes your Lambda functions as HTTP endpoints.
- **DynamoDB:** Stores motivational quotes with fields such as `quote_id`, `quote_text`, `author`, `year`, and optionally `category`.
- **OpenAI API:** Powers the AI explanation functionality.
- **Serverless Framework:** Handles the packaging, deployment, and management of the API and its resources.

## Endpoints

The deployed API provides the following endpoints:

- **GET `/quotes`**  
  Retrieves all motivational quotes.

- **GET `/quotes/{year}`**  
  Retrieves quotes for a specified year.  
  *Path Parameter:* `year`

- **POST `/quotes/explanation`**  
  Generates an AI-powered explanation for a given quote.  
  **Request Body (JSON):**
  ```json
  {
    "quote_id": "1"
  }
GET /quotes/search
Searches quotes based on a keyword.
Query Parameter: ?keyword=your_keyword

GET /quotes/filter
Filters quotes by category.
Query Parameter: ?category=your_category

GET /quotes/author
Filters quotes by author.
Query Parameter: ?author=author_name

GET /quotes/year
Filters quotes by year (alternative method using a query parameter).
Query Parameter: ?year=YYYY

Installation
Prerequisites
Python 3.8 or higher
AWS CLI configured with your AWS credentials
Node.js (required by the Serverless Framework)
Serverless Framework installed globally
Clone the Repository
bash
Copy
Edit
git clone https://github.com/64eyes/motivational-quotes-api.git
cd motivational-quotes-api
Set Up Python Virtual Environment
bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate  # For Windows use: venv\Scripts\activate
Install Python Dependencies
If you have a requirements.txt:

bash
Copy
Edit
pip install -r requirements.txt
If you don't, generate one from your current environment:

bash
Copy
Edit
pip freeze > requirements.txt
Deployment
This project is deployed using the Serverless Framework.

Configure Environment Variables
In your serverless.yml, add your environment variables. For example:

yaml
Copy
Edit
provider:
  name: aws
  runtime: python3.12
  region: us-east-1
  environment:
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}
Ensure that you have the OPENAI_API_KEY set in your local environment before deploying:

bash
Copy
Edit
export OPENAI_API_KEY="your_openai_api_key_here"
Deploy the Service
Run the following command from the root of your project:

bash
Copy
Edit
serverless deploy
After deployment, the command line output will include your live API endpoints.

Usage
You can test your API endpoints using tools like Postman or curl.

Examples
Retrieve All Quotes:

bash
Copy
Edit
curl -X GET https://<your-api-id>.execute-api.us-east-1.amazonaws.com/dev/quotes
Filter by Author:

bash
Copy
Edit
curl -X GET "https://<your-api-id>.execute-api.us-east-1.amazonaws.com/dev/quotes/author?author=Einstein"
Filter by Year:

bash
Copy
Edit
curl -X GET "https://<your-api-id>.execute-api.us-east-1.amazonaws.com/dev/quotes/year?year=2020"
Search by Keyword:

bash
Copy
Edit
curl -X GET "https://<your-api-id>.execute-api.us-east-1.amazonaws.com/dev/quotes/search?keyword=inspire"
Generate Quote Explanation:

bash
Copy
Edit
curl -X POST https://<your-api-id>.execute-api.us-east-1.amazonaws.com/dev/quotes/explanation \
     -H "Content-Type: application/json" \
     -d '{"quote_id": "1"}'
Replace <your-api-id> with the actual API Gateway ID provided upon deployment.

Development
Local Testing
Invoke Functions Locally:

bash
Copy
Edit
serverless invoke local --function getQuotes
View Logs:

bash
Copy
Edit
serverless logs -f getQuotes --tail
Version Control
Make sure to commit your changes and push to GitHub:

bash
Copy
Edit
git add .
git commit -m "Initial commit - Motivational Quotes API"
git push origin main
Future Enhancements
User Authentication: Add endpoints for user registration and login.
Daily Quote Notifications: Implement scheduled notifications via email or SMS.
Advanced Filtering: Enhance filtering options and support complex queries.
Analytics: Track API usage and identify popular quotes.
CI/CD Pipeline: Set up GitHub Actions for continuous integration and automated deployments.
Additional Features: Explore quote submissions, social sharing, and personalization.
License
This project is licensed under the MIT License.