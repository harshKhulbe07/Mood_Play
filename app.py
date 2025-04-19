from flask import Flask, render_template, request, jsonify
from deepface import DeepFace
import os
import random
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Mapping of emotions to song folders (you can customize these)
EMOTION_FOLDERS = {
    "happy": "static/songs/happy",
    "sad": "static/songs/sad",
    "angry": "static/songs/angry",
    "neutral": "static/songs/neutral",
    "surprise": "static/songs/surprise",
    "fear": "static/songs/fear",
    "disgust": "static/songs/disgust"
}

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        img_data = data['image'].split(",")[1]  # remove data:image/jpeg;base64,...
        image_bytes = base64.b64decode(img_data)
        img = Image.open(BytesIO(image_bytes))

        # Save temp image for DeepFace
        temp_path = "temp.jpg"
        img.save(temp_path)

        # Analyze emotion using DeepFace
        analysis = DeepFace.analyze(img_path=temp_path, actions=['emotion'], enforce_detection=False)
        emotion = analysis[0]['dominant_emotion'].lower()

        # Pick a song from the corresponding folder
        song_folder = EMOTION_FOLDERS.get(emotion, EMOTION_FOLDERS['neutral'])
        song_path = get_random_song(song_folder)

        return jsonify({
            "emotion": emotion,
            "song_url": '/' + song_path  # To serve from /static/...
        })

    except Exception as e:
        print("Error in /analyze:", e)
        return jsonify({"error": "Failed to analyze image"}), 500


@app.route('/next')
def next_song():
    emotion = request.args.get('same_emotion', '').lower()
    song_folder = EMOTION_FOLDERS.get(emotion)

    if not song_folder or not os.path.exists(song_folder):
        return jsonify({"error": "No songs found for this emotion"}), 404

    song_path = get_random_song(song_folder)
    return jsonify({'song_url': '/' + song_path})


def get_random_song(folder_path):
    songs = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
    if not songs:
        return "static/songs/neutral/default.mp3"
    selected_song = random.choice(songs)
    return os.path.join(folder_path, selected_song).replace("\\", "/")  # for Windows compatibility


if __name__ == '__main__':
    app.run(debug=True)
