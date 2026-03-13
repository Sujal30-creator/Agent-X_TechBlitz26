import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize the OpenAI client using the key from your .env file
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def analyze_lead(name, contact_info, source, raw_data):
    """
    Acts as a sales researcher agent to score and summarize a lead.
    """
    system_prompt = """
    You are an elite sales researcher and lead qualifier. 
    Analyze the provided lead information and determine their priority.
    
    Output your response STRICTLY as a JSON object with two keys:
    1. "score": Must be exactly "High", "Medium", or "Low".
    2. "summary": A brief, punchy 2-sentence summary of why they got this score and what the sales rep should focus on.
    """

    user_prompt = f"""
    Lead Name: {name}
    Contact Info: {contact_info}
    Source: {source}
    Additional Data: {raw_data}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # You can upgrade to gpt-4 or gpt-4o-mini if preferred
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={ "type": "json_object" }, # Forces OpenAI to return valid JSON
            temperature=0.3 # Keep it low for consistent formatting
        )
        
        # Parse the JSON string returned by OpenAI
        result = json.loads(response.choices[0].message.content)
        return result.get("score", "Pending"), result.get("summary", "Analysis failed.")
        
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return "Pending", "AI analysis temporarily unavailable."