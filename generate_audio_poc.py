from gtts import gTTS
import os

def text_to_speech(text, output_file="output.mp3", lang="en"):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(output_file)
    print(f"Saved speech to {output_file}")

# Example: Convert output.md to speech
with open("output.md", "r", encoding="utf-8") as f:
    text = f.read()
text_to_speech(text, output_file="poc.mp3", lang="en")
