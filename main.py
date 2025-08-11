from html2image import Html2Image
import re
import os
import sys
import audio
from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_videoclips, ImageClip
import argparse
from openai import OpenAI
from dotenv import load_dotenv, dotenv_values

load_dotenv()
API_KEY = os.getenv("KEY")
MODEL = os.getenv("MODEL")
URL = os.getenv("URL")

prompt_file = open("prompt.txt")
prompt = f"Make a slideshow based on the following description:\n {sys.argv[1]}\n" + prompt_file.read()

def parse_args():
    args = argparse.ArgumentParser(description="Automated slideshow presentation maker.")
    args.add_argument("prompt", help="Prompt for slideshow") 
    args.add_argument("-o", "--output", default="output.mp4")
    args.add_argument("-r", "--resolution", type=lambda s: tuple(map(int, s.lower().split("x"))), default=(1920, 1080), metavar="WxH")
    args.add_argument("-v", "--voice", default="en-US-RogerNeural")
    args.add_argument("-s", "--speed", default="+0%", metavar="(+/-)n%", help="Speed of speech, for example, slow is -25%, quick is +25%")
    
    return args.parse_args()

# Generate function
def llm_call(prompt, client):
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a professional slideshow maker, you create interesting and pretty slideshows. Be sure to make sure that your tags are accurate."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

# Turn each slide into an image
def slides_to_images(slides, style, res):
    if not os.path.exists(os.path.abspath("slides")):
        os.mkdir("slides")

    hti = Html2Image(size=res)
    for i in range(len(slides)):
        output_path = f"slide_{i}.png" # Html2Image is a strange fella
        hti.screenshot(html_str=slides[i], css_str=style, save_as=output_path)
        os.rename(f"slide_{i}.png", f"slides/slide_{i}.png")

def create_movie(script, speaker, output_path):
    if not os.path.exists(os.path.abspath("audio")):
        os.mkdir("audio")

    if not os.path.exists(os.path.abspath("clips")):
        os.mkdir("clips")

    segments = re.findall(r"<slide_.*?>(.*?)</slide_.*?>", script, re.DOTALL)
    print(f"segments: {len(segments)}")
    clips = []

    for i in range(len(segments)):
        audio.generate_audio(f"audio/audio_{i}.mp3", segments[i], speaker)
        audio_clip = AudioFileClip(f"audio/audio_{i}.mp3")
        img = ImageClip(f"slides/slide_{i}.png").set_duration(audio_clip.duration+1) 
        video = img.set_audio(audio_clip)
        video.write_videofile(
            f"clips/clip_{i}.mp4",
            fps=4,
            codec="libx264",
            audio_codec="aac",
            bitrate="1000k"
        )
        clips.append(VideoFileClip(f"clips/clip_{i}.mp4"))

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        output_path,
        threads=4,
        codec="libx264",
        audio_codec="aac"
    )

if __name__=="__main__":
    args = parse_args()

    print(f"Creating slideshow with prompt: \n{sys.argv[1]}")
    print("Making API call (This might take a while)")
    client = OpenAI(
        api_key=API_KEY,
        base_url=URL
    )

    response = llm_call(prompt, client)
    print(response)

    # Extract parts
    script = re.search(r"<script>(.*?)</script>", response, re.DOTALL)
    slideshow = re.search(r"<slideshow>(.*?)</slideshow>", response, re.DOTALL)
    slides = re.findall(r"<slide_.*?>(.*?)</slide_.*?>", slideshow.group(1), re.DOTALL)
    style = re.search(r"<style>(.*?)</style>", response, re.DOTALL)

    slides_to_images(slides, style.group(1), args.resolution)
    create_movie(script.group(1), args.speaker, args.output)
