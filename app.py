from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import os
import random
import pyttsx3

app = Flask(__name__)

# -------- Upload folder --------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- Behavior labels ----------
ALL_BEHAVIORS = [
    "normal", "fall", "angry", "attack", "distress",
    "sleeping", "wandering", "talking", "eating", "seizure"
]
CRITICAL = ["fall", "attack", "distress", "seizure"]


# ---------- Fake Behavior Detector ----------
def analyze_video(path):
    name = os.path.basename(path).lower()
    matches = [b for b in ALL_BEHAVIORS if b in name]

    if not matches:
        matches = random.sample(ALL_BEHAVIORS, k=random.randint(1, 3))

    return matches


# ---------- Text-to-Speech Generator ----------
def speak_alert(events):
    engine = pyttsx3.init()

    if "fall" in events:
        msg = "Alert! The patient has fallen."
    elif "attack" in events:
        msg = "Emergency! Someone is attacking the patient."
    elif "seizure" in events:
        msg = "Medical emergency! The patient is having a seizure."
    elif "distress" in events:
        msg = "Warning! The patient is in distress."
    else:
        msg = "Non-critical behavior detected."

    audio_path = os.path.join(UPLOAD_FOLDER, "alert.mp3")
    engine.save_to_file(msg, audio_path)
    engine.runAndWait()

    return msg, "alert.mp3"


# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/prediction")
def prediction_page():
    return render_template("predict.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/upload", methods=["POST"])
def upload():
    if "video" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    video = request.files["video"]
    save_path = os.path.join(UPLOAD_FOLDER, video.filename)
    video.save(save_path)

    events = analyze_video(save_path)
    voice_msg, audio_file = speak_alert(events)

    return jsonify({
        "video_name": video.filename,
        "behaviors": ", ".join(events),
        "voice_message": voice_msg,
        "audio_url": f"/uploads/{audio_file}"
    })


if __name__ == "__main__":
    app.run(debug=True)
