import logging
import os
import uuid
import asyncio
import edge_tts
import config
import re
import gc

logger = logging.getLogger(__name__)

# Aggressively reduced block sizing for absolute minimum static heap consumption
CHUNK_TARGET_CHARS = 1500

def split_into_chunks(text: str, target_size: int = CHUNK_TARGET_CHARS):
    """Splits text intelligently by double-newline paragraph clusters."""
    paragraphs = re.split(r'\n\s*\n', text)
    
    chunks = []
    current_chunk = []
    current_len = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        para_len = len(para)
        
        # Hard overflow safety: if a single paragraph is already longer than target, push it immediately
        if para_len > target_size:
             if current_chunk:
                 chunks.append("\n\n".join(current_chunk))
                 current_chunk = []
                 current_len = 0
             chunks.append(para)
             continue

        if current_chunk and (current_len + para_len) > target_size:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_len = para_len
        else:
            current_chunk.append(para)
            current_len += para_len

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
        
    return chunks

async def _process_single_chunk(chunk_text: str, voice: str, index: int):
    """Strictly serialized memory-managed synthesizer step."""
    filename = f"{uuid.uuid4().hex}_{index}.mp3"
    output_path = os.path.join(config.AUDIO_DIR, filename)
    
    timings = []
    
    try:
        communicate = edge_tts.Communicate(chunk_text, voice)
        # Direct streaming IO minimized stack retention
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
        
        duration = timings[-1]["end"] if timings else 0
            
        # REMOVE text from response to save critical RAM
        return {
            "success": True,
            "filename": filename,
            "duration": duration,
            "timings": timings
        }
    except Exception as e:
        logger.error(f"Memory Safe Skip on chunk {index}: {e}")
        return {"success": False, "error": str(e)}

async def _synthesize_all_chunks(text_chunks: list, voice: str):
    """Executes strictly sequential iteration to guarantee fixed memory footprint."""
    results = []
    
    total = len(text_chunks)
    for idx, c in enumerate(text_chunks):
        logger.info(f"Processing stable chunk {idx+1}/{total}...")
        
        # Standard awaited linear pipeline - no concurrency overhead!
        res = await _process_single_chunk(c, voice, idx)
        results.append(res)
        
        # Explicit scheduler yielding allows network stack handling without context-swapping memory hits
        await asyncio.sleep(0.05)
        
        # Free dynamic memory immediately
        if idx % 2 == 0:
             gc.collect()
             
    return results

def generate_audio(text: str, voice_type="female"):
    """
    Low-Memory Static synthesis engine.
    Strictly sequential to fit hard Cloud runtime resource ceilings.
    Returns standardized playlist arrays.
    """
    text = text.strip()
    if not text:
        raise ValueError("Text payload empty.")

    text_chunks = split_into_chunks(text)
    logger.info(f"Memory Optimized Pipeline. Total chunks: {len(text_chunks)}")

    voice = "en-US-AvaNeural" if voice_type == "female" else "en-US-GuyNeural"

    try:
        # Clear pre-run heap
        gc.collect()
        
        chunk_results = asyncio.run(_synthesize_all_chunks(text_chunks, voice))
    except Exception as e:
        logger.error(f"Pipeline OOM Safe Fail: {e}")
        raise RuntimeError("Optimized stable synthesizer encountered a blocking fault.")

    # Unload text chunks from RAM immediately
    del text_chunks
    gc.collect()

    valid_manifest = []
    for res in chunk_results:
        if res.get("success"):
            valid_manifest.append({
                "audio_filename": res["filename"],
                "duration": res["duration"],
                "timings": res["timings"]
            })
            
    # Final memory disposal
    del chunk_results
    gc.collect()

    if not valid_manifest:
        raise RuntimeError("Stability Mode: synthesis returned zero valid chunks.")

    logger.info(f"Finalized playlist. Safe memory output: {len(valid_manifest)} chunks.")
    return valid_manifest