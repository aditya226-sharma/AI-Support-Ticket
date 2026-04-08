import boto3
import json
import os
from dotenv import load_dotenv
from models import Priority, Category

load_dotenv()

_bedrock = None


def get_bedrock_client():
    global _bedrock
    if _bedrock is None:
        _bedrock = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
    return _bedrock


def invoke_model(prompt: str) -> str:
    model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-text-express-v1")
    body = json.dumps({
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 512,
            "temperature": 0.3,
            "topP": 0.9,
        },
    })
    try:
        response = get_bedrock_client().invoke_model(modelId=model_id, body=body)
        result = json.loads(response["body"].read())
        return result["results"][0]["outputText"].strip()
    except Exception as e:
        return f"AI service unavailable: {str(e)}"


def classify_ticket(subject: str, description: str) -> dict:
    prompt = f"""Analyze this customer support ticket and respond ONLY with a JSON object.

Subject: {subject}
Description: {description}

Respond with exactly this JSON format (no extra text):
{{
  "category": "<one of: billing, technical, account, shipping, general>",
  "priority": "<one of: low, medium, high, critical>",
  "confidence": <float between 0.0 and 1.0>
}}"""

    raw = invoke_model(prompt)
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        data = json.loads(raw[start:end])
        return {
            "category": Category(data.get("category", "general")),
            "priority": Priority(data.get("priority", "medium")),
            "confidence": float(data.get("confidence", 0.7)),
        }
    except Exception:
        return {"category": Category.general, "priority": Priority.medium, "confidence": 0.5}


def generate_resolution(subject: str, description: str, category: str) -> str:
    prompt = f"""You are a helpful customer support AI. Provide a clear, concise resolution for this ticket.

Category: {category}
Subject: {subject}
Issue: {description}

Write a professional response (2-4 sentences) that directly addresses the customer's issue with actionable steps."""

    return invoke_model(prompt)


def analyze_ticket(subject: str, description: str) -> dict:
    classification = classify_ticket(subject, description)
    resolution = generate_resolution(subject, description, classification["category"])
    return {**classification, "ai_resolution": resolution}
