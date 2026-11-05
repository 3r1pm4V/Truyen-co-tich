import os
import sys
import subprocess
import json

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"D:\Nghia\Truyen co tich"
STILLS_DIR = os.path.join(BASE_DIR, r"assets\concept_stills\ghibli_fullstory")
CLIPS_DIR = os.path.join(BASE_DIR, r"assets\videos\ghibli_clips")
OUTPUT_VIDEO = os.path.join(BASE_DIR, r"assets\videos\banh_chung_banh_giay_ghibli_full_movie.mp4")
ARTIFACT_DIR = r"C:\Users\nghiabh\.gemini\antigravity\brain\da7e6bcc-ec25-40e6-bc5c-8dfa02d4e056"
MASTER_AUDIO = os.path.join(BASE_DIR, r"assets\audio\voiceover_master_su_tich_banh_chung_banh_giay.mp3")
BGM_AUDIO = os.path.join(BASE_DIR, r"assets\audio\tap1\dong_son_bgm.wav")

os.makedirs(CLIPS_DIR, exist_ok=True)

# 11 shots configuration matching exact 147.32s master audio with 0.6s crossfades
# Total audio = 147.32s
# 10 transitions of 0.6s = 6.0s overlap
# Sum of clip durations = 147.32 + 6.0 = 153.32s
shots = [
    {
        "id": "shot_01",
        "file": os.path.join(STILLS_DIR, "scene-01.jpeg"),
        "duration": 10.6,
        "motion": "zoom_in"  # Slow push-in
    },
    {
        "id": "shot_02",
        "file": os.path.join(STILLS_DIR, "scene-02.jpeg"),
        "duration": 13.6,
        "motion": "pan_right"  # Pan towards King Hung
    },
    {
        "id": "shot_03",
        "file": os.path.join(STILLS_DIR, "ghibli_fs_03_tim_san_vat_dongson.jpeg"),
        "duration": 8.6,
        "motion": "pan_left"  # Pan along river
    },
    {
        "id": "shot_04",
        "file": os.path.join(STILLS_DIR, "scene-04.jpeg"),
        "duration": 17.6,
        "motion": "zoom_in"  # Gentle push-in on Lang Lieu
    },
    {
        "id": "shot_05a",
        "file": os.path.join(STILLS_DIR, "scene-05.jpeg"),
        "duration": 15.6,
        "motion": "zoom_in"  # Sleeping prince
    },
    {
        "id": "shot_05b",
        "file": os.path.join(STILLS_DIR, "scene-06.jpeg"),
        "duration": 15.6,
        "motion": "tilt_up"  # Tilt towards celestial deity
    },
    {
        "id": "shot_06a",
        "file": os.path.join(STILLS_DIR, "scene-07.jpeg"),
        "duration": 14.6,
        "motion": "zoom_in"  # Wrapping cakes
    },
    {
        "id": "shot_06b",
        "file": os.path.join(STILLS_DIR, "scene-08.jpeg"),
        "duration": 14.6,
        "motion": "pan_right"  # Bonfire and night sky
    },
    {
        "id": "shot_07a",
        "file": os.path.join(STILLS_DIR, "ghibli_fs_09_hoi_thi_dongson.jpeg"),
        "duration": 14.6,
        "motion": "pan_left"  # Council offering
    },
    {
        "id": "shot_07b",
        "file": os.path.join(STILLS_DIR, "scene-10.jpeg"),
        "duration": 18.6,
        "motion": "zoom_in"  # Royal succession
    },
    {
        "id": "shot_08",
        "file": os.path.join(STILLS_DIR, "scene-11.jpeg"),
        "duration": 9.92,
        "motion": "pull_out"  # Pull-out on Tet family
    }
]

