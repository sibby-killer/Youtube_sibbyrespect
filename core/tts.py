import os
import asyncio
import edge_tts
from config import TEMP_DIR

VOICE = "en-US-EricNeural"  # Energetic, conversational male voice

async def _generate_audio(text: str, output_path: str, srt_path: str):
    """
    Internal async function to generate audio and subtitles using edge-tts
    """
    # Use edge-tts to generate high-quality voiceover
    # Increase rate by 15% to sound more like a fast-talking human TikToker
    communicate = edge_tts.Communicate(text, VOICE, rate="+15%", boundary="WordBoundary")
    submaker = edge_tts.SubMaker()
    
    with open(output_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
                
    with open(srt_path, "w", encoding="utf-8") as sub_file:
        sub_file.write(submaker.get_srt())

def generate_voiceover(text: str, filename="voiceover.mp3"):
    """
    Generates an MP3 voiceover and SRT from text and saves it to the temp directory.
    Returns the tuple of absolute paths: (audio_path, srt_path).
    """
    output_path = os.path.join(TEMP_DIR, filename)
    srt_filename = filename.rsplit('.', 1)[0] + ".srt"
    srt_path = os.path.join(TEMP_DIR, srt_filename)
    
    print(f"Generating voiceover: {output_path} and {srt_path}")
    
    # Run the async edge-tts command
    asyncio.run(_generate_audio(text, output_path, srt_path))
    
    print("Voiceover and subtitles generated successfully.")
    return output_path, srt_path

if __name__ == "__main__":
    # Test
    test_text = "Did you know that the Benjamin Franklin effect relies on a cognitive dissonance loophole in your brain? By asking a hater for a small favor, their brain rewires itself to actually like you."
    generate_voiceover(test_text)
