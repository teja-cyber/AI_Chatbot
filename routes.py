from flask import request, jsonify, render_template, redirect, url_for, session
from models import UserModel, ChatbotModel
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import json
from sentence_transformers import util

user_model = UserModel(Config.USER_DATA_FILE)
chatbot_model = ChatbotModel()

def setup_routes(app):

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
            user_password_hash = user_model.users.get(username)

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

            if username in user_model.users:
                return render_template("register.html", error="Username already exists")

            user_model.users[username] = generate_password_hash(password)
            user_model.save_users()
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

    @app.route("/chatbot", methods=["POST"])
    def chatbot_response():
        try:
            data = request.get_json(force=True)
            user_input = data.get("input")

            # Fetch data from local response.json file
            local_data = fetch_from_local(Config.RESPONSE_FILE)
            plans = local_data.get('plans', [])
            predefined_responses = local_data.get('responses', [])

            response_text = handle_response(user_input, predefined_responses, chatbot_model)

            return jsonify({"response": response_text, "healthcare_plans": plans})

        except Exception as e:
            return jsonify({"error": str(e)}), 400

def fetch_from_local(response_file):
    try:
        with open(response_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File '{response_file}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{response_file}': {e}")
    return {"plans": [], "responses": []}

def handle_response(user_input, predefined_responses, chatbot_model):
    user_embedding = chatbot_model.sentence_model.encode(user_input, convert_to_tensor=True)
    predefined_texts = [response['input'] for response in predefined_responses]
    predefined_embeddings = chatbot_model.sentence_model.encode(predefined_texts, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(user_embedding, predefined_embeddings)
    best_match_idx = similarities.argmax().item()
    best_similarity_score = similarities[0, best_match_idx].item()

    if best_similarity_score > 0.7:  # Adjust the threshold based on your needs
        response_text = predefined_responses[best_match_idx]['response']
    else:
        response_text = chatbot_model.generate_response(user_input)

    if not response_text:
        response_text = "I'm sorry, I didn't understand that. Could you please rephrase?"

    return response_text