print("=== STEP 1: RENDERING 11 HIGH-RESOLUTION GHIBLI CLIPS ===")
rendered_clips = []
for i, s in enumerate(shots):
    out_clip = os.path.join(CLIPS_DIR, f"{s['id']}.mp4")
    dur = s['duration']
    frames = int(dur * 30)
    
    # Define camera motion filter
    if s['motion'] == "zoom_in":
        # Slow push-in
        vf = f"scale=2304:1296,crop=1920:1080:'(in_w-out_w)/2':'(in_h-out_h)/2',zoompan=z='min(zoom+0.0003,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps=30,format=yuv420p"
    elif s['motion'] == "pull_out":
        # Slow pull-out
        vf = f"scale=2304:1296,crop=1920:1080:'(in_w-out_w)/2':'(in_h-out_h)/2',zoompan=z='max(1.10-0.0003*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps=30,format=yuv420p"
    elif s['motion'] == "pan_right":
        # Smooth pan right
        vf = f"scale=2304:1296,crop=1920:1080:'(in_w-out_w)*(t/{dur})':'(in_h-out_h)/2',format=yuv420p"
    elif s['motion'] == "pan_left":
        # Smooth pan left
        vf = f"scale=2304:1296,crop=1920:1080:'(in_w-out_w)*(1-t/{dur})':'(in_h-out_h)/2',format=yuv420p"
    elif s['motion'] == "tilt_up":
        # Smooth tilt up
        vf = f"scale=2304:1296,crop=1920:1080:'(in_w-out_w)/2':'(in_h-out_h)*(1-t/{dur})',format=yuv420p"
    else:
        vf = "scale=1920:1080,format=yuv420p"
        
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", s['file'],
        "-vf", vf,
        "-t", str(dur), "-r", "30",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        out_clip
    ]
    print(f"[{i+1}/11] Rendering {s['id']} ({dur}s)...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error rendering {s['id']}:", res.stderr)
        sys.exit(1)
    rendered_clips.append(out_clip)

print("\n=== STEP 2: CONCATENATING WITH 0.6s DISSOLVE TRANSITIONS (XFADE) ===")
# Build complex xfade filter graph
# 11 clips -> 10 xfades
inputs = []
for c in rendered_clips:
    inputs.extend(["-i", c])

filter_chains = []
# Calculate offsets
cur_offset = shots[0]['duration'] - 0.6
filter_chains.append(f"[0:v][1:v]xfade=transition=fade:duration=0.6:offset={cur_offset:.2f}[v1]")

for i in range(2, len(shots)):
    prev_v = f"[v{i-1}]"
    cur_v = f"[{i}:v]"
    next_v = f"[v{i}]" if i < len(shots) - 1 else "[v_final]"
    cur_offset += shots[i-1]['duration'] - 0.6
    filter_chains.append(f"{prev_v}{cur_v}xfade=transition=fade:duration=0.6:offset={cur_offset:.2f}{next_v}")

filter_str = ";".join(filter_chains)

temp_concat = os.path.join(CLIPS_DIR, "full_video_track_no_audio.mp4")
cmd_concat = [
    "ffmpeg", "-y"
] + inputs + [
    "-filter_complex", filter_str,
    "-map", "[v_final]",
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    temp_concat
]

print("Chaining 11 clips via xfade filter...")
res = subprocess.run(cmd_concat, capture_output=True, text=True)
if res.returncode != 0:
    print("Error during xfade concatenation:", res.stderr)
    sys.exit(1)
print(f"Video track assembled: {temp_concat}")

print("\n=== STEP 3: MUXING MASTER VOICEOVER + DONG SON SOUNDTRACK ===")
# Master voiceover: 100% volume
# BGM looped and attenuated to volume 0.16, with 4s fade-out at end
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

# Copy to artifacts directory
artifact_dest = os.path.join(ARTIFACT_DIR, "banh_chung_banh_giay_ghibli_full_movie.mp4")
import shutil
shutil.copyfile(OUTPUT_VIDEO, artifact_dest)
print(f" Copied to artifact directory:\n{artifact_dest}")

# Verify final duration
probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", OUTPUT_VIDEO]
dur_out = subprocess.check_output(probe_cmd).decode('utf-8').strip()
print(f"\nFinal Video Duration: {dur_out} seconds (Target: ~147.3s)")
