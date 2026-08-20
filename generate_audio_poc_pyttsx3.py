import os
import pyttsx3
from pydub import AudioSegment

def text_to_speech_mac(text, output_mp3="pocpyttsx3.mp3"):
    temp_aiff = "temp_speech.aiff"
    
    # 1. Initialize Engine
    engine = pyttsx3.init()
    
    # 2. Adjust Rate/Volume if needed
    engine.setProperty('rate', 160)
    
    # 3. Save to native macOS AIFF format
    engine.save_to_file(text, temp_aiff)
    engine.runAndWait()
    
    # 4. Convert AIFF -> MP3 via pydub
    if os.path.exists(temp_aiff):
        sound = AudioSegment.from_file(temp_aiff, format="aiff")
        sound.export(output_mp3, format="mp3", bitrate="128k")
        os.remove(temp_aiff) # Clean up temp file
        print(f"✅ Successfully converted full text to {output_mp3}")
    else:
        print("❌ Error: Speech generation failed.")

# Test Execution
if __name__ == "__main__":
    with open("output.md", "r", encoding="utf-8") as f:
        text = f.read()
    
    text_to_speech_mac(text, output_mp3="pocpyttsx3.mp3")