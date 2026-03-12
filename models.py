# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False) # e.g., Website, Instagram, WhatsApp
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(150), nullable=False)
    raw_data = db.Column(db.Text, nullable=True) 
    
    # Agent Insights
    ai_score = db.Column(db.String(20), default='Pending') # High, Medium, Low
    ai_summary = db.Column(db.Text, nullable=True)
    
    # Pipeline Status
    status = db.Column(db.String(50), default='New') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CommunicationLog(db.Model):
    __tablename__ = 'communication_logs'
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=False)
    channel = db.Column(db.String(50), nullable=False) 
    message_direction = db.Column(db.String(20), nullable=False) 
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)