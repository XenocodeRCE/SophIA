"""
Interface Web pour SophIA
Interface moderne avec Flask pour conversation philosophique
"""

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import os
import sys
from datetime import datetime
from typing import Dict, Any
import logging
import json
import uuid

# Ajouter le path parent pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from sophia.core.sophia_hybrid import HybridSophIA

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sophia_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instance globale de SophIA
sophia_instance = None
active_sessions = {}

def get_sophia():
    """Récupère ou crée une instance de SophIA"""
    global sophia_instance
    if sophia_instance is None:
        try:
            sophia_instance = HybridSophIA(session_name="web_session", auto_save=True)
            logger.info("✅ SophIA initialisée pour l'interface web")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation SophIA: {e}")
            sophia_instance = None
    return sophia_instance

@app.route('/')
def index():
    """Page principale"""
    return render_template('sophia_chat.html')

@app.route('/api/status')
def status():
    """Status de SophIA"""
    sophia = get_sophia()
    if sophia:
        model_info = sophia.llm.get_model_info()
        return jsonify({
            'status': 'ready',
            'llm_status': model_info['status'],
            'model': model_info.get('model', 'Unknown'),
            'ontology_concepts': len(sophia.ontology.concepts),
            'session_name': sophia.session.session_name
        })
    else:
        return jsonify({'status': 'error', 'message': 'SophIA non disponible'}), 500

