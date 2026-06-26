from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Load IPC database from JSON file
def load_ipc_database():
    """Load IPC sections from JSON file"""
    db_path = os.path.join(os.path.dirname(__file__), 'ipc_database.json')
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('sections', [])
    except FileNotFoundError:
        print("Warning: ipc_database.json not found!")
        return []

# Load lawyers database from JSON file
def load_lawyers_database():
    """Load lawyers from JSON file"""
    db_path = os.path.join(os.path.dirname(__file__), 'lawyers_database.json')
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('lawyers', [])
    except FileNotFoundError:
        print("Warning: lawyers_database.json not found!")
        return []

# Load databases at startup
ipc_database = load_ipc_database()
lawyers_database = load_lawyers_database()

# Load contacts database from JSON file
def load_contacts():
    db_path = os.path.join(os.path.dirname(__file__), 'contacts.json')
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('contacts', [])
    except FileNotFoundError:
        return []

def save_contacts(contacts):
    db_path = os.path.join(os.path.dirname(__file__), 'contacts.json')
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump({'contacts': contacts}, f, ensure_ascii=False, indent=2)

# Load contacts at startup
contacts_database = load_contacts()

def search_ipc(query):
    """Search IPC sections by keywords or section number"""
    query_lower = query.lower()
    results = []
    
    for section in ipc_database:
        # Search by section number
        if query_lower in section["section"].lower():
            results.append(section)
        # Search by keywords
        elif any(keyword in query_lower for keyword in section["keywords"]):
            results.append(section)
    
    return results

def law_advisor_bot(question, language="english"):
    """Main chatbot function with language support"""
    if not question.strip():
        if language == "hindi":
            return "कृपया भारतीय कानून से संबंधित कोई कानूनी प्रश्न पूछें।"
        elif language == "marathi":
            return "कृपया भारतीय कायद्याशी संबंधित कोई कानूनी प्रश्न विचारा."
        return "Please ask a legal question related to Indian law."
    
    # Validate language
    if language not in ["english", "hindi", "marathi"]:
        language = "english"
    
    # Search for relevant IPC sections
    results = search_ipc(question)
    
    if results:
        # Format response with found sections
        if language == "english":
            response = "📚 Based on your question, here are the relevant IPC sections:\n\n"
        elif language == "hindi":
            response = "📚 आपके प्रश्न के आधार पर, यहां प्रासंगिक IPC खंड हैं:\n\n"
        else:  # marathi
            response = "📚 तुमच्या प्रश्नाच्या आधारे, येथे संबंधित IPC विभाग आहेत:\n\n"
        
        for i, section in enumerate(results[:3], 1):
            sec_num = section['section']
            title = section['title'].get(language, section['title']['english']) if isinstance(section['title'], dict) else section['title']
            meaning = section['meaning'].get(language, section['meaning']['english']) if isinstance(section['meaning'], dict) else section['meaning']
            punishment = section['punishment'].get(language, section['punishment']['english']) if isinstance(section['punishment'], dict) else section['punishment']
            
            response += f"⚖️ {sec_num}: {title}\n"
            response += f"📝 {meaning}\n"
            response += f"⏰ {punishment}\n\n"
        return response
    else:
        if language == "english":
            return "I couldn't find relevant IPC sections. Try asking about: theft, assault, harassment, fraud, dowry, robbery, etc."
        elif language == "hindi":
            return "मुझे प्रासंगिक IPC खंड नहीं मिले। चोरी, हमला, उत्पीड़न, धोखाधड़ी, दहेज आदि के बारे में पूछने का प्रयास करें।"
        else:  # marathi
            return "मला संबंधित IPC विभाग सापडले नाहीत. चोरी, हल्ला, छळ, फसवणूक, दहेज इत्यादी बद्दल विचारण्याचा प्रयत्न करा."

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "🇮🇳 AI Law Advisor Bot - Multilingual IPC Database",
        "languages": ["english", "hindi", "marathi"],
        "info": "Send POST requests to /chat with your legal question",
        "database": f"Contains {len(ipc_database)} IPC sections with 3 languages",
        "example": {
            "url": "/chat",
            "method": "POST",
            "data": {"question": "What is theft?", "language": "english"}
        }
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question", "")
    language = data.get("language", "english")
    answer = law_advisor_bot(question, language)
    return jsonify({"answer": answer, "language": language})

@app.route("/sections", methods=["GET"])
def get_sections():
    """Get all IPC sections"""
    language = request.args.get('language', 'english')
    return jsonify({
        "sections": ipc_database, 
        "total": len(ipc_database),
        "language": language
    })

@app.route("/search", methods=["POST"])
def search():
    """Search IPC sections"""
    data = request.get_json()
    query = data.get("query", "")
    language = data.get("language", "english")
    results = search_ipc(query)
    return jsonify({
        "query": query, 
        "results": results, 
        "count": len(results),
        "language": language
    })

@app.route("/languages", methods=["GET"])
def get_languages():
    """Get available languages"""
    return jsonify({"languages": ["english", "hindi", "marathi"]})

@app.route("/lawyers", methods=["GET"])
def get_lawyers():
    """Get all lawyers"""
    specialization = request.args.get('specialization', '')
    if specialization:
        results = []
        for lawyer in lawyers_database:
            if any(spec.lower() == specialization.lower() for spec in lawyer.get('specialization', [])):
                results.append(lawyer)
        return jsonify({"lawyers": results, "count": len(results)})
    return jsonify({"lawyers": lawyers_database, "total": len(lawyers_database)})

@app.route("/lawyers/<int:lawyer_id>", methods=["GET"])
def get_lawyer_details(lawyer_id):
    """Get specific lawyer details"""
    for lawyer in lawyers_database:
        if lawyer['id'] == lawyer_id:
            return jsonify(lawyer)
    return jsonify({"error": "Lawyer not found"}), 404

@app.route("/lawyers/search", methods=["POST"])
def search_lawyers():
    """Search lawyers by specialization"""
    data = request.get_json()
    specialization = data.get('specialization', '')
    if not specialization:
        return jsonify({"error": "Please provide specialization"}), 400
    
    results = []
    for lawyer in lawyers_database:
        if any(spec.lower() in specialization.lower() for spec in lawyer.get('specialization', [])):
            results.append(lawyer)
    return jsonify({"results": results, "count": len(results)})

@app.route("/specializations", methods=["GET"])
def get_specializations():
    """Get all available specializations"""
    specs = set()
    for lawyer in lawyers_database:
        specs.update(lawyer.get('specialization', []))
    return jsonify({"specializations": list(specs)})


@app.route('/contact', methods=['POST'])
def create_contact():
    """Create a contact/request to a lawyer and save it"""
    data = request.get_json() or {}
    required = ['lawyer_name', 'specialization', 'client_name', 'client_email', 'client_phone', 'message']
    if not all(k in data and str(data.get(k)).strip() for k in required):
        return jsonify({'error': 'Missing required fields'}), 400

    from datetime import datetime
    contact = {
        'id': len(contacts_database) + 1,
        'lawyer_name': data.get('lawyer_name'),
        'specialization': data.get('specialization'),
        'client_name': data.get('client_name'),
        'client_email': data.get('client_email'),
        'client_phone': data.get('client_phone'),
        'message': data.get('message'),
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'status': 'sent'
    }
    contacts_database.append(contact)
    try:
        save_contacts(contacts_database)
    except Exception as e:
        return jsonify({'error': 'Failed to save contact', 'details': str(e)}), 500

    return jsonify({'success': True, 'contact': contact}), 201


@app.route('/contacts', methods=['GET'])
def list_contacts():
    """Return all saved contact requests (optionally filter by client_email)"""
    client_email = request.args.get('client_email', '')
    lawyer_name = request.args.get('lawyer_name', '')
    results = contacts_database
    if client_email:
        results = [c for c in results if c.get('client_email', '').lower() == client_email.lower()]
    if lawyer_name:
        results = [c for c in results if lawyer_name.lower() in c.get('lawyer_name', '').lower()]
    return jsonify({'contacts': results, 'count': len(results)})

if __name__ == "__main__":
    print(f"✅ Loaded {len(ipc_database)} IPC sections")
    print(f"✅ Loaded {len(lawyers_database)} Lawyer profiles")
    print("🌐 Available languages: English, Hindi, Marathi")
    app.run(debug=True)
