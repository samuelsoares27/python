from flask import Flask, render_template, request, jsonify
import os
import whisper
import yt_dlp
from pydub import AudioSegment

app = Flask(__name__, static_folder="static")

OUTPUT_FOLDER = "downloads"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    video_url = data.get("video_url")
    
    if not video_url:
        return jsonify({"error": "URL do vídeo é obrigatória!"}), 400

    try:
        audio_path = os.path.join(OUTPUT_FOLDER, "audio.mp3")
        wav_path = os.path.join(OUTPUT_FOLDER, "audio.wav")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        audio = AudioSegment.from_file(audio_path)
        audio.export(wav_path, format="wav")

        model = whisper.load_model("base")
        result = model.transcribe(wav_path)
        transcribed_text = result["text"]

        return jsonify({"transcription": transcribed_text})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
