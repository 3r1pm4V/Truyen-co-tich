import os, subprocess, json, math
from gtts import gTTS
import numpy as np

vdir = r'D:\Nghia\Truyen co tich\assets\videos\tap1'
adir = r'D:\Nghia\Truyen co tich\assets\audio\tap1'
art_dir = r'C:\Users\nghiabh\.gemini\antigravity\brain\da7e6bcc-ec25-40e6-bc5c-8dfa02d4e056'
os.makedirs(adir, exist_ok=True)

# 1. Generate Voiceover lines with gTTS
lines = [
    ("shot_01.mp3", "Vào đời Hùng Vương thứ sáu, sau khi dẹp xong giặc Ân, thiên hạ thái bình, nhà vua tuổi đã cao."),
    ("shot_02.mp3", "Nhà vua muốn truyền ngôi, nhưng có đến hai mươi người con trai, không biết chọn ai cho xứng đáng."),
    ("shot_03.mp3", "Vua bèn phán rằng: Đến ngày hội Tiên Vương, ai tìm được món ăn vừa ý ta để cúng trời đất tổ tiên, ta sẽ truyền ngôi báu cho!"),
    ("shot_04.mp3", "Các hoàng tử đua nhau tìm của ngon vật lạ. Riêng Lang Liêu mồ côi mẹ, quen việc đồng áng, trong lòng băn khoăn khôn xiết."),
]

for fname, text in lines:
    raw_path = os.path.join(adir, f"raw_{fname}")
    tts = gTTS(text, lang='vi', slow=False)
    tts.save(raw_path)
    
    # Process audio with ffmpeg for cinematic warmth (slight pitch adjust and warm bass eq)
    proc_path = os.path.join(adir, fname)
    cmd = [
        "ffmpeg", "-y", "-i", raw_path,
        "-af", "atempo=0.92,equalizer=f=120:width_type=o:width=1:g=3.5,equalizer=f=3500:width_type=o:width=1:g=2.0",
        proc_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Generated and enhanced: {fname}")

# 2. Synthesize Ancient Dong Son Bronze Drum & Atmospheric Drone Music (32 seconds, 44100Hz)
sr = 44100
total_sec = 32.5
total_samples = int(sr * total_sec)
t = np.linspace(0, total_sec, total_samples, endpoint=False)

# Harmonic Drone (C2 - G2 - D3 ancient pentatonic fundamental)
drone = (
    0.22 * np.sin(2 * np.pi * 65.41 * t) +               # C2
    0.16 * np.sin(2 * np.pi * 98.00 * t) +               # G2
    0.11 * np.sin(2 * np.pi * 130.81 * t) +              # C3
    0.07 * np.sin(2 * np.pi * 196.00 * t + 0.5) +        # G3
    0.04 * np.sin(2 * np.pi * 293.66 * t + 1.0)          # D4
)
# Add subtle slow breathing amplitude modulation (0.12 Hz)
lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.12 * t)
drone = drone * lfo

# Bronze Drum Hits (Trống Đồng - deep fundamental with metallic non-harmonic rings)
drum_track = np.zeros(total_samples, dtype=np.float32)

def strike_bronze_drum(start_time, strength=1.0):
    start_idx = int(start_time * sr)
    dur = 4.2 # 4.2 seconds decay
    n_samples = min(int(dur * sr), total_samples - start_idx)
    st = np.linspace(0, dur, n_samples, endpoint=False)
    
    # Pitch drop transient (thud)
    freq_sweep = 95.0 * np.exp(-12.0 * st) + 48.0
    thud = np.sin(2 * np.pi * np.cumsum(freq_sweep) / sr) * np.exp(-3.5 * st)
    
    # Bronze metallic inharmonic overtones
    ring1 = np.sin(2 * np.pi * 174.0 * st) * np.exp(-1.8 * st) * 0.45
    ring2 = np.sin(2 * np.pi * 287.0 * st + 0.3) * np.exp(-2.2 * st) * 0.35
    ring3 = np.sin(2 * np.pi * 442.0 * st + 0.7) * np.exp(-3.0 * st) * 0.25
    ring4 = np.sin(2 * np.pi * 715.0 * st + 1.2) * np.exp(-4.5 * st) * 0.15
    
    hit = strength * (thud * 0.75 + ring1 + ring2 + ring3 + ring4)
    drum_track[start_idx : start_idx + n_samples] += hit

