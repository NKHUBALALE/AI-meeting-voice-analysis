import librosa
import numpy as np
from moviepy import VideoFileClip
from faster_whisper import WhisperModel
from collections import Counter
import re
import os
import uuid

# Load model ONCE (important for performance)
model = WhisperModel("base", device="cpu", compute_type="int8")


def analyze_video(file_path):

    if not os.path.exists(file_path):
        return {"error": f"Video file not found: {file_path}"}

    temp_audio = f"temp_{uuid.uuid4().hex}.wav"

    try:
        video = VideoFileClip(file_path)

        if video.audio is None:
            return {"error": "No audio track detected. Record using Chrome Tab with audio enabled."}

        video.audio.write_audiofile(temp_audio, logger=None)

        y, sr = librosa.load(temp_audio)

        rms = librosa.feature.rms(y=y)
        avg_volume = np.mean(rms)

        if avg_volume < 0.01:
            volume_result = "LOW"
        elif avg_volume < 0.03:
            volume_result = "GOOD"
        else:
            volume_result = "LOUD"

        clipping_ratio = np.mean(np.abs(y) > 0.99)

        if clipping_ratio > 0.05:
            clipping_result = "CLIPPING DETECTED"
        elif clipping_ratio > 0.01:
            clipping_result = "Signal very hot"
        else:
            clipping_result = "Clean signal"

        pitch, _ = librosa.piptrack(y=y, sr=sr)
        pitch_values = pitch[pitch > 0]

        if len(pitch_values) == 0:
            pitch_variance = 0
            tone_result = "NO SPEECH DETECTED"
        else:
            pitch_variance = np.var(pitch_values)

            if pitch_variance < 200:
                tone_result = "MONOTONE"
            elif pitch_variance < 1000:
                tone_result = "NORMAL"
            else:
                tone_result = "EXPRESSIVE"

        segments, info = model.transcribe(temp_audio)

        text = ""
        for segment in segments:
            text += segment.text + " "

        word_count = len(text.split())

        if word_count == 0:
            return {"error": "No speech detected in audio"}

        audio_duration_minutes = librosa.get_duration(y=y, sr=sr) / 60
        wpm = word_count / audio_duration_minutes if audio_duration_minutes > 0 else 0

        if wpm < 120:
            pace_result = "SLOW"
        elif wpm < 160:
            pace_result = "GOOD"
        else:
            pace_result = "FAST"

        intervals = librosa.effects.split(y, top_db=30)

        speech_duration = sum((end - start) for start, end in intervals) / sr
        total_duration = librosa.get_duration(y=y, sr=sr)

        silence_duration = total_duration - speech_duration

        speech_ratio = (speech_duration / total_duration) * 100 if total_duration > 0 else 0
        silence_ratio = (silence_duration / total_duration) * 100 if total_duration > 0 else 0

        pauses = [
            (intervals[i + 1][0] - intervals[i][1]) / sr
            for i in range(len(intervals) - 1)
        ]

        avg_pause = np.mean(pauses) if pauses else 0
        longest_pause = max(pauses) if pauses else 0

        questions = text.count("?")
        question_words = ["who", "what", "why", "how", "when"]
        questions += sum(text.lower().count(q) for q in question_words)

        statements = max(0, len(text.split(".")) - 1)

        words = re.findall(r'\b[a-z]+\b', text.lower())

        stop_words = {
            "the","and","is","to","a","of","in","that","it","for","on","with","as",
            "this","be","are","was","were","or","an","at","by","from"
        }

        filtered_words = [w for w in words if w not in stop_words and len(w) > 2]

        keyword_counts = Counter(filtered_words)
        top_keywords = keyword_counts.most_common(5)

        filler_words = ["um","uh","like","you know","actually","basically"]

        filler_counts = {}
        total_fillers = 0

        for word in filler_words:
            count = text.lower().count(word)
            if count > 0:
                filler_counts[word] = count
                total_fillers += count

        if wpm > 170 and tone_result == "EXPRESSIVE":
            profile = "Energetic Speaker"
        elif wpm < 120 and avg_pause > 1:
            profile = "Calm Speaker"
        elif tone_result == "MONOTONE":
            profile = "Reserved Speaker"
        elif speech_ratio > 85:
            profile = "Information-Dense Speaker"
        else:
            profile = "Balanced Communicator"

        feedback = []

        if volume_result == "LOW":
            feedback.append("Your voice volume is low. Move closer to the microphone or speak louder.")

        if clipping_ratio > 0.05:
            feedback.append("Audio clipping detected. Reduce microphone gain or move slightly away from the mic.")

        if pace_result == "FAST":
            feedback.append("You are speaking very fast. Slowing down can improve clarity.")

        if pace_result == "SLOW":
            feedback.append("Your speaking pace is slow. Increasing pace may improve engagement.")

        if tone_result == "MONOTONE":
            feedback.append("Your voice tone is monotone. Add vocal emphasis to key ideas.")

        if speech_ratio > 85:
            feedback.append("You speak continuously with few pauses. Add pauses to help listeners process ideas.")

        if avg_pause < 0.2:
            feedback.append("Your pauses are very short. Slightly longer pauses can improve clarity.")

        if questions < 2:
            feedback.append("Consider asking more questions to engage listeners.")

        if total_fillers > 10:
            feedback.append("You used many filler words. Reducing them can improve clarity.")
        
        if len(feedback) == 0:
            feedback.append("Great job! Your communication is clear, balanced, and effective.")
        score = 100

        if pace_result != "GOOD":
            score -= 10
        if tone_result == "MONOTONE":
            score -= 10
        if volume_result == "LOW":
            score -= 10
        if speech_ratio > 85:
            score -= 5
        if avg_pause < 0.2:
            score -= 5
        if total_fillers > 10:
            score -= 10

        score = max(score, 0)

        return {
            "volume": volume_result,
            "clipping": clipping_result,
            "pace": pace_result,
            "wpm": int(wpm),
            "tone": tone_result,
            "avg_pause": round(avg_pause, 2),
            "longest_pause": round(longest_pause, 2),
            "speech_ratio": round(speech_ratio, 1),
            "silence_ratio": round(silence_ratio, 1),
            "questions": questions,
            "statements": statements,
            "profile": profile,
            "keywords": [{"word": w, "count": c} for w, c in top_keywords],
            "filler_words": filler_counts,
            "confidence_score": score,
            "feedback": feedback,
            "transcript": text.strip()
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        if os.path.exists(temp_audio):
            try:
                os.remove(temp_audio)
            except:
                pass

        try:
            video.close()
        except:
            pass