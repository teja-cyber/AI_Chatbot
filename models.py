import json
from werkzeug.security import generate_password_hash, check_password_hash
from transformers import pipeline
from sentence_transformers import SentenceTransformer

class UserModel:
    def __init__(self, user_data_file):
        self.user_data_file = user_data_file
        self.users = self.load_users()

    def load_users(self):
        users = {}
        try:
            with open(self.user_data_file, 'r') as file:
                users = json.load(file)
        except FileNotFoundError:
            print(f"File '{self.user_data_file}' not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from '{self.user_data_file}': {e}")
        return users

    def save_users(self):
        with open(self.user_data_file, 'w') as file:
            json.dump(self.users, file)

class ChatbotModel:
    def __init__(self):
        self.chatbot = pipeline('text-generation', model='gpt2', truncation=True)
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

    def generate_response(self, user_input, max_length=150, num_return_sequences=1, temperature=0.7, top_k=50, top_p=0.95):
        response = self.chatbot(
            user_input, 
            max_length=max_length, 
            num_return_sequences=num_return_sequences, 
            temperature=temperature, 
            top_k=top_k, 
            top_p=top_p
        )
        return response[0]['generated_text'].strip()
