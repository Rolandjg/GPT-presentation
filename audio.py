import edge_tts

def generate_audio(file_name, text, voice, speed):
    communicate = edge_tts.Communicate(text, voice, rate=speed)
    communicate.save_sync(file_name)

if __name__ == "__main__":
    generate_audio("test.mp3", "This is a test generation, hopefully it doesn't sound too bad.", "en-US-AnaNeural", "+40%")
