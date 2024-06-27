from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Path to the user data file
USER_DATA_FILE = 'C:\\Users\\TLimbachiya\\Documents\\Chrome_download\\AI_chatbot\\users.json'
RESPONSE_FILE = 'response.json'

# Load the model and tokenizer
chatbot = pipeline('text-generation', model='gpt2', truncation=True)
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

def load_users():
    users = {}
    try:
        with open(USER_DATA_FILE, 'r') as file:
            users = json.load(file)
    except FileNotFoundError:
        print(f"File '{USER_DATA_FILE}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{USER_DATA_FILE}': {e}")
    return users

def save_users(users):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file)

users = load_users()

@app.route("/")
def index():
    if "username" in session:
        username = session["username"]
        welcome_message = f"Welcome {username}! I'm your personal assistant bot. I'm here to provide information and help with any questions you have. Feel free to ask me anything!"
        return render_template("index.html", username=username, welcome_message=welcome_message)
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_password_hash = users.get(username)
        
        if user_password_hash and check_password_hash(user_password_hash, password):
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid username or password")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if username in users:
            return render_template("register.html", error="Username already exists")
        
        users[username] = generate_password_hash(password)
        save_users(users)
        return redirect(url_for("register_confirmation", username=username))
    
    return render_template("register.html")

@app.route("/register/confirmation")
def register_confirmation():
    username = request.args.get("username")
    return render_template("register_confirmation.html", username=username)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

def fetch_from_local():
    try:
        with open(RESPONSE_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("File 'response.json' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from 'response.json': {e}")
    return {"plans": [], "responses": []}

@app.route("/chatbot", methods=["POST"])
def chatbot_response():
    try:
        data = request.get_json(force=True)
        user_input = data.get("input")
        
        # Fetch data from local response.json file
        local_data = fetch_from_local()
        plans = local_data.get('plans', [])
        predefined_responses = local_data.get('responses', [])
        
        # Check for predefined responses based on similarity
        user_embedding = sentence_model.encode(user_input, convert_to_tensor=True)
        predefined_texts = [response['input'] for response in predefined_responses]
        predefined_embeddings = sentence_model.encode(predefined_texts, convert_to_tensor=True)
        similarities = util.pytorch_cos_sim(user_embedding, predefined_embeddings)
        best_match_idx = similarities.argmax().item()
        best_similarity_score = similarities[0, best_match_idx].item()
        
        if best_similarity_score > 0.7:  # Adjust the threshold based on your needs
            response_text = predefined_responses[best_match_idx]['response']
        else:
            response_text = chatbot(user_input, max_length=150, num_return_sequences=1)[0]['generated_text'].strip()
        
        # Default response if no suitable response found
        if not response_text:
            response_text = "I'm sorry, I didn't understand that. Could you please rephrase?"

        return jsonify({"response": response_text, "healthcare_plans": plans})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
