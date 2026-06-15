"""
Post-processing for ThSL Bridge — runs after a sentence is finished.

Pipeline:
    word list  →  Typhoon LLM (natural Thai sentence)  →  gTTS (spoken aloud)

Designed to DEGRADE GRACEFULLY:
  - No Typhoon API key / no internet  → falls back to the raw joined words
  - gTTS fails                        → prints the sentence, keeps running

Typhoon API key:  put it in either
  - environment variable  TYPHOON_API_KEY
  - or a file  scripts/typhoon_key.txt  (one line, just the key)

Used by predict_stream.py:  import postprocess; postprocess.process(word_buffer)
"""
import os
import time
import glob
import json
import urllib.request

TYPHOON_URL   = "https://api.opentyphoon.ai/v1/chat/completions"
TYPHOON_MODEL = "typhoon-v2.5-30b-a3b-instruct"   # current Typhoon instruct model
KEY_FILE      = os.path.join(os.path.dirname(__file__), "typhoon_key.txt")
TTS_DIR       = "D:/KachornThSL/temp"


def _get_key():
    """Read the Typhoon API key from env var or key file. Returns None if absent."""
    key = os.environ.get("TYPHOON_API_KEY")
    if key:
        return key.strip()
    try:
        with open(KEY_FILE, encoding="utf-8") as f:
            return f.read().strip() or None
    except FileNotFoundError:
        return None


def build_sentence(words):
    """Turn a list of ThSL words into a natural Thai sentence via Typhoon.
    Falls back to space-joined words if no key or the call fails."""
    raw = " ".join(words)
    key = _get_key()
    if not key:
        print("[typhoon] no API key — using raw words")
        return raw

    prompt = (
        "คุณเป็นผู้ช่วยแปลงคำจากภาษามือไทยให้เป็นประโยคภาษาไทยที่เป็นธรรมชาติ "
        "ฉันจะให้ลำดับคำที่ได้จากการแปลภาษามือ "
        "ช่วยเรียบเรียงให้เป็นประโยคสั้น ๆ ที่ถูกต้องและเป็นธรรมชาติ "
        "ตอบกลับเฉพาะประโยคเท่านั้น ห้ามอธิบายเพิ่ม\n"
        f"คำ: {raw}"
    )
    body = {
        "model": TYPHOON_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.3,
    }
    req = urllib.request.Request(
        TYPHOON_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            out = json.loads(resp.read().decode("utf-8"))
        sentence = out["choices"][0]["message"]["content"].strip()
        return sentence or raw
    except Exception as e:
        print(f"[typhoon] request failed: {e} — using raw words")
        return raw


def _play(mp3_path):
    """Play an mp3 file. Tries playsound, then falls back to the default player."""
    try:
        from playsound import playsound
        playsound(mp3_path)
        return
    except Exception:
        pass
    try:
        os.startfile(mp3_path)   # Windows fallback — opens default media player
    except Exception as e:
        print(f"[play] could not play audio: {e}")


def _cleanup_old_tts(keep_latest=3):
    """Delete old tts mp3s that are no longer locked (best-effort)."""
    files = sorted(glob.glob(os.path.join(TTS_DIR, "tts_*.mp3")))
    for old in files[:-keep_latest]:
        try:
            os.remove(old)
        except OSError:
            pass  # still locked by a player — leave it


def speak(text):
    """Speak Thai text aloud via Google TTS.
    Uses a unique filename per utterance so a still-open player from the
    previous sentence can't lock the next save (fixes Permission denied)."""
    try:
        from gtts import gTTS
        os.makedirs(TTS_DIR, exist_ok=True)
        mp3 = os.path.join(TTS_DIR, f"tts_{int(time.time()*1000)}.mp3")
        gTTS(text=text, lang="th").save(mp3)
        _play(mp3)
        _cleanup_old_tts()
    except Exception as e:
        print(f"[gtts] failed: {e}")


def process(words):
    """Full post-process: words → natural sentence → spoken aloud. Returns the sentence."""
    if not words:
        return ""
    sentence = build_sentence(words)
    print(f"[postprocess] {words}  →  {sentence}")
    speak(sentence)
    return sentence


if __name__ == "__main__":
    # quick manual test
    process(["ฉัน", "ต้องการ", "ช่วย"])