# Strike pattern (ceremonial rhythm matching scene shifts)
strike_times = [
    0.2,    # Opening majestic strike
    4.0,    # Mid shot 1
    8.0,    # Shift to Throne room
    12.0,   # Deep resonance
    16.0,   # King decree strike
    18.5,   # Emphasize decree
    24.0,   # Shift to Lang Lieu
    28.0    # Contemplation strike
]

for st_time in strike_times:
    strength = 1.0 if st_time in [0.2, 8.0, 16.0, 24.0] else 0.65
    strike_bronze_drum(st_time, strength)

# Final BGM mix
bgm = drone + drum_track
# Fade in 1.5s, fade out 2.0s
fade_in = np.minimum(1.0, np.linspace(0, 1.0, int(1.5 * sr)))
bgm[:len(fade_in)] *= fade_in
fade_out = np.minimum(1.0, np.linspace(1.0, 0, int(2.0 * sr)))
bgm[-len(fade_out):] *= fade_out

# Normalize BGM
bgm = bgm / (np.max(np.abs(bgm)) + 1e-6) * 0.38

# Save BGM to wav
import wave
bgm_int16 = (bgm * 32767).astype(np.int16)
bgm_path = os.path.join(adir, "dong_son_bgm.wav")
with wave.open(bgm_path, "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sr)
    wf.writeframes(bgm_int16.tobytes())
print("Generated Dong Son BGM:", bgm_path)

# 3. Assemble Audio with FFmpeg
s1 = os.path.join(adir, "shot_01.mp3")
s2 = os.path.join(adir, "shot_02.mp3")
s3 = os.path.join(adir, "shot_03.mp3")
s4 = os.path.join(adir, "shot_04.mp3")

# Build full mixed audio track:
# [0] bgm, [1] s1, [2] s2, [3] s3, [4] s4
# adelay filters in milliseconds: s1 at 800ms, s2 at 8600ms, s3 at 16600ms, s4 at 24600ms
filter_complex = (
    "[1:a]adelay=800|800,volume=1.35[v1];"
    "[2:a]adelay=8600|8600,volume=1.35[v2];"
    "[3:a]adelay=16600|16600,volume=1.40[v3];"
    "[4:a]adelay=24600|24600,volume=1.35[v4];"
    "[0:a]volume=0.35[bg];"
    "[bg][v1][v2][v3][v4]amix=inputs=5:duration=longest:dropout_transition=2[aout]"
)

full_audio_out = os.path.join(adir, "full_soundtrack.wav")
cmd_audio = [
    "ffmpeg", "-y",
    "-i", bgm_path,
    "-i", s1,
    "-i", s2,
    "-i", s3,
    "-i", s4,
    "-filter_complex", filter_complex,
    "-map", "[aout]",
    "-c:a", "pcm_s16le",
    full_audio_out
]
subprocess.run(cmd_audio, check=True)
print("Mixed full audio soundtrack!")

# 4. Mux with 32s Master Video
master_video = os.path.join(vdir, "banh_chung_tap_1_rough_cut.mp4")
final_video = os.path.join(vdir, "banh_chung_tap_1_cinematic_final.mp4")
art_final_video = os.path.join(art_dir, "banh_chung_tap_1_cinematic_final.mp4")

cmd_mux = [
    "ffmpeg", "-y",
    "-i", master_video,
    "-i", full_audio_out,
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    final_video
]
subprocess.run(cmd_mux, check=True)
import shutil
shutil.copy2(final_video, art_final_video)
print(f"Final Cinematic Film with Voiceover & Music produced successfully!")
print(f"File: {final_video}")
print(f"Size: {os.path.getsize(final_video)} bytes")
