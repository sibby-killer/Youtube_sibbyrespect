import asyncio
import edge_tts

async def test_submaker():
    communicate = edge_tts.Communicate("Hello world, this is a test of edge tts submaker.", "en-US-EricNeural")
    submaker = edge_tts.SubMaker()
    
    with open("test.mp3", "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
                
    print("Methods available on submaker:")
    print(dir(submaker))
    
    print("Done testing submaker API.")

if __name__ == "__main__":
    asyncio.run(test_submaker())
