import urllib.request, json, os, subprocess, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np

vdir = r'D:\Nghia\Truyen co tich\assets\videos\tap1'
adir = r'D:\Nghia\Truyen co tich\assets\audio\tap1_cit'
art_dir = r'C:\Users\nghiabh\.gemini\antigravity\brain\da7e6bcc-ec25-40e6-bc5c-8dfa02d4e056'
storyboard_media = r'C:\Users\nghiabh\.agent-storyboard\projects\project-mw3167g1-kt97m4\media'
os.makedirs(adir, exist_ok=True)

VOICE_ID = "Thiện Minh"  # Nam · Bắc · Phong cách kể chuyện · 48 kHz
API_URL = "http://127.0.0.1:8001/api/tts/generate"

lines = [
    ("shot_01.wav", "Đời Hùng Vương thứ sáu, dẹp xong giặc Ân, thiên hạ thái bình, nhà vua tuổi đã cao."),
    ("shot_02.wav", "Vua muốn truyền ngôi, nhưng có hai mươi người con trai, không biết chọn ai cho xứng đáng."),
    ("shot_03.wav", "Vua phán: Đến hội Tiên Vương, ai dâng được món ăn vừa ý ta cúng tổ tiên, ta sẽ truyền ngôi!"),
    ("shot_04.wav", "Các hoàng tử đua tìm của ngon vật lạ. Riêng Lang Liêu quen việc đồng áng, lòng băn khoăn khôn xiết."),
]

def get_duration(file_path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    return float(subprocess.check_output(cmd).decode().strip())

TARGET_MAX_DUR = 5.2 # Max duration per shot

print(f"--- 1. Generating Studio Narration via CIT Voice Studio ({VOICE_ID}) ---")
processed_files = []

for fname, text in lines:
    raw_path = os.path.join(adir, f"raw_{fname}")
    payload = {
        "text": text,
        "voice_id": VOICE_ID,
        "speed": 1.0,
        "temperature": 0.65,
        "format": "wav"
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        with open(raw_path, 'wb') as f:
            f.write(resp.read())
            
    # Remove leading/trailing silence
    trimmed_path = os.path.join(adir, f"trimmed_{fname}")
    cmd_trim = [
        "ffmpeg", "-y", "-i", raw_path,
        "-af", "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse",
        trimmed_path
    ]
    subprocess.run(cmd_trim, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    dur = get_duration(trimmed_path)
    speed = max(1.0, dur / TARGET_MAX_DUR)
    
    # Processed output (48kHz, perfectly calibrated duration <= 5.2s)
    proc_path = os.path.join(adir, fname)
    cmd_proc = [
        "ffmpeg", "-y", "-i", trimmed_path,
        "-af", f"atempo={speed:.3f}",
        "-ar", "48000",
        proc_path
    ]
    subprocess.run(cmd_proc, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    final_dur = get_duration(proc_path)
    print(f"Generated {fname}: {final_dur:.2f}s (speedup: {speed:.2f}x)")
    processed_files.append(proc_path)

# 2. Synthesize High-Res 48kHz Dong Son Bronze Drum & Harmonic Drone BGM
print("--- 2. Synthesizing 48kHz Dong Son Bronze Drum Soundtrack ---")
sr = 48000
total_sec = 32.5
total_samples = int(sr * total_sec)
t = np.linspace(0, total_sec, total_samples, endpoint=False)

drone = (
    0.20 * np.sin(2 * np.pi * 65.41 * t) +               # C2
    0.15 * np.sin(2 * np.pi * 98.00 * t) +               # G2
    0.10 * np.sin(2 * np.pi * 130.81 * t) +              # C3
    0.06 * np.sin(2 * np.pi * 196.00 * t + 0.5) +        # G3
    0.04 * np.sin(2 * np.pi * 293.66 * t + 1.0)          # D4
)
lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.12 * t)
drone = drone * lfo

drum_track = np.zeros(total_samples, dtype=np.float32)

def strike_bronze_drum(start_time, strength=1.0):
    start_idx = int(start_time * sr)
    dur = 4.2
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

for st_time in [0.2, 4.0, 8.0, 12.0, 16.0, 19.0, 24.0, 28.0]:
    strength = 1.0 if st_time in [0.2, 8.0, 16.0, 24.0] else 0.6
    strike_bronze_drum(st_time, strength)

bgm = drone + drum_track
fade_in = np.minimum(1.0, np.linspace(0, 1.0, int(1.5 * sr)))
bgm[:len(fade_in)] *= fade_in
fade_out = np.minimum(1.0, np.linspace(1.0, 0, int(2.0 * sr)))
bgm[-len(fade_out):] *= fade_out
bgm = bgm / (np.max(np.abs(bgm)) + 1e-6) * 0.32

import wave
bgm_int16 = (bgm * 32767).astype(np.int16)
bgm_path = os.path.join(adir, "dong_son_bgm_48k.wav")
with wave.open(bgm_path, "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sr)
    wf.writeframes(bgm_int16.tobytes())

# 3. Precise Timeline Assembly
# 0.8s into each 8.0s shot -> exactly 2.0s silent pause before each scene cut
s1, s2, s3, s4 = processed_files
filter_complex = (
    "[1:a]adelay=800|800,volume=1.35[v1];"
    "[2:a]adelay=8800|8800,volume=1.35[v2];"
    "[3:a]adelay=16800|16800,volume=1.40[v3];"
    "[4:a]adelay=24800|24800,volume=1.35[v4];"
    "[0:a]volume=0.32[bg];"
    "[bg][v1][v2][v3][v4]amix=inputs=5:duration=longest:dropout_transition=1[aout]"
)

full_audio_out = os.path.join(adir, "cit_full_soundtrack_48k.wav")
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
    "-ar", "48000",
    full_audio_out
]
subprocess.run(cmd_audio, check=True)
print("Mixed 48kHz CIT Voiceover + Dong Son Bronze Drum Soundtrack!")

# 4. Mux into Master Video
master_video = os.path.join(vdir, "banh_chung_tap_1_rough_cut.mp4")
final_video = os.path.join(vdir, "banh_chung_tap_1_cit_voice.mp4")
art_final_video = os.path.join(art_dir, "banh_chung_tap_1_cit_voice.mp4")
sb_final_video = os.path.join(storyboard_media, "banh_chung_tap_1_cit_voice.mp4")

cmd_mux = [
    "ffmpeg", "-y",
    "-i", master_video,
    "-i", full_audio_out,
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "256k",
    "-shortest",
    final_video
]
subprocess.run(cmd_mux, check=True)

shutil.copy2(final_video, art_final_video)
shutil.copy2(final_video, sb_final_video)
print(f"CIT Voice Studio Film created successfully!")
print(f"File: {final_video}")
print(f"Size: {os.path.getsize(final_video)} bytes")
