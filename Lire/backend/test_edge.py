import asyncio
import edge_tts
import json

async def test_timing():
    text = "Hello this is a test. Let's see if timings work now."
    voice = "en-US-AvaNeural"
    communicate = edge_tts.Communicate(text, voice)
    
    timings = []
    try:
        with open("dummy.mp3", "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif "Boundary" in str(chunk["type"]):
                    print("DUMPING BOUNDARY:", json.dumps({k: str(v) for k, v in chunk.items()}, indent=2))
        print(json.dumps(timings, indent=2))
    except Exception as e:
        print("ERROR:", e)

    from pydub import AudioSegment
    sound = AudioSegment.from_file("dummy.mp3")
    print("ACTUAL AUDIO DURATION IN MILLISECONDS:", len(sound))

if __name__ == "__main__":
    asyncio.run(test_timing())
