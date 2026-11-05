import os, subprocess, json
from gtts import gTTS
import numpy as np

vdir = r'D:\Nghia\Truyen co tich\assets\videos\tap1'
adir = r'D:\Nghia\Truyen co tich\assets\audio\tap1'
art_dir = r'C:\Users\nghiabh\.gemini\antigravity\brain\da7e6bcc-ec25-40e6-bc5c-8dfa02d4e056'
storyboard_media = r'C:\Users\nghiabh\.agent-storyboard\projects\project-mw3167g1-kt97m4\media'
os.makedirs(adir, exist_ok=True)

# 1. Concise, sharp script lines designed for 8s shots
lines = [
    ("shot_01_fixed.mp3", "Đời Hùng Vương thứ sáu, dẹp xong giặc Ân, thiên hạ thái bình, nhà vua tuổi đã cao."),
    ("shot_02_fixed.mp3", "Vua muốn truyền ngôi, nhưng có hai mươi người con trai, không biết chọn ai xứng đáng."),
    ("shot_03_fixed.mp3", "Vua phán: Đến hội Tiên Vương, ai dâng được món ăn vừa ý ta cúng tổ tiên, ta sẽ truyền ngôi!"),
    ("shot_04_fixed.mp3", "Các hoàng tử đua tìm của ngon vật lạ. Riêng Lang Liêu quen việc đồng áng, lòng băn khoăn khôn xiết."),
]

