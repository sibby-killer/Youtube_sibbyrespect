import os
import subprocess
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, vfx
from config import OUTPUT_DIR, TEMP_DIR

def stitch_video(audio_path: str, broll_paths: list, output_filename: str = "final_short.mp4", srt_path: str = None):
    """
    Takes an audio file and a list of B-roll video paths.
    Cuts and stitches the B-roll clips to match the exact duration of the audio.
    Outputs the final MP4 to the OUTPUT_DIR.
    """
    print("Starting video assembly...")
    
    if not os.path.exists(audio_path):
        print(f"Error: Audio file {audio_path} not found.")
        return None
        
    if not broll_paths:
        print("Error: No B-roll files provided.")
        return None

    try:
        audio = AudioFileClip(audio_path)
        total_duration = audio.duration
        
        # Calculate how long each clip should be (evenly split)
        # Note: A more advanced version would randomly cut clips or use exact scenes
        num_clips = len(broll_paths)
        clip_duration = total_duration / num_clips
        
        processed_clips = []
        for path in broll_paths:
            if not os.path.exists(path):
                print(f"Skipping {path} (not found).")
                continue
                
            clip = VideoFileClip(path)
            
            # If the downloaded clip is shorter than clip_duration, we loop it
            if clip.duration < clip_duration:
                clip = clip.fx(vfx.loop, duration=clip_duration)
            else:
                # Cut clip to the exact length needed
                clip = clip.subclip(0, clip_duration)
                
            # Resize and crop to standard Shorts/TikTok vertical format (1080x1920)
            # Moviepy resizing maintains aspect ratio by default, so we crop center
            w, h = clip.size
            target_ratio = 1080 / 1920.0
            clip_ratio = w / float(h)
            
            if clip_ratio > target_ratio:
                # Clip is too wide, crop width
                new_w = h * target_ratio
                clip = clip.crop(x_center=w/2, width=new_w)
            else:
                # Clip is too tall, crop height
                new_h = w / target_ratio
                clip = clip.crop(y_center=h/2, height=new_h)
                
            clip = clip.resize(newsize=(1080, 1920))
            processed_clips.append(clip)
            
        if not processed_clips:
            print("Error: Could not process any B-roll clips.")
            return None
            
        print("Concatenating video clips...")
        final_video = concatenate_videoclips(processed_clips, method="compose")
        
        print("Adding voiceover...")
        final_video = final_video.set_audio(audio)
        
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        if srt_path and os.path.exists(srt_path):
            temp_output = os.path.join(TEMP_DIR, "temp_no_subs.mp4")
            print(f"Rendering intermediate MP4 without subs to {temp_output}...")
            final_video.write_videofile(
                temp_output,
                fps=30,
                codec="libx264",
                audio_codec="aac",
                preset="ultrafast",
                threads=4
            )
            
            print("Burning dynamic SRT subtitles using FFmpeg...")
            # Windows FFmpeg subtitles filter path escaping:
            # 1. Use the absolute path
            # 2. Replace all backslashes with forward slashes  
            # 3. Escape ONLY the colon in the path (not in the drive letter)
            #    Format required: C\\:/Users/... → wrong; we must do: C\\:/path
            srt_abs = os.path.abspath(srt_path)
            # Split on the drive letter colon: 'C:' becomes prefix='C', rest='/Users/...'
            if len(srt_abs) >= 2 and srt_abs[1] == ':':
                drive   = srt_abs[0]           # e.g. 'C'
                rest    = srt_abs[2:].replace('\\', '/')
                ffmpeg_srt_path = f"{drive}\\\\:{rest}"
            else:
                ffmpeg_srt_path = srt_abs.replace('\\', '/')

            # Hormozi style: Yellow, Outline, Mid-Center, Bold
            # SSA Alignment 10 = Mid-Center
            style = "FontName=Arial,FontSize=26,PrimaryColour=&H00FFFF&,OutlineColour=&H000000&,Outline=2,Alignment=10,Bold=1"
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            
            ffmpeg_cmd = [
                ffmpeg_exe, "-y",
                "-i", temp_output,
                "-vf", f"subtitles={ffmpeg_srt_path}:force_style='{style}'",
                "-c:a", "copy",
                output_path
            ]
            subprocess.run(ffmpeg_cmd, check=True)
            
            if os.path.exists(temp_output):
                try:
                    os.remove(temp_output)
                except:
                    pass
            print(f"Video assembly complete! Saved to {output_path}")
        else:
            print(f"Rendering final MP4 to {output_path}...")
            # Render the video directly without subs
            final_video.write_videofile(
                output_path,
                fps=30,
                codec="libx264",
                audio_codec="aac",
                preset="ultrafast",
                threads=4
            )
            print(f"Video assembly complete! Saved to {output_path}")
        
        # Cleanup clips from memory
        for clip in processed_clips:
            clip.close()
        audio.close()
        final_video.close()
        
        return output_path

    except Exception as e:
        print(f"Error during video editing: {e}")
        return None
