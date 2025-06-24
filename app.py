from flask import Flask, flash,render_template,request,redirect
import os
import uuid
import yt_dlp
import whisper
from datetime import datetime
from flask import send_from_directory
app=Flask(__name__)
app.secret_key = "srinithi@8287"
# Ensure required folders exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("subtitles", exist_ok=True)
models={}
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  
@app.route('/')
def home():
    return render_template("index.html")


def log():
    with open("used_log.txt","a",encoding="utf-8")as f:
        f.write(f"Used on {datetime.now()}\n")
    
@app.route('/generate',methods=['POST'])
def generate():
    log()
    processed=False
    youtube=request.form.get("youtube")
    language=request.form.get("language")
    model_siZe=request.form.get("model")
    if 'file' in request.files:
        file=request.files['file']
        if file.filename!="":
            unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
            file_path=os.path.join("uploads",unique_filename)
            file.save(file_path)
            subtitle_text,subtitle_file=title(file_path,model_siZe,language)
            processed=True
    if youtube:
        ydl_opts={
        'format':'mp4',
        'outtmpl':'uploads/%(title)s.%(ext)s'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info=ydl.extract_info(youtube)
            filename=ydl.prepare_filename(info)
            subtitle_text,subtitle_file=title(filename,model_siZe,language)
            processed=True
    if processed:
        return render_template('index.html',subtitle=subtitle_text,subtitle_file=subtitle_file)
    return "Provide with valid youtube link/files"
    
@app.route('/feed')
def feed():
    return render_template('feedback.html')

@app.route('/feedback',methods=['POST'])
def feedback():
    message=request.form.get("feed")
    with open ("feedback.txt","a",encoding="utf-8")as f:
        f.write(message+"\n---\n")
    return redirect('/')

def timeformat(seconds):
    hour=int(seconds//3600)
    minute=(int(seconds%3600)//60)
    sec=int(seconds%60)
    millisec=int((seconds-int(seconds))*1000)
    return f"{hour:02}:{minute:02}:{sec:02}:{millisec:03}"

def get_model(model_name):
    if model_name not in models:
       models[model_name]=whisper.load_model(model_name)
    return models[model_name]

def title(filename,model_siZe,language=None):
    model = get_model(model_siZe)
    name=os.path.basename(filename)
    subtitle_file=os.path.splitext(name)[0]+".srt"
    path=os.path.join("uploads",name)
    if language:
        res=model.transcribe(path,language=language)
    else:
        language=getLanguage(path,model_siZe)
        res=model.transcribe(path,language=language)
    subtitle_path=os.path.join("subtitles",subtitle_file)
    with open(subtitle_path,"w",encoding="utf-8")as f:
        for i,segment in enumerate(res["segments"],start=1):
            start=timeformat(segment["start"])
            end=timeformat(segment["end"])
            text=segment["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
    return res["text"],subtitle_file


def getLanguage(path,model_siZe):
    model=get_model(model_siZe)
    audio_data=whisper.load_audio(path)
    audio_data=whisper.pad_or_trim(audio_data)

    mel=whisper.log_mel_spectrogram(audio_data).to(model.device)

    _,probs=model.detect_language(mel)
    detected_lang=max(probs,key=probs.get)

    return detected_lang

@app.route('/download/<filename>')
def download(filename):
    print(filename)
    return send_from_directory("subtitles",filename,as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

