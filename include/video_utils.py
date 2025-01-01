
import os, time
import json as JS
import requests
from os.path import isfile
from pprint import pprint as pp
from pprint import pformat
from os.path import join   , isdir 
import subprocess
from moviepy.editor import VideoFileClip


def check_video_length(file_path, max_length_seconds=90):
    try:
        clip = VideoFileClip(file_path)
        duration = clip.duration
        clip.close()
        
        if duration > max_length_seconds:
            print(f"Video is longer than {max_length_seconds} seconds. Duration: {duration:.2f} seconds")
            return False, duration
        else:
            print(f"Video is within the {max_length_seconds} second limit. Duration: {duration:.2f} seconds")
            return True, duration
    
    except Exception as e:
        print(f"An error occurred while checking video length: {str(e)}")
        return False, None


def shorten_and_resize_video(file_path, max_length_seconds=90, min_height=960):
    try:
        # Get video information without fully loading the clip
        video_info = VideoFileClip(file_path)
        duration = video_info.duration
        original_width = video_info.w
        original_height = video_info.h
        video_info.close()

        if duration <= max_length_seconds and original_height >= min_height:
            print("Video is already within the time limit and meets height requirement. No changes made.")
            return file_path

        # Generate new filename
        base, ext = os.path.splitext(file_path)
        new_file_path = f"{base}_shortened_resized{ext}"

        # Calculate new dimensions
        if original_height < min_height:
            new_height = min_height
            new_width = int(original_width * (new_height / original_height))
            new_width = new_width - (new_width % 2)  # Ensure even width for video encoding
        else:
            new_height = original_height
            new_width = original_width

        # Construct FFmpeg command
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", file_path,
            "-t", str(max_length_seconds),
            "-vf", f"scale={new_width}:{new_height}:force_original_aspect_ratio=decrease,pad={new_width}:{new_height}:(ow-iw)/2:(oh-ih)/2",
            "-c:a", "copy",
            new_file_path
        ]

        # Execute FFmpeg command
        subprocess.run(ffmpeg_cmd, check=True)

        print(f"Video has been processed. New file: {new_file_path}")
        print(f"New dimensions: {new_width}x{new_height}")
        return new_file_path

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while processing the video: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        
        raise e

def process_video_for_facebook_reels(file_path, max_length_seconds=89, min_height=960, target_aspect_ratio=9/16, min_fps=23):
    try:
        # Get video information without fully loading the clip
        video_info = VideoFileClip(file_path)
        duration = video_info.duration
        original_width = video_info.w
        original_height = video_info.h
        original_aspect_ratio = original_width / original_height
        original_fps = video_info.fps
        video_info.close()

        if (duration <= max_length_seconds and 
            original_height >= min_height and 
            abs(original_aspect_ratio - target_aspect_ratio) < 0.01 and
            original_fps >= min_fps):
            print("Video already meets all requirements. No changes made.")
            return file_path

        # Generate new filename
        base, ext = os.path.splitext(file_path)
        new_file_path = f"{base}_processed_for_reels{ext}"
        directory, basename = os.path.split(new_file_path)

        print("Directory:", directory)
        print("Base Name:", basename)
        new_dir=join(directory,'processed') 
        if not isdir (new_dir):
            os.makedirs(new_dir)    
        new_file_path=join(new_dir, basename)   
        if isfile(new_file_path):
            print(f"File already exists: {new_file_path}")
            #delete file
            os.remove(new_file_path)
        assert not isfile(new_file_path),new_file_path
        # Calculate new dimensions
        new_height = max(min_height, original_height)
        new_width = int(new_height * target_aspect_ratio)
        new_width = new_width - (new_width % 2)  # Ensure even width for video encoding

        # Determine new frame rate
        new_fps = max(min_fps, original_fps)

        # Construct FFmpeg command
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", file_path,
            "-t", str(max_length_seconds),
            "-vf", f"scale={new_width}:{new_height}:force_original_aspect_ratio=decrease,pad={new_width}:{new_height}:(ow-iw)/2:(oh-ih)/2",
            "-r", str(new_fps),
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            new_file_path
        ]

        # Execute FFmpeg command
        subprocess.run(ffmpeg_cmd, check=True)

        print(f"Video has been processed. New file: {new_file_path}")
        print(f"New dimensions: {new_width}x{new_height}, New FPS: {new_fps}")
        return new_file_path

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while processing the video: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None


def validate_reel_for_facebook(file_path, max_length_seconds=90, min_height=960, target_aspect_ratio=9/16):
    try:
        # Get video information without fully loading the clip
        video_info = VideoFileClip(file_path)
        duration = video_info.duration
        width = video_info.w
        height = video_info.h
        aspect_ratio = width / height
        video_info.close()

        print(f"Video duration: {duration} seconds, dimensions: {width}x{height}, aspect ratio: {aspect_ratio:.2f}")

        if (duration <= max_length_seconds and 
            height >= min_height and 
            abs(aspect_ratio - target_aspect_ratio) < 0.01):
            print("Video meets all Facebook Reels requirements.")
            return file_path
        else:
            print("Video needs processing to meet Facebook Reels requirements. Processing...")
            return process_video_for_facebook_reels(file_path, max_length_seconds-1, min_height, target_aspect_ratio)

    except Exception as e:
        print(f"An error occurred while validating the video: {str(e)}")
        raise e
    
def validate_reel_length(file_path):
    assert isfile(file_path), file_path 
    length=90
    is_within_limit, duration = check_video_length(file_path,length)

    if not is_within_limit:
        print(f"Original video duration: {duration:.2f} seconds. Shortening video...")
        #shortened_file_path = shorten_and_resize_video(file_path)
        shortened_file_path = process_video_for_facebook_reels(file_path)
        if shortened_file_path:
            print(f"Video shortened successfully. New file: {shortened_file_path}")
            return shortened_file_path
        else:
            print("Failed to shorten video.")
            raise Exception("Failed to shorten video.")
    else:
        print("Video is already within the time limit.")    
        return file_path
