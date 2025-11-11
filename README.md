# vmix-auto-rename
Automatically renames vMix recording files based on API data and sends Telegram notifications when recording stops.

# vMix Auto Rename (Universal) & Telegram Notify

A small Python tool that **renames vMix recordings** when recording stops and **notifies Telegram**.  
Works cross‑platform (Windows/macOS/Linux). No hard‑coded paths, no IDs, no tokens in the repo.

---

## How it works

1. Trigger this script from **Bitfocus Companion** on vMix event **“On condition becoming false”** (recording stopped).
2. The script queries `http://127.0.0.1:8088/api/` to get the current recording path (`<recording filename1="...">`).
3. It builds the **new filename** using your *project name* (passed as the first CLI argument) and preserves the rest of the original name.
   - Default behavior: **replace only the substring `vMix_LAST_RECORD`** with your project name, keeping the rest intact.
   - If that substring is not found, it falls back to: `<project_name> - DD-Month-YYYY.ext`
4. Sends a Telegram message with the new filename in **Markdown** monospaced style.

---

## Requirements

- Python 3.8+
- Dependencies:
  ```bash
  pip install requests
  ```

---

## Configuration

This script uses **environment variables** (safer for secrets):

- `TELEGRAM_TOKEN` – your bot token, e.g. `123456:ABC-...`
- `TELEGRAM_CHAT_IDS` – comma‑separated chat IDs, e.g. `123456789,987654321`

You can export them in your shell, systemd service, Windows service, or set them inline:
```bash
# macOS/Linux example
export TELEGRAM_TOKEN="YOUR_TOKEN"
export TELEGRAM_CHAT_IDS="123456789,987654321"

# Windows PowerShell example
$env:TELEGRAM_TOKEN="YOUR_TOKEN"
$env:TELEGRAM_CHAT_IDS="123456789,987654321"
```

---

## Run from Bitfocus Companion

Use **Run shell path (local)** and point to your venv python + this script.

- macOS/Linux:
  ```bash
  /path/to/venv/bin/python /path/to/vmix_auto_rename.py "$(custom:project_name)"
  ```

- Windows (PowerShell or CMD; path is just an example):
  ```bash
  "C:\path\to\venv\Scripts\python.exe" "C:\path\to\vmix_auto_rename.py" "$(custom:project_name)"
  ```

> If Companion runs as a Windows service, set it to run **under your user account** so Python has network access for Telegram.

---

## Example Telegram message

```
🎬 vMix recording:
`MyProject - 11-November-2025.mp4`
```

---

## Notes

- Script writes a small log file next to itself (`pmc_log.txt`).
- Works without hard‑coded absolute paths; all paths are derived from the vMix API response.
- If you prefer full rename logic only, set `REPLACE_ONLY=False` inside the script.

---

## License

MIT
