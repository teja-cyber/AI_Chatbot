import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    USER_DATA_FILE = os.getenv('USER_DATA_FILE', 'C:\\Users\\TLimbachiya\\Documents\\Chrome_download\\AI_chatbot\\users.json')
    RESPONSE_FILE = os.getenv('RESPONSE_FILE', 'response.json')
