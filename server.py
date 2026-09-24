import os
import json
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Разрешаем прием скриншотов из Web App

# Ключ будет безопасно подтягиваться из настроек облака
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "Скриншот не загружен"}), 400
    
    file = request.files['image']
    base64_image = base64.b64encode(file.read()).decode('utf-8')
    
    prompt_text = """
    Ты профессиональный спортивный аналитик. Твоя задача — проанализировать реальный скриншот букмекерской конторы.
    1. Убедись, что на скриншоте есть линия ставок.
    2. Определи названия играющих команд.
    3. Выбери ровно ОДИН исход со скриншота, коэффициент которого от 1.50 до 2.00 (или ближайший).
    4. Напиши краткое (1-2 предложения) аналитическое обоснование.
    Верни ответ СТРОГО в формате JSON:
    {"team1": "Команда 1", "team2": "Команда 2", "best_pick": "Исход", "odd": 1.85, "probability_pct": 82, "analysis_logic": "Обоснование..."}
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "response_format": { "type": "json_object" },
        "max_tokens": 350
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        ai_data = json.loads(response.json()["choices"][0]["message"]["content"])
        return jsonify(ai_data)
    except Exception as e:
        return jsonify({"error": f"Ошибка OpenAI: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
