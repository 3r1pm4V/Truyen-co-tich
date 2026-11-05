import os
import sys
import subprocess
import shutil

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"D:\Nghia\Truyen co tich"
SHOTS_DIR = os.path.join(BASE_DIR, r"assets\videos\veo_ghibli_shots")
RETIMED_DIR = os.path.join(BASE_DIR, r"assets\videos\veo_retime_clips")
OUTPUT_VIDEO = os.path.join(BASE_DIR, r"assets\videos\banh_chung_banh_giay_veo_ghibli_full_movie.mp4")
ARTIFACT_DIR = r"C:\Users\nghiabh\.gemini\antigravity\brain\da7e6bcc-ec25-40e6-bc5c-8dfa02d4e056"
MASTER_AUDIO = os.path.join(BASE_DIR, r"assets\audio\voiceover_master_su_tich_banh_chung_banh_giay.mp3")
BGM_AUDIO = os.path.join(BASE_DIR, r"assets\audio\tap1\dong_son_bgm.wav")

os.makedirs(RETIMED_DIR, exist_ok=True)

# 11 Veo 3.1 shots matching exact 147.32s master audio timeline
shots_config = [
    {"name": "veo_shot_01_kinh_do.mp4", "target_dur": 10.6},
    {"name": "veo_shot_02_chi_du.mp4", "target_dur": 13.6},
    {"name": "veo_shot_03_tim_san_vat.mp4", "target_dur": 8.6},
    {"name": "veo_shot_04_lang_lieu.mp4", "target_dur": 17.6},
    {"name": "veo_shot_05a_hao_quang.mp4", "target_dur": 15.6},
    {"name": "veo_shot_05b_than_bao_mong.mp4", "target_dur": 15.6},
    {"name": "veo_shot_06a_goi_banh.mp4", "target_dur": 14.6},
    {"name": "veo_shot_06b_nau_banh.mp4", "target_dur": 14.6},
    {"name": "veo_shot_07a_hoi_thi.mp4", "target_dur": 14.6},
    {"name": "veo_shot_07b_truyen_ngoi.mp4", "target_dur": 18.6},
    {"name": "veo_shot_08_ngay_tet.mp4", "target_dur": 9.92}
]

print("=== STEP 1: RETIMING & UPSCALING 11 VEO 3.1 SHOTS TO 1080P ===")
retimed_files = []
for i, s in enumerate(shots_config):
    src = os.path.join(SHOTS_DIR, s['name'])
    out_file = os.path.join(RETIMED_DIR, f"retime_{i+1:02d}_{s['name']}")
    target_dur = s['target_dur']
    
    # Get original duration
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", src]
    orig_dur = float(subprocess.check_output(probe_cmd).decode('utf-8').strip())
    
    pts_factor = target_dur / orig_dur
    vf = f"setpts={pts_factor:.6f}*PTS,scale=1920:1080:flags=lanczos,fps=30,format=yuv420p"
    
    cmd = [
        "ffmpeg", "-y", "-i", src,
        "-vf", vf,
        "-t", str(target_dur),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        out_file
    ]
    print(f"[{i+1}/11] Retiming {s['name']} ({orig_dur:.2f}s -> {target_dur:.2f}s)...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error retiming {s['name']}:", res.stderr)
        sys.exit(1)
    retimed_files.append(out_file)

print("\n=== STEP 2: CONCATENATING VIA XFADE DISSOLVE TRANSITIONS (0.6s) ===")
inputs = []
for f in retimed_files:
    inputs.extend(["-i", f])

filter_chains = []
cur_offset = shots_config[0]['target_dur'] - 0.6
filter_chains.append(f"[0:v][1:v]xfade=transition=fade:duration=0.6:offset={cur_offset:.2f}[v1]")

for i in range(2, len(shots_config)):
    prev_v = f"[v{i-1}]"
    cur_v = f"[{i}:v]"
    next_v = f"[v{i}]" if i < len(shots_config) - 1 else "[v_final]"
    cur_offset += shots_config[i-1]['target_dur'] - 0.6
    filter_chains.append(f"{prev_v}{cur_v}xfade=transition=fade:duration=0.6:offset={cur_offset:.2f}{next_v}")

filter_str = ";".join(filter_chains)

temp_concat = os.path.join(RETIMED_DIR, "full_veo_video_no_audio.mp4")
cmd_concat = [
    "ffmpeg", "-y"
] + inputs + [
    "-filter_complex", filter_str,
    "-map", "[v_final]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    temp_concat
]

print("Assembling 11 Veo clips into full video track...")
res = subprocess.run(cmd_concat, capture_output=True, text=True)
if res.returncode != 0:
    print("Error during concatenation:", res.stderr)
    sys.exit(1)
print(f"Video track assembled: {temp_concat}")

print("\n=== STEP 3: MUXING MASTER VOICEOVER + DONG SON SOUNDTRACK ===")
cmd_audio = [
    "ffmpeg", "-y",
    "-i", temp_concat,
    "-i", MASTER_AUDIO,
    "-stream_loop", "-1", "-i", BGM_AUDIO,
    "-filter_complex",
    "[2:a]volume=0.16,afade=t=out:st=143:d=4[bgm];[1:a][bgm]amix=inputs=2:duration=first[aout]",
    "-map", "0:v",
    "-map", "[aout]",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "256k",
    "-shortest",
    OUTPUT_VIDEO
]

print("Muxing final audio-video master...")
res = subprocess.run(cmd_audio, capture_output=True, text=True)
if res.returncode != 0:
    print("Error during audio muxing:", res.stderr)
    sys.exit(1)

print(f"\n Masterpiece successfully rendered to:\n{OUTPUT_VIDEO}")

# Copy to artifact directory
artifact_dest = os.path.join(ARTIFACT_DIR, "banh_chung_banh_giay_veo_ghibli_full_movie.mp4")
shutil.copyfile(OUTPUT_VIDEO, artifact_dest)
print(f" Copied to artifact directory:\n{artifact_dest}")

# Verify final duration
probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", OUTPUT_VIDEO]
dur_out = subprocess.check_output(probe_cmd).decode('utf-8').strip()
print(f"\nFinal Video Duration: {dur_out} seconds (Target: ~147.3s)")
