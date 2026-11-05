import os, subprocess, shutil

v1 = r'D:\Nghia\Truyen co tich\assets\videos\tap1\shot_04_lang_lieu.mp4'
v2 = r'C:\Users\nghiabh\flow-mcp-out\Preview_Scene4_Video\scene-01.mp4'
audio = r'D:\Nghia\Truyen co tich\assets\audio\preview_scene4_audio.mp3'
out_video = r'D:\Nghia\Truyen co tich\assets\videos\tap1\preview_scene4_multishot.mp4'
art_video = r'C:\Users\nghiabh\.gemini\antigravity\brain\da7e6bcc-ec25-40e6-bc5c-8dfa02d4e056\preview_scene4_multishot.mp4'
sb_video = r'C:\Users\nghiabh\.agent-storyboard\projects\project-mw3167g1-kt97m4\media\preview_scene4_multishot.mp4'

# 1. First, make sure each clip has exactly 8.8s or loop/tpad slightly so combined = 17.4s
# v1: 0s to 8.8s (Shot 4A: Medium shot)
# v2: 8.5s to 17.4s (Shot 4B: Close-up)
# Let's slow each video slightly or extend with tpad to 8.8s each
filter_script = (
    "[0:v]setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=1.5[v0];"
    "[1:v]setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=1.5[v1];"
    "[v0][v1]xfade=transition=fade:duration=0.6:offset=8.5[vtrans]"
)

cmd = [
    "ffmpeg", "-y",
    "-i", v1,
    "-i", v2,
    "-i", audio,
    "-filter_complex", filter_script,
    "-map", "[vtrans]",
    "-map", "2:a:0",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    "-t", "17.42",
    out_video
]

print("Assembling multi-shot preview...")
subprocess.run(cmd, check=True)

shutil.copy2(out_video, art_video)
shutil.copy2(out_video, sb_video)
print("Preview Multi-shot Scene created successfully!")
print("File:", out_video)
print("Size:", os.path.getsize(out_video), "bytes")