@app.route('/api/ask', methods=['POST'])
def ask_sophia():
    """Endpoint pour poser une question à SophIA"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question vide'}), 400
        
        sophia = get_sophia()
        if not sophia:
            return jsonify({'error': 'SophIA non disponible'}), 500
        
        # Génération de la réponse
        response = sophia.ask(question)
        
        # Préparation de la réponse
        result = {
            'response': response.natural_response,
            'concepts': response.conceptual_analysis.get('concepts_detected', []),
            'confidence': response.conceptual_analysis.get('confidence', 0),
            'reasoning_path': response.conceptual_analysis.get('reasoning_path', []),
            'timestamp': datetime.now().isoformat(),
            'question': question
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur dans ask_sophia: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def get_history():
    """Récupère l'historique de conversation"""
    try:
        sophia = get_sophia()
        if sophia:
            summary = sophia.get_conversation_summary()
            return jsonify(summary)
        return jsonify({'error': 'SophIA non disponible'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/concepts')
def get_concepts():
    """Récupère la liste des concepts ontologiques"""
    try:
        sophia = get_sophia()
        if sophia:
            concepts = {
                name: {
                    'type': concept.concept_type.value if hasattr(concept, 'concept_type') else 'unknown',
                    'description': getattr(concept, 'description', ''),
                    'related_concepts': getattr(concept, 'related_concepts', [])
                }
                for name, concept in sophia.ontology.concepts.items()
            }
            return jsonify(concepts)
        return jsonify({'error': 'SophIA non disponible'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Gestion WebSocket pour chat en temps réel
@socketio.on('connect')
def handle_connect():
    """Connexion WebSocket"""
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    active_sessions[session_id] = {'connected_at': datetime.now()}
    
    emit('connected', {
        'session_id': session_id,
        'message': '🧠 Connecté à SophIA',
        'status': 'connected'
    })
    
    logger.info(f"Nouvelle connexion WebSocket: {session_id}")

@socketio.on('disconnect')
def handle_disconnect():
    """Déconnexion WebSocket"""
    session_id = session.get('session_id')
    if session_id in active_sessions:
        del active_sessions[session_id]
    logger.info(f"Déconnexion WebSocket: {session_id}")

@socketio.on('ask_question')
def handle_question(data):
    """Traitement question via WebSocket"""
    try:
        question = data.get('question', '').strip()
        session_id = session.get('session_id')
        
        if not question:
            emit('error', {'message': 'Question vide'})
            return
        
        # Émission du status "réflexion"
        emit('thinking', {'message': '🤖 SophIA réfléchit...'})
        
        sophia = get_sophia()
        if not sophia:
            emit('error', {'message': 'SophIA non disponible'})
            return
        
        # Génération réponse
        response = sophia.ask(question)
        
        # Émission de la réponse
        emit('response', {
            'question': question,
            'response': response.natural_response,
            'concepts': response.conceptual_analysis.get('concepts_detected', []),
            'confidence': response.conceptual_analysis.get('confidence', 0),
            'reasoning_path': response.conceptual_analysis.get('reasoning_path', []),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erreur WebSocket: {e}")
        emit('error', {'message': str(e)})

def create_templates():
    """Crée le template HTML"""
    
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 SophIA - IA Philosophique</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header h1 {
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2rem;
            text-align: center;
        }
        
        .status {
            text-align: center;
            margin-top: 0.5rem;
            font-size: 0.9rem;
            color: #666;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 2rem;
            height: calc(100vh - 120px);
        }
        
        .chat-area {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .messages {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 1rem;
            padding: 1rem;
            background: #f8f9ff;
            border-radius: 10px;
            max-height: 60vh;
        }
        
        .message {
            margin-bottom: 1.5rem;
            padding: 1rem;
            border-radius: 10px;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            margin-left: 20%;
            border-bottom-right-radius: 5px;
        }
        
        .sophia-message {
            background: white;
            border: 2px solid #e0e6ff;
            margin-right: 10%;
            border-bottom-left-radius: 5px;
        }
        
        .sophia-message .concepts {
            margin-top: 0.5rem;
            padding: 0.5rem;
            background: #f0f4ff;
            border-radius: 5px;
            font-size: 0.85rem;
            color: #666;
        }
        
        .concept-tag {
            background: #667eea;
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 12px;
            font-size: 0.75rem;
            margin-right: 0.5rem;
            display: inline-block;
        }
        
        .input-area {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        
        .input-area input {
            flex: 1;
            padding: 1rem;
            border: 2px solid #e0e6ff;
            border-radius: 25px;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .input-area input:focus {
            border-color: #667eea;
        }
        
        .send-btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            transition: transform 0.2s;
        }
        
        .send-btn:hover {
            transform: scale(1.05);
        }
        
        .send-btn:disabled {
            opacity: 0.6;
            transform: none;
            cursor: not-allowed;
        }
        
        .sidebar {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .sidebar h3 {
            color: #667eea;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .info-box {
            background: #f8f9ff;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 4px solid #667eea;
        }
        
        .thinking {
            text-align: center;
            color: #667eea;
            font-style: italic;
            padding: 1rem;
            background: #f0f4ff;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
                grid-template-rows: 1fr auto;
                padding: 1rem;
            }
            
            .sidebar {
                order: 2;
            }
        }
        
        .connection-status {
            padding: 0.5rem;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .connected { background: #d4edda; color: #155724; }
        .disconnected { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 SophIA - Intelligence Artificielle Philosophique</h1>
        <div class="status" id="status">Initialisation...</div>
    </div>
    
    <div class="container">
        <div class="chat-area">
            <div class="connection-status" id="connectionStatus">Connexion...</div>
            <div class="messages" id="messages">
                <div class="message sophia-message">
                    <strong>🧠 SophIA :</strong> Bienvenue ! Je suis SophIA, votre assistant philosophique. Posez-moi vos questions sur la philosophie, l'éthique, la métaphysique, l'épistémologie et bien plus encore !
                </div>
            </div>
            <div class="input-area">
                <input type="text" id="questionInput" placeholder="Posez votre question philosophique..." maxlength="500">
                <button class="send-btn" id="sendBtn" onclick="sendQuestion()">Envoyer</button>
            </div>
        </div>
        
        <div class="sidebar">
            <h3>📊 Informations</h3>
            
            <div class="info-box">
                <strong>🔗 Connexion</strong>
                <div id="connectionInfo">En cours...</div>
            </div>
            
            <div class="info-box">
                <strong>🧠 Modèle</strong>
                <div id="modelInfo">LLaMA 3.1 via Ollama</div>
            </div>
            
            <div class="info-box">
                <strong>📚 Ontologie</strong>
                <div id="conceptsCount">Chargement...</div>
            </div>
            
            <div class="info-box">
                <strong>💡 Conseils</strong>
                <ul style="margin-top: 0.5rem; padding-left: 1rem;">
                    <li>Posez des questions ouvertes</li>
                    <li>Explorez les concepts philosophiques</li>
                    <li>Demandez des clarifications</li>
                    <li>Challengez les réponses</li>
                </ul>
            </div>
        </div>
    </div>

    <script>
        // Configuration WebSocket
        const socket = io();
        let isConnected = false;
        let isThinking = false;
        
        // Éléments DOM
        const messagesDiv = document.getElementById('messages');
        const questionInput = document.getElementById('questionInput');
        const sendBtn = document.getElementById('sendBtn');
        const statusDiv = document.getElementById('status');
        const connectionStatus = document.getElementById('connectionStatus');
        const connectionInfo = document.getElementById('connectionInfo');
        const conceptsCount = document.getElementById('conceptsCount');
        
        // Gestion de la connexion
        socket.on('connected', (data) => {
            isConnected = true;
            updateConnectionStatus(true);
            connectionInfo.textContent = `Connecté (${data.session_id.substring(0, 8)}...)`;
        });
        
        socket.on('disconnect', () => {
            isConnected = false;
            updateConnectionStatus(false);
        });
        
        // Gestion des réponses
        socket.on('thinking', (data) => {
            isThinking = true;
            addThinkingMessage();
            updateSendButton();
        });
        
        socket.on('response', (data) => {
            isThinking = false;
            removeThinkingMessage();
            addSophiaMessage(data);
            updateSendButton();
        });
        
        socket.on('error', (data) => {
            isThinking = false;
            removeThinkingMessage();
            addErrorMessage(data.message);
            updateSendButton();
        });
        
        // Fonctions d'interface
        function updateConnectionStatus(connected) {
            connectionStatus.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
            connectionStatus.textContent = connected ? '🟢 Connecté à SophIA' : '🔴 Déconnecté';
            updateSendButton();
        }
        
        function updateSendButton() {
            sendBtn.disabled = !isConnected || isThinking;
            sendBtn.textContent = isThinking ? 'Réflexion...' : 'Envoyer';
        }
        
        function addUserMessage(question) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message user-message';
            messageDiv.innerHTML = `<strong>🤔 Vous :</strong> ${escapeHtml(question)}`;
            messagesDiv.appendChild(messageDiv);
            scrollToBottom();
        }
        
        function addSophiaMessage(data) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message sophia-message';
            
            let conceptsHtml = '';
            if (data.concepts && data.concepts.length > 0) {
                const conceptTags = data.concepts.map(concept => 
                    `<span class="concept-tag">${concept}</span>`
                ).join('');
                conceptsHtml = `<div class="concepts">
                    <strong>💡 Concepts détectés :</strong> ${conceptTags}
                    <br><strong>🎯 Confiance :</strong> ${Math.round(data.confidence * 100)}%
                </div>`;
            }
            
            messageDiv.innerHTML = `
                <strong>🧠 SophIA :</strong> ${escapeHtml(data.response)}
                ${conceptsHtml}
            `;
            
            messagesDiv.appendChild(messageDiv);
            scrollToBottom();
        }
        
        function addThinkingMessage() {
            const thinkingDiv = document.createElement('div');
            thinkingDiv.className = 'thinking';
            thinkingDiv.id = 'thinkingMessage';
            thinkingDiv.textContent = '🤖 SophIA réfléchit à votre question...';
            messagesDiv.appendChild(thinkingDiv);
            scrollToBottom();
        }
        
        function removeThinkingMessage() {
            const thinkingMsg = document.getElementById('thinkingMessage');
            if (thinkingMsg) {
                thinkingMsg.remove();
            }
        }
        
        function addErrorMessage(error) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message sophia-message';
            messageDiv.innerHTML = `<strong style="color: red;">❌ Erreur :</strong> ${escapeHtml(error)}`;
            messagesDiv.appendChild(messageDiv);
            scrollToBottom();
        }
        
        function sendQuestion() {
            const question = questionInput.value.trim();
            if (!question || !isConnected || isThinking) return;
            
            addUserMessage(question);
            socket.emit('ask_question', { question: question });
            questionInput.value = '';
        }
        
        function scrollToBottom() {
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Gestion du clavier
        questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendQuestion();
            }
        });
        
        // Chargement des informations
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ready') {
                    statusDiv.textContent = `✅ Prêt - ${data.model}`;
                    conceptsCount.textContent = `${data.ontology_concepts} concepts`;
                } else {
                    statusDiv.textContent = '❌ Erreur de démarrage';
                }
            })
            .catch(error => {
                statusDiv.textContent = '❌ Erreur de connexion';
            });
        
        // Initialisation
        updateSendButton();
    </script>
</body>
</html>'''
    
    with open(os.path.join(templates_dir, 'sophia_chat.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info("✅ Template HTML créé")

def run_web_interface(host='127.0.0.1', port=5000, debug=False):
    """Lance l'interface web"""
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🌐 SophIA - Interface Web                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

🚀 Démarrage du serveur web...
📍 URL: http://{host}:{port}
🧠 Initialisation de SophIA...
""")
    
    # Créer les templates
    create_templates()
    
    # Initialiser SophIA
    sophia = get_sophia()
    if sophia:
        model_info = sophia.llm.get_model_info()
        print(f"✅ SophIA prête ! LLaMA: {model_info['status']}")
        print(f"📚 Ontologie: {len(sophia.ontology.concepts)} concepts")
    else:
        print("❌ Erreur d'initialisation de SophIA")
    
    print(f"\n🌐 Ouvrez votre navigateur sur: http://{host}:{port}")
    print("💬 Interface de chat philosophique prête !")
    print("\n" + "="*80)
    
    # Lancer le serveur
    try:
        socketio.run(
            app, 
            host=host, 
            port=port, 
            debug=debug,
            use_reloader=False,  # ← Évite le redémarrage double
            log_output=True      # ← Active les logs détaillés
        )
    except KeyboardInterrupt:
        print("\n👋 Arrêt du serveur web")
    except Exception as e:
        print(f"❌ Erreur serveur: {e}")

if __name__ == '__main__':
    run_web_interface(debug=True)# web_interface.py
