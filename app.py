# app.py
import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from models import db, Lead, CommunicationLog

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db.init_app(app)

# Create tables before first request
with app.app_context():
    db.create_all()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# ==========================================
# 1. LEAD INGESTION ENDPOINT (For P2)
# ==========================================
@app.route('/api/lead', methods=['POST'])
def receive_lead():
    """Endpoint to catch leads from the React frontend or simulated webhooks."""
    data = request.json
    
    if not data or not data.get('name') or not data.get('contact_info'):
        return jsonify({'error': 'Missing required fields'}), 400

    # Save to database
    new_lead = Lead(
        source=data.get('source', 'Website'),
        name=data.get('name'),
        contact_info=data.get('contact_info'),
        raw_data=str(data)
    )
    db.session.add(new_lead)
    db.session.commit()

    # TODO in Phase 2: Trigger OpenAI Researcher Agent here
    # For now, we will simulate passing it to Telegram
    
    send_telegram_notification(new_lead)

    return jsonify({'message': 'Lead received successfully', 'lead_id': new_lead.id}), 201

# ==========================================
# 2. TELEGRAM NOTIFICATION HELPER (For P1)
# ==========================================
def send_telegram_notification(lead):
    """Sends the lead summary and Approve/Reject buttons to the rep."""
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    text = f"🚨 *New Lead Alert*\n\n" \
           f"*Name:* {lead.name}\n" \
           f"*Source:* {lead.source}\n" \
           f"*Contact:* {lead.contact_info}\n\n" \
           f"_AI Score and Summary pending Phase 2..._"

    # Inline Keyboard for Approve/Reject
    reply_markup = {
        "inline_keyboard": [[
            {"text": "✅ Approve", "callback_data": f"approve_{lead.id}"},
            {"text": "❌ Reject", "callback_data": f"reject_{lead.id}"}
        ]]
    }

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": reply_markup
    }
    
    requests.post(url, json=payload)

# ==========================================
# 3. TELEGRAM WEBHOOK (For P1)
# ==========================================
@app.route('/webhook/telegram', methods=['POST'])
def telegram_webhook():
    """Catches button clicks (Approve/Reject) from Telegram."""
    data = request.json
    
    if 'callback_query' in data:
        callback_query = data['callback_query']
        callback_data = callback_query['data']
        message_id = callback_query['message']['message_id']
        chat_id = callback_query['message']['chat']['id']
        
        # Parse the action and lead ID
        action, lead_id = callback_data.split('_')
        lead = Lead.query.get(lead_id)

        if lead:
            if action == 'approve':
                lead.status = 'Approved'
                # TODO in Phase 3: Trigger multi-modal outreach here
                response_text = f"Lead {lead.name} Approved. Initiating outreach..."
            elif action == 'reject':
                lead.status = 'Rejected'
                response_text = f"Lead {lead.name} Rejected."
            
            db.session.commit()

            # Update the original Telegram message to show the decision
            edit_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageText"
            requests.post(edit_url, json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": response_text
            })

    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)