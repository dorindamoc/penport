# Penport 🖊️

> Bridge the gap between your fountain pen and your digital journal.

---

## The Problem

There's something irreplaceable about writing by hand. The friction of a fountain pen on paper, the slowness that forces you to think, the physical artifact of a filled notebook. Many people who journal seriously prefer paper — and then immediately face the problem of their writing being locked there, unsearchable, unbackable, invisible to the digital tools they use everywhere else.

The workarounds are all painful. Typing everything up defeats the purpose. Photo-to-text apps exist but they're generic, not designed for cursive handwriting, and dump raw OCR output that needs significant cleanup. Dedicated handwriting apps work well but require writing on a screen, which isn't the same thing.

Penport's position is simple: **keep writing on paper, let the computer do the digitization work**.

---

## How It Works

Penport runs quietly in your system tray, watching a local folder. When a new photo appears there, it runs it through a two-step AI pipeline and saves a clean, dated text file to your output folder.

```
📷 photograph your page
        ↓
📁 drop it in your inbox folder
        ↓
👁️  Penport detects the new image
        ↓
🧠 Step 1 — vision LLM transcribes the handwriting
        ↓
✏️  Step 2 — text LLM corrects misread words using context & language rules
        ↓
📄 clean dated text file saved to your output folder
```

### The inbox folder

The inbox is just a local folder on your machine. You can populate it however you like:

- Point it at a folder your cloud sync client (Proton Drive, iCloud, Google Drive, Dropbox, OneDrive) already maintains
- Transfer photos manually from your phone
- Use any automation tool you already have

This means Penport works with virtually any cloud storage setup without needing direct API access to it.

### The output folder

The output is also just a local folder. Point it wherever makes sense for you:

- An Obsidian vault
- A folder synced to your cloud storage
- A Diarium import folder
- Anywhere you keep notes

Each entry is saved as a plain `.txt` file named by date (`2026-04-18.txt`). Multiple entries on the same day are appended to the same file.

### The AI pipeline

Penport uses a **two-step pipeline** to maximize transcription accuracy:

1. **Transcription** — a multimodal vision LLM reads the image and produces a raw text transcription. This handles the hard part: decoding your handwriting.

2. **Correction** — a text LLM reviews the transcription and fixes words that don't exist in your configured languages, inferring the correct word from surrounding context. Proper nouns and words from secondary languages are left untouched.

You bring your own API key (BYOK) for whichever provider you choose. Penport never proxies your key or sends it anywhere other than the provider's own API.

---

## Supported LLM Providers

| Provider | Vision (Step 1) | Correction (Step 2) | Free tier |
|----------|:-:|:-:|:-:|
| Gemini | ✅ | ✅ | ✅ generous |
| OpenAI | ✅ | ✅ | ❌ |
| Anthropic | ✅ | ✅ | ❌ |
| Ollama (local) | ✅ | ✅ | ✅ fully free |

**Recommended starting point:** Gemini Flash via Google AI Studio. Free API key, no credit card, strong cursive handwriting recognition. For a personal journaling pipeline processing a few photos a day you will never approach the rate limits.

---

## Installation

> ⚠️ Penport is in early development. Installers are not yet available. See [Development](#development) to run from source.

Pre-built installers for Windows, macOS, and Linux will be available on the [Releases](../../releases) page once v1 is ready.

---

## Usage

### First run

On first launch, the Settings window opens automatically.

1. **Set your inbox folder** — the local folder Penport will watch for new images
2. **Set your output folder** — where transcribed text files will be saved
3. **Choose your LLM provider** and enter your API key
4. **Set your languages** — e.g. `Romanian` as primary, `Norwegian, English` as additional. This helps the correction step avoid fixing words that are correct but just happen to be from a different language.
5. Click **Save** — Penport starts watching immediately

### Day to day

1. Write in your journal as normal
2. Photograph the page with your phone
3. Drop the photo into your inbox folder (or let your cloud sync client do it automatically)
4. Penport picks it up within minutes and saves a clean text file to your output folder
5. A desktop notification confirms when it's done

### Tray icon

Penport lives in your system tray. Right-click for:

| Menu item | Action |
|-----------|--------|
| Sync Now | Manually scan the inbox folder right now |
| Open Last Output | Opens the most recently created text file |
| Settings | Open the settings window |
| View Log | Browse transcription history and status |
| Quit | Stop Penport |

**Icon states:**
- ⚫ Grey — idle, watching
- 🔄 Animated — processing an image
- 🔴 Red — an error occurred, click View Log for details

---

## Roadmap

### v1 — Local (current)
- [ ] System tray icon with context menu
- [ ] Local inbox folder watcher
- [ ] Two-step LLM pipeline (transcription + correction)
- [ ] Language-aware correction
- [ ] Local output folder (dated `.txt` files)
- [ ] SQLite job history
- [ ] Settings window
- [ ] PyInstaller bundle for Windows, macOS, Linux

### v2 — Direct cloud adapters
For users who want Penport to connect directly to cloud storage without a desktop sync client (useful for server deployments or minimal setups):
- [ ] Google Drive
- [ ] Dropbox
- [ ] OneDrive
- [ ] WebDAV (Nextcloud, Syncthing)
- [ ] Proton Drive *(pending API maturity)*

### v3 — Mobile
- [ ] Android app (Kotlin) — photograph directly in app, skip the folder entirely
- [ ] iOS app

---

## Development

### Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

```bash
git clone https://github.com/yourusername/penport.git
cd penport
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
python main.py
```

### Building an installer

```bash
pyinstaller build/penport.spec
```

The output will be in `dist/`.

---

## Privacy

Penport runs entirely on your machine. Your journal photos and transcribed text never leave your computer except for the API call to your chosen LLM provider (sent directly from your machine using your own API key). Penport has no telemetry, no analytics, and no external server.

If privacy is a hard requirement, use the **Ollama** provider to run a local vision model entirely offline. No data leaves your machine at all.

---

## Contributing

Contributions are welcome. Please open an issue before starting significant work so we can discuss approach.

Areas where help is most appreciated:
- Additional LLM provider implementations (`providers/`)
- Cloud adapter implementations for v2 (`adapters/`)
- Testing on different handwriting styles and languages
- macOS and Windows packaging and testing

---

## License

MIT
