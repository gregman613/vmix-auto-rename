import os
import sys
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

VMIX_API_URL = "http://127.0.0.1:8088/api/"
REPLACE_ONLY = True  # True: replace only 'vMix_LAST_RECORD'; False: always rebuild name

# --- Resolve script dir for log ---
SCRIPT_DIR = Path(__file__).resolve().parent
LOG_PATH = SCRIPT_DIR / "pmc_log.txt"

def log(msg: str) -> None:
    try:
        LOG_PATH.write_text(LOG_PATH.read_text(encoding="utf-8") + f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}\n", encoding="utf-8")
    except FileNotFoundError:
        LOG_PATH.write_text(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}\n", encoding="utf-8")

def getenv_list(name: str):
    val = os.getenv(name, "").strip()
    if not val:
        return []
    return [item.strip() for item in val.split(",") if item.strip()]

def main():
    # --- Args ---
    if len(sys.argv) < 1 + 1:
        log("❌ No project name provided (argv[1]).")
        sys.exit(1)
    project_name = sys.argv[1]

    # --- Secrets from env ---
    telegram_token = os.getenv("TELEGRAM_TOKEN", "").strip()
    telegram_chat_ids = getenv_list("TELEGRAM_CHAT_IDS")
    if not telegram_token or not telegram_chat_ids:
        log("❌ TELEGRAM_TOKEN or TELEGRAM_CHAT_IDS not set.")
        # continue renaming even if telegram is missing? choose to continue and only skip telegram
        # sys.exit(1)

    log(f"▶ Start: project_name={project_name}")

    # --- vMix API ---
    try:
        resp = requests.get(VMIX_API_URL, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        log(f"❌ vMix API error: {e}")
        sys.exit(1)

    # --- Parse XML ---
    try:
        root = ET.fromstring(resp.text)
        recording = root.find("recording")
    except Exception as e:
        log(f"❌ XML parse error: {e}")
        sys.exit(1)

    if recording is None or "filename1" not in recording.attrib:
        log("❌ Recording filename not found in XML.")
        sys.exit(1)

    original_path = recording.attrib["filename1"]
    log(f"Found file: {original_path}")

    # --- Derive new name ---
    # We do NOT hard-code any base folders; we construct new name relative to original.
    original = Path(original_path)
    folder = original.parent
    ext = original.suffix or ".mp4"
    date_str = datetime.now().strftime("%d-%B-%Y")

    new_filename = None

    if REPLACE_ONLY and "vMix_LAST_RECORD" in original.name:
        new_filename = original.name.replace("vMix_LAST_RECORD", project_name, 1)
    else:
        new_filename = f"{project_name} - {date_str}{ext}"

    new_path = folder / new_filename

    # --- Rename ---
    try:
        os.replace(str(original), str(new_path))
        log(f"✅ Renamed to: {new_path}")
    except Exception as e:
        log(f"❌ Rename failed: {e}")
        sys.exit(1)

    # --- Telegram notify ---
    if telegram_token and telegram_chat_ids:
        text = f"🎬 vMix recording:\n`{new_filename}`"
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

        for chat_id in telegram_chat_ids:
            try:
                requests.get(url, params={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown"
                }, timeout=5)
                log(f"✅ Telegram sent to {chat_id}")
            except Exception as e:
                log(f"❌ Telegram error ({chat_id}): {e}")
    else:
        log("ℹ️ Telegram skipped (no token or chat IDs).")

    log("🏁 Done.\n")

if __name__ == "__main__":
    main()