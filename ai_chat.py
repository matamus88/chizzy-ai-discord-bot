import requests
import os
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv('HF_API_KEY', '')
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

def query_ai(prompt, max_tokens=512):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": f"<s>[INST] {prompt} [/INST]",
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 0.7,
            "do_sample": True
        }
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                text = result[0].get('generated_text', '')
                if '[/INST]' in text:
                    text = text.split('[/INST]')[-1].strip()
                return text[:2000] if text else 'No response generated.'
        return 'AI service unavailable. Try again later.'
    except:
        return 'Something went wrong. Please try again.'

def get_ai_response(prompt):
    return query_ai(f"You are a helpful AI assistant. Answer clearly and concisely.\n\nUser: {prompt}")

def get_code_help(code):
    return query_ai(f"You are an expert programmer. Help with this code or question:\n\n{code}", max_tokens=1024)

def get_summarize(text):
    return query_ai(f"Summarize the following text in 2-3 sentences:\n\n{text}")

def get_translate(text, language):
    return query_ai(f"Translate the following text to {language}. Only output the translation:\n\n{text}")

def get_premium_response(prompt):
    return query_ai(f"You are Chizzy AI, an advanced, helpful, and friendly AI assistant. You give detailed, well-formatted responses. You use emoji where appropriate.\n\nUser: {prompt}", max_tokens=1024)
