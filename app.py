import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS # Ensure this is imported
from models import db, Lead, CommunicationLog
from ai_agent import analyze_lead

load_dotenv()

app = Flask(__name__)
# 1. The Global CORS Fix: Allow everything for the hackathon
CORS(app, resources={r"/*": {"origins": "*"}}) 

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# 2. Add 'OPTIONS' to the allowed methods here:
@app.route('/api/lead', methods=['POST', 'OPTIONS'])
def receive_lead():
    # 3. Explicitly handle the preflight check
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    data = request.json
    
    if not data or not data.get('name') or not data.get('contact_info'):
        return jsonify({'error': 'Missing required fields'}), 400

    # Extract data
    source = data.get('source', 'Website')
    name = data.get('name')
    contact_info = data.get('contact_info')
    raw_data = str(data)

    # 1. Trigger the AI Researcher Agent
    ai_score, ai_summary = analyze_lead(name, contact_info, source, raw_data)

    # 2. Save to database with AI insights
    new_lead = Lead(
        source=source,
        name=name,
        contact_info=contact_info,
        raw_data=raw_data,
        ai_score=ai_score,
        ai_summary=ai_summary
    )
    db.session.add(new_lead)
    db.session.commit()

    # 3. Notify the rep via Telegram
    send_telegram_notification(new_lead)

    return jsonify({'message': 'Lead processed and scored successfully', 'lead_id': new_lead.id}), 201
# ==========================================
# 2. TELEGRAM NOTIFICATION HELPER (For P1)
# ==========================================
def send_telegram_notification(lead):
    """Sends the lead summary and Approve/Reject buttons to the rep."""
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    score_emoji = "🔥" if lead.ai_score == "High" else "⚡" if lead.ai_score == "Medium" else "🧊"
    
    text = f"🚨 *New Lead Alert*\n\n" \
           f"*Name:* {lead.name}\n" \
           f"*Source:* {lead.source}\n" \
           f"*Contact:* {lead.contact_info}\n\n" \
           f"🤖 *AI Analysis:*\n" \
           f"*Score:* {lead.ai_score} {score_emoji}\n" \
           f"*Summary:* _{lead.ai_summary}_"

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