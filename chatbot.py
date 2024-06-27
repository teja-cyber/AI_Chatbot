from sentence_transformers import util
import json

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
