import asyncio
import edge_tts

async def test_submaker():
    communicate = edge_tts.Communicate("Hello world, this is a test.", "en-US-EricNeural")
    submaker = edge_tts.SubMaker()
    
    async for chunk in communicate.stream():
        print(chunk["type"])
        if chunk["type"] == "WordBoundary":
            print("Found word boundary:", chunk)
            submaker.create_sub(chunk, "WordBoundary") # Wait, submaker actually creates subtitles differently?
            # Let's inspect submaker methods and see if feed() takes chunk, or submaker.create_sub()
            
    # Try feeding it a WordBoundary if it was feed()
    # Actually wait, maybe look at submaker source or see if get_srt() prints it.

if __name__ == "__main__":
    asyncio.run(test_submaker())
