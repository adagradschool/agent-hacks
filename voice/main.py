"""
hold_space_to_talk.py
Press-and-hold <space>  → record
Release                 → transcribe + TTS reply
Press <esc>             → quit
"""
import io, queue, threading, sounddevice as sd, soundfile as sf
from pynput import keyboard
from elevenlabs.client import ElevenLabs
from elevenlabs import play

# ── CONFIG ───────────────────────────────────────────────────────────
SR        = 16_000          # sample-rate expected by ElevenLabs STT
VOICE_ID  = "JBFqnCBsd6RMkjVDRZzb"
TTS_MODEL = "eleven_multilingual_v2"
client    = ElevenLabs()    # uses ELEVEN_API_KEY env var
# ─────────────────────────────────────────────────────────────────────

frames_q   = queue.Queue()  # audio frames from the callback
recording  = threading.Event()
terminate  = threading.Event()


def agent(prompt: str) -> str:
    """Stub – replace with Langflow / LangChain call."""
    return f"I heard: {prompt}"


def audio_callback(indata, *_):
    """Called by sounddevice for every block."""
    if recording.is_set():
        frames_q.put(indata.copy())


def keyboard_listener():
    """Runs in a background thread, toggling the recording flag."""
    def on_press(key):
        if key == keyboard.Key.space:
            recording.set()        # start capturing
        elif key == keyboard.Key.esc:
            terminate.set()        # exit program

    def on_release(key):
        if key == keyboard.Key.space:
            recording.clear()      # stop capturing

    with keyboard.Listener(on_press=on_press, on_release=on_release):
        terminate.wait()           # blocks until esc pressed


def flush_frames_to_wav() -> io.BytesIO:
    """Pulls all frames collected so far → BytesIO WAV buffer."""
    if frames_q.empty():
        return None
    import numpy as np
    buf  = io.BytesIO()
    data = np.concatenate(list(frames_q.queue))
    frames_q.queue.clear()
    sf.write(buf, data, SR, format="WAV", subtype="PCM_16")
    buf.seek(0)
    return buf


# ── MAIN LOOP ────────────────────────────────────────────────────────
threading.Thread(target=keyboard_listener, daemon=True).start()

with sd.InputStream(samplerate=SR, channels=1, dtype="int16",
                    callback=audio_callback):
    print("Hold <space> and speak.  Press <esc> to quit.")
    while not terminate.is_set():
        if recording.is_set():
            sd.sleep(50)           # user is still talking
            continue

        wav_buf = flush_frames_to_wav()
        if not wav_buf:
            sd.sleep(50)
            continue               # nothing recorded

        # ── ElevenLabs Speech-to-Text ───────────────────────────────
        result = client.speech_to_text.convert(
            file=wav_buf,
            model_id="scribe_v1", # Model to use, for now only "scribe_v1" is supported
            tag_audio_events=False, # Tag audio events like laughter, applause, etc.
            language_code="eng", # Language of the audio file. If set to None, the model will detect the language automatically.
            diarize=False, # Whether to annotate who is speaking
        )
        text   = result.text.strip()
        if not text:
            continue
        print(f"👤 {text}")

        # ── Your agent’s reply ─────────────────────────────────────
        reply  = agent(text)

        # ── ElevenLabs TTS (streaming) ─────────────────────────────
        audio = client.text_to_speech.convert(
            text=reply,
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        play(audio)                # blocks until done

print("Goodbye!")

