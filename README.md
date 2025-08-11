## GPT-presentation
Create slideshow presentations with large language models

## Example with GLM-4.5
```bash
python main.py "What is FLIP fluids and how is it unique, on a technnical level" --speaker "en-US-AriaNeural"
```
https://github.com/user-attachments/assets/b849d10d-4bde-46c6-830c-4dabdcbe9134

## Running
- Clone this repo
- Populate .env
- pip install -r requirements.txt
- Run main.py

# Command line usage
## Positional arguments
- Prompt: Description of the video

## Flags
- TTS voice: -v --voice
- TTS speed: -s --speed
- Output file name: -o --output
- Resolution: -r --resolution

## Example
```bash
python3 main.py "What the hard problem of consciousness is" --output -r 1920x1080 "output.mp4" -v "en_US_AvaNeural" -s "+20%"
```

# Voices
```
edge-playback --list-voices
```

# Common problems
- Model hallucinates image links which fail to load.
