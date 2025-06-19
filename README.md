# Motivational Quotes API

A **cloud-native, AI-powered, serverless API** for motivational quotes. Features include adding/searching quotes, semantic search, personalized recommendations, user favorites/history, and more. Built with AWS Lambda, API Gateway, DynamoDB, OpenAI, FAISS, Flask, and Cognito. Deployable via the Serverless Framework.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Endpoints](#endpoints)
- [Authentication (Cognito)](#authentication-cognito)
- [Installation](#installation)
- [Deployment](#deployment)
- [Usage & Examples](#usage--examples)
- [FAISS Microservice](#faiss-microservice)
- [Testing](#testing)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Overview

This API delivers daily motivational quotes, supports semantic search and AI-powered recommendations, and enables user-specific features like favorites and history. It is designed for mobile/web apps or any service needing inspirational content with modern AI capabilities.

---

## Architecture

- **AWS Lambda + API Gateway:** Serverless REST API endpoints
- **DynamoDB:** NoSQL storage for quotes, favorites, and history
- **OpenAI API:** Embedding and personalization
- **FAISS (Flask Microservice on EC2):** Semantic vector search
- **Amazon Cognito:** User authentication (JWT)
- **Serverless Framework:** Deployment automation

---

## Features

- Add new motivational quotes (single or batch)
- Semantic search using natural language (OpenAI + FAISS)
- Personalized quote recommendations
- User favorites and history tracking
- AI-powered quote explanations
- Secure endpoints with Cognito authentication
- Scalable, serverless, and cloud-native

---

## Endpoints

### **Quotes**

- `POST /quotes` — Add a new quote (auth required)
- `POST /quotes/batch` — Batch upload quotes (auth required)
- `GET /quotes` — Retrieve all quotes
- `GET /quotes/{year}` — Retrieve quotes by year
- `GET /quotes/search?keyword=...` — Keyword search
- `POST /quotes/search` — Semantic search (auth required)
- `POST /quotes/explanation` — AI explanation for a quote

### **Personalization**

- `POST /quotes/recommend` — Personalized recommendations (auth required)

### **Favorites**

- `POST /quotes/{id}/favorite` — Add to favorites (auth required)
- `DELETE /quotes/{id}/favorite` — Remove from favorites (auth required)
- `GET /user/favorites` — List user favorites (auth required)

### **History**

- `POST /quotes/{id}/viewed` — Add to user history (auth required)
- `GET /user/history` — List user history (auth required)

---

## Authentication (Cognito)

Most endpoints require a valid **JWT** from Amazon Cognito.

### **Setup**

1. Create a Cognito User Pool and App Client (no secret).
2. Note your User Pool ID, App Client ID, and Pool ARN.
3. Update `serverless.yml` with your Cognito Pool ARN.

### **Getting a JWT**

- Sign up/sign in via Cognito Hosted UI or AWS CLI/SDK.
- Use the returned `id_token` or `access_token` as your Bearer token.

### **Example (with curl):**

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/dev/quotes \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"quote_text": "Stay positive!", "author": "AI", "year": 2024}'
```

---

## Installation

**Prerequisites:**

- Python 3.8+
- Node.js (for Serverless Framework)
- AWS CLI configured
- OpenAI API key

**Setup:**

```bash
# Clone and enter project
git clone <repo-url>
cd motivational-quotes-api

# Python venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
npm install
```

---

## Deployment

1. **Set environment variables:**
   - `OPENAI_API_KEY` (required)
   - `FAISS_SERVICE_URL` (default: http://localhost:5000)
2. **Update Cognito ARN in `serverless.yml`.**
3. **Deploy:**

```bash
serverless deploy
```

4. **Deploy FAISS microservice:**
   - See [FAISS Microservice](#faiss-microservice) below.

---

## Usage & Examples

### **Add a Quote**

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/dev/quotes \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"quote_text": "Stay positive!", "author": "AI", "year": 2024}'
```

### **Batch Upload**

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/dev/quotes/batch \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"quotes": [{"quote_text": "A", "author": "B", "year": 2020}, ...]}'
```

### **Semantic Search**

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/dev/quotes/search \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"query": "overcoming failure"}'
```

### **Personalized Recommendations**

```bash
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/dev/quotes/recommend \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"profile": "I like quotes about resilience and growth."}'
```

### **Favorites**

```bash
# Add to favorites
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/dev/quotes/<id>/favorite -H "Authorization: Bearer <JWT>"
# Remove from favorites
curl -X DELETE https://<api-id>.execute-api.<region>.amazonaws.com/dev/quotes/<id>/favorite -H "Authorization: Bearer <JWT>"
# List favorites
curl -X GET https://<api-id>.execute-api.<region>.amazonaws.com/dev/user/favorites -H "Authorization: Bearer <JWT>"
```

### **History**

```bash
# Add to history
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/dev/quotes/<id>/viewed -H "Authorization: Bearer <JWT>"
# List history
curl -X GET https://<api-id>.execute-api.<region>.amazonaws.com/dev/user/history -H "Authorization: Bearer <JWT>"
```

---

## FAISS Microservice

- **Location:** `faiss_service/app.py`
- **Purpose:** Stores and searches OpenAI embeddings for semantic search and recommendations.
- **Endpoints:**
  - `POST /add_embedding` — Add/update quote embedding
  - `POST /search` — Semantic search
- **Deployment:**
  - Deploy on EC2 or any server with Python, Flask, and FAISS installed.
  - Set `FAISS_SERVICE_URL` in Lambda environment to point to this service.

---

## Testing

- Use Postman or curl for endpoint testing (see above examples).
- Ensure you include a valid Cognito JWT for protected endpoints.
- Check CloudWatch logs for Lambda debugging.
- Test FAISS microservice independently with sample embeddings if needed.

---

## Future Enhancements

- Scheduled "Quote of the Day" notifications (email/SMS)
- Admin/moderation tools
- Analytics and usage dashboards
- CI/CD pipeline
- API documentation (OpenAPI/Swagger)

---

## License

This project is licensed under the MIT License.