def get_duration(file_path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    return float(subprocess.check_output(cmd).decode().strip())

TARGET_MAX_DUR = 5.2 # Max 5.2s per line, leaving ~2.0s silent breathing room before next 8s cut!

for fname, text in lines:
    raw_path = os.path.join(adir, f"raw_{fname}")
    tts = gTTS(text, lang='vi', slow=False)
    tts.save(raw_path)
    
    # Strip silence first
    trimmed_path = os.path.join(adir, f"trimmed_{fname}")
    cmd_trim = [
        "ffmpeg", "-y", "-i", raw_path,
        "-af", "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse",
        trimmed_path
    ]
    subprocess.run(cmd_trim, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    dur = get_duration(trimmed_path)
    print(f"{fname} raw duration: {dur:.2f}s")
    
    # Calculate tempo speedup needed to fit within TARGET_MAX_DUR
    speed = max(1.0, dur / TARGET_MAX_DUR)
    proc_path = os.path.join(adir, fname)
    
    # Apply atempo + cinematic vocal EQ (120Hz warmth + 3.2kHz speech clarity)
    cmd_proc = [
        "ffmpeg", "-y", "-i", trimmed_path,
        "-af", f"atempo={speed:.3f},equalizer=f=120:width_type=o:width=1:g=3.0,equalizer=f=3200:width_type=o:width=1:g=2.2",
        proc_path
    ]
    subprocess.run(cmd_proc, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    final_dur = get_duration(proc_path)
    print(f" -> {fname} calibrated duration: {final_dur:.2f}s (speedup: {speed:.2f}x)")

# 2. Synthesize Dong Son Bronze Drum & Atmospheric Drone BGM
sr = 44100
total_sec = 32.5
total_samples = int(sr * total_sec)
t = np.linspace(0, total_sec, total_samples, endpoint=False)

drone = (
    0.22 * np.sin(2 * np.pi * 65.41 * t) +               # C2
    0.16 * np.sin(2 * np.pi * 98.00 * t) +               # G2
    0.11 * np.sin(2 * np.pi * 130.81 * t) +              # C3
    0.07 * np.sin(2 * np.pi * 196.00 * t + 0.5) +        # G3
    0.04 * np.sin(2 * np.pi * 293.66 * t + 1.0)          # D4
)
lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.12 * t)
drone = drone * lfo

drum_track = np.zeros(total_samples, dtype=np.float32)

def strike_bronze_drum(start_time, strength=1.0):
    start_idx = int(start_time * sr)
    dur = 4.0
    n_samples = min(int(dur * sr), total_samples - start_idx)
    st = np.linspace(0, dur, n_samples, endpoint=False)
    
    freq_sweep = 95.0 * np.exp(-12.0 * st) + 48.0
    thud = np.sin(2 * np.pi * np.cumsum(freq_sweep) / sr) * np.exp(-3.5 * st)
    
    ring1 = np.sin(2 * np.pi * 174.0 * st) * np.exp(-1.8 * st) * 0.45
    ring2 = np.sin(2 * np.pi * 287.0 * st + 0.3) * np.exp(-2.2 * st) * 0.35
    ring3 = np.sin(2 * np.pi * 442.0 * st + 0.7) * np.exp(-3.0 * st) * 0.25
    ring4 = np.sin(2 * np.pi * 715.0 * st + 1.2) * np.exp(-4.5 * st) * 0.15
    
    hit = strength * (thud * 0.75 + ring1 + ring2 + ring3 + ring4)
    drum_track[start_idx : start_idx + n_samples] += hit

# Exact ceremonial rhythm aligned with scene cuts (0.0s, 8.0s, 16.0s, 24.0s)
for st_time in [0.2, 4.0, 8.0, 12.0, 16.0, 19.0, 24.0, 28.0]:
    strength = 1.0 if st_time in [0.2, 8.0, 16.0, 24.0] else 0.6
    strike_bronze_drum(st_time, strength)

bgm = drone + drum_track
fade_in = np.minimum(1.0, np.linspace(0, 1.0, int(1.5 * sr)))
bgm[:len(fade_in)] *= fade_in
fade_out = np.minimum(1.0, np.linspace(1.0, 0, int(2.0 * sr)))
bgm[-len(fade_out):] *= fade_out
bgm = bgm / (np.max(np.abs(bgm)) + 1e-6) * 0.35

import wave
bgm_int16 = (bgm * 32767).astype(np.int16)
bgm_path = os.path.join(adir, "dong_son_bgm.wav")
with wave.open(bgm_path, "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sr)
    wf.writeframes(bgm_int16.tobytes())

# 3. Mix audio timeline with guaranteed ZERO overlap
# Scene 1: 0.0s - 8.0s   -> Voice at 0.8s, ends at ~6.0s (pause ~2.0s)
# Scene 2: 8.0s - 16.0s  -> Voice at 8.8s, ends at ~14.0s (pause ~2.0s)
# Scene 3: 16.0s - 24.0s -> Voice at 16.8s, ends at ~22.0s (pause ~2.0s)
# Scene 4: 24.0s - 32.0s -> Voice at 24.8s, ends at ~30.0s (pause ~2.0s)
s1 = os.path.join(adir, "shot_01_fixed.mp3")
s2 = os.path.join(adir, "shot_02_fixed.mp3")
s3 = os.path.join(adir, "shot_03_fixed.mp3")
s4 = os.path.join(adir, "shot_04_fixed.mp3")

filter_complex = (
    "[1:a]adelay=800|800,volume=1.40[v1];"
    "[2:a]adelay=8800|8800,volume=1.40[v2];"
    "[3:a]adelay=16800|16800,volume=1.45[v3];"
    "[4:a]adelay=24800|24800,volume=1.40[v4];"
    "[0:a]volume=0.32[bg];"
    "[bg][v1][v2][v3][v4]amix=inputs=5:duration=longest:dropout_transition=1[aout]"
)

full_audio_out = os.path.join(adir, "full_soundtrack_calibrated.wav")
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
print("Mixed calibrated soundtrack with zero collisions!")

# 4. Mux into Final Video
master_video = os.path.join(vdir, "banh_chung_tap_1_rough_cut.mp4")
final_video = os.path.join(vdir, "banh_chung_tap_1_cinematic_final.mp4")
art_final_video = os.path.join(art_dir, "banh_chung_tap_1_cinematic_final.mp4")
sb_final_video = os.path.join(storyboard_media, "banh_chung_tap_1_cinematic_final.mp4")

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
shutil.copy2(final_video, sb_final_video)
print(f"Calibrated Final Film updated successfully!")
print(f"File size: {os.path.getsize(final_video)} bytes")
