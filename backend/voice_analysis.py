import librosa
import numpy as np
from moviepy import VideoFileClip
from faster_whisper import WhisperModel
from collections import Counter
import re

VIDEO_FILE = "input.webm"

print("\nProcessing meeting recording...\n")

video = VideoFileClip(VIDEO_FILE)

if video.audio is None:
    print("ERROR: No audio track detected. Record using Chrome Tab with audio enabled.")
    exit()

video.audio.write_audiofile("audio.wav")

y, sr = librosa.load("audio.wav")

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
pitch_variance = np.var(pitch_values)

if pitch_variance < 200:
    tone_result = "MONOTONE"
elif pitch_variance < 1000:
    tone_result = "NORMAL"
else:
    tone_result = "EXPRESSIVE"

print("Transcribing speech...")

model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe("audio.wav")

text = ""
for segment in segments:
    text += segment.text + " "

word_count = len(text.split())

audio_duration_minutes = librosa.get_duration(y=y, sr=sr) / 60
wpm = word_count / audio_duration_minutes

if wpm < 120:
    pace_result = "SLOW"
elif wpm < 160:
    pace_result = "GOOD"
else:
    pace_result = "FAST"

intervals = librosa.effects.split(y, top_db=30)

speech_duration = 0
for start, end in intervals:
    speech_duration += (end - start)

speech_duration = speech_duration / sr
total_duration = librosa.get_duration(y=y, sr=sr)

silence_duration = total_duration - speech_duration

speech_ratio = (speech_duration / total_duration) * 100
silence_ratio = (silence_duration / total_duration) * 100

pauses = []

for i in range(len(intervals) - 1):
    pause = (intervals[i+1][0] - intervals[i][1]) / sr
    pauses.append(pause)

avg_pause = np.mean(pauses) if pauses else 0
longest_pause = max(pauses) if pauses else 0

questions = text.count("?")

question_words = ["who","what","why","how","when"]
extra_questions = sum(text.lower().count(q) for q in question_words)

questions += extra_questions
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

print("\nVoice Metrics")
print(f"Volume: {volume_result}")
print(f"Clipping: {clipping_result}")
print(f"Speaking Pace: {pace_result} ({int(wpm)} WPM)")
print(f"Tone Variation: {tone_result}")
print(f"Average Pause: {avg_pause:.2f}s")
print(f"Speech: {speech_ratio:.1f}% | Silence: {silence_ratio:.1f}%")
print(f"Questions: {questions} | Statements: {statements}")

print("\nCommunication Profile:", profile)

print("\nTopic Keywords")
for word, count in top_keywords:
    print(f"{word} ({count})")

print("\nFiller Words")

if filler_counts:
    for w, c in filler_counts.items():
        print(f"{w}: {c}")
else:
    print("None detected")

print(f"\nSpeaking Confidence Score: {score}/100")

print("\nAI Communication Feedback")

if feedback:
    for f in feedback:
        print("-", f)
else:
    print("Your communication metrics appear balanced.")

print("\nAnalysis complete\n")