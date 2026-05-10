import logging
import os
import uuid
import asyncio
import edge_tts
import config
import re

logger = logging.getLogger(__name__)

# Target block sizing (keeps under Azure single-req throttling limits and optimizes cache)
CHUNK_TARGET_CHARS = 5000

def split_into_chunks(text: str, target_size: int = CHUNK_TARGET_CHARS):
    """Splits text intelligently by double-newline paragraph clusters."""
    # Split by double newline first
    paragraphs = re.split(r'\n\s*\n', text)
    
    chunks = []
    current_chunk = []
    current_len = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        para_len = len(para)
        
        # If adding this para pushes over target, and we have content, close current chunk
        if current_chunk and (current_len + para_len) > target_size:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_len = para_len
        else:
            current_chunk.append(para)
            current_len += para_len

    # Final sweep
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
        
    # Cap overall massive books dynamically if somehow enormous, for demo limits
    # Remove cap for final unlimited scaling:
    # return chunks[:30]  
    return chunks

async def _process_single_chunk(chunk_text: str, voice: str, index: int):
    """Internal parallel runner creating one audio artifact and list of cues."""
    filename = f"{uuid.uuid4().hex}_{index}.mp3"
    output_path = os.path.join(config.AUDIO_DIR, filename)
    
    timings = []
    
    try:
        communicate = edge_tts.Communicate(chunk_text, voice)
        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "SentenceBoundary":
                    start_sec = float(chunk["offset"]) / 10_000_000
                    dur_sec = float(chunk["duration"]) / 10_000_000
                    timings.append({
                        "start": start_sec,
                        "end": start_sec + dur_sec,
                        "text": chunk["text"]
                    })
        
        # Determine overall physical audio duration from the absolute last timing point
        duration = 0
        if timings:
            duration = timings[-1]["end"]
            
        return {
            "success": True,
            "filename": filename,
            "duration": duration,
            "timings": timings,
            "text": chunk_text
        }
    except Exception as e:
        logger.error(f"Error synthesizing chunk {index}: {e}")
        return {"success": False, "error": str(e)}

async def _synthesize_all_chunks(text_chunks: list, voice: str):
    """Executes mass asynchronous gathering."""
    tasks = [
        _process_single_chunk(c, voice, idx)
        for idx, c in enumerate(text_chunks)
    ]
    # Gather concurrently for ultra-high speed
    results = await asyncio.gather(*tasks)
    return results

def generate_audio(text: str, voice_type="female"):
    """
    Scalable Chunked Neural synthesis.
    Splits massive text, runs concurrent Cloud streams, outputs full manifest list.
    Returns a standardized list of valid chunk objects.
    """
    text = text.strip()
    if not text:
        raise ValueError("Text payload cannot be null.")

    text_chunks = split_into_chunks(text)
    logger.info(f"Starting Scaled Pipeline. Text broke into {len(text_chunks)} chapters.")

    voice = "en-US-AvaNeural" if voice_type == "female" else "en-US-GuyNeural"

    try:
        chunk_results = asyncio.run(_synthesize_all_chunks(text_chunks, voice))
    except Exception as e:
        logger.error(f"Pipeline Failure: {e}")
        raise RuntimeError("Mass orchestration stream failed.")

    # Validate results and clear missing steps
    valid_manifest = []
    for res in chunk_results:
        if res.get("success"):
            valid_manifest.append({
                "audio_filename": res["filename"],
                "duration": res["duration"],
                "timings": res["timings"],
                "text": res["text"]
            })
        else:
            logger.error(f"Skipping failed chunk entry: {res.get('error')}")

    if not valid_manifest:
        raise RuntimeError("Failed to synthesize any text chunks.")

    logger.info(f"Finalizing Playlist. Successfully output {len(valid_manifest)} chunks.")
    return valid_manifest