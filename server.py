from flask import Flask, request, jsonify, render_template
import os
from mtranslate import translate
from twilio.rest import Client

account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')

client = Client(os.getenv('ACCOUNT_SID'), os.getenv('AUTH_TOKEN'))

def send_whatsapp_message(to_number, message):
    try:
        message = client.messages.create(
            from_=twilio_whatsapp_number,
            body=message,
            to=f'whatsapp:{to_number}'  # Example: whatsapp:+8801XXXXXXXXX
        )
        print(f"WhatsApp message sent! SID: {message.sid}")
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")

app = Flask(__name__)

# Load remedies in English (base language)
remedies = {}

remedy_files = {
    "india": "remedies.txt",
    "korea": "korea.txt",
    "kenya": "africa.txt"
}

def load_remedies(file_name):
    """Load remedies from the specified file."""
    remedies = {}
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as file:
            for line in file:
                if ":" in line:
                    symptom, remedy = line.strip().split(":", 1)
                    remedies[symptom.lower()] = remedy.strip()
    return remedies

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/get_remedy", methods=["POST"])
def get_remedy():
    """Translate symptom to English, find remedy, and translate remedy back to user language."""
    data = request.get_json()

    if data is None:
        return jsonify({"error": "Invalid JSON format."}), 400

    symptom = data.get("symptom", "").strip().lower()
    language = data.get("language", "en").strip().lower()  # Default to English
    location = data.get("location", "india").strip().lower()  # Default to India
    
    if not symptom:
        return jsonify({"error": "Please enter a symptom."})
    
    # Determine the correct remedy file based on location
    remedy_file = remedy_files.get(location, "remedies.txt")
    remedies = load_remedies(remedy_file)
# Step 1: Translate symptom to English
    translated_symptom = symptom  # If the input is already in English
    if language != "en":
        try:
            # Translate the symptom to English (from the given language)
            translated_symptom = translate(symptom, to_language="en", from_language=language)
            print(f"Translated '{symptom}' to English: {translated_symptom}")  # Debugging
        except Exception as e:
            return jsonify({"error": "Symptom translation error: " + str(e)})

    # Step 3: Normalize and try exact + partial match
    normalized_symptom = translated_symptom.lower().strip()
    remedy = remedies.get(normalized_symptom)

    # Fallback: Try fuzzy/partial matching
    if not remedy:
        for key in remedies:
            if normalized_symptom in key:
                remedy = remedies[key]
                break
    if not remedy:
        remedy="No remedy found for the given symptom."
 # Step 4: Translate remedy back to the requested language
    if language != "en":
        try:
            translated_remedy = translate(remedy, to_language=language, from_language="en")
            print(f"Translated remedy to {language}: {translated_remedy}")  # Debugging
        except Exception as e:
            return jsonify({"error": "Remedy translation error: " + str(e)})
    else:
        translated_remedy = remedy  # Keep English if requested
    
    # NEW: Send WhatsApp Message if number provided
    user_whatsapp_number = data.get("phone")  # You must send this from frontend
    if user_whatsapp_number:
        send_whatsapp_message(user_whatsapp_number, translated_remedy)


    return jsonify({"remedy": translated_remedy})
if __name__ == "__main__":
    app.run(debug=True)

