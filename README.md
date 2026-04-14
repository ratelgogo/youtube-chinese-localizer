# youtube-chinese-localizer

Codex skill and standalone scripts for turning YouTube or local foreign-language videos into:

- Simplified Chinese subtitles
- Mandarin dubbing
- final MP4 exports with burned-in subtitles

The current pipeline uses:

- `yt-dlp` for YouTube download
- `faster-whisper` for local ASR
- Volcengine `TranslateText` for subtitle translation
- Volc TTS `openspeech.bytedance.com/api/v3/tts/unidirectional` for Mandarin dubbing
- `ffmpeg` for audio mixing and final export

## Repository Layout

- `SKILL.md`: Codex skill entry
- `scripts/localize_video.py`: end-to-end pipeline
- `scripts/run_localize_video.sh`: launcher that prefers `.venv` and falls back to `python3`
- `references/runtime-requirements.md`: setup notes and troubleshooting
- `agents/openai.yaml`: skill metadata

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew install ffmpeg yt-dlp
```

Set credentials:

**New console (single API key for both MT and TTS):**
```bash
export VOLCENGINE_API_KEY="your-api-key"
```

**Old console (separate credentials):**
- For Translation: `VOLCENGINE_MT_APP_ID` + `VOLCENGINE_MT_ACCESS_KEY`
- For TTS: `VOLCENGINE_TTS_APP_ID` + `VOLCENGINE_TTS_ACCESS_KEY`
- Optional: `VOLCENGINE_MT_RESOURCE_ID` (default: volc.speech.mt)
- Optional: `VOLCENGINE_TTS_RESOURCE_ID` (default: seed-tts-2.0)

Example (old console):
```bash
export VOLCENGINE_MT_APP_ID="your-mt-app-id"
export VOLCENGINE_MT_ACCESS_KEY="your-mt-access-key"
export VOLCENGINE_TTS_APP_ID="your-tts-app-id"
export VOLCENGINE_TTS_ACCESS_KEY="your-tts-access-key"
```

Run with a YouTube URL:

```bash
scripts/run_localize_video.sh \
  --input "https://www.youtube.com/watch?v=..." \
  --workdir ./runs/demo
```

If YouTube blocks anonymous download, reuse browser cookies:

```bash
scripts/run_localize_video.sh \
  --input "https://www.youtube.com/watch?v=..." \
  --workdir ./runs/demo \
  --cookies-from-browser edge
```

Run with a local file:

```bash
scripts/run_localize_video.sh \
  --input /path/to/video.mp4 \
  --workdir ./runs/local-video \
  --voice zh_male_beijingxiaoye_emo_v2_mars_bigtts
```

## Command Line Arguments

### Required Arguments
- `--input`: YouTube URL or local video path
- `--workdir`: Directory for intermediate and final files

### Optional Arguments
- `--transcript-json`: Existing transcript JSON with segments (skip transcription)
- `--cookies-from-browser`: Pass browser cookies to yt-dlp (e.g., edge, chrome)
- `--skip-transcription`: Require --transcript-json instead of transcribing
- `--skip-tts`: Stop after subtitles and do not synthesize dubbing
- `--source-language`: Hint language code for ASR
- `--whisper-model`: faster-whisper model name (default: small)
- `--whisper-device`: faster-whisper device (default: auto)
- `--whisper-compute-type`: faster-whisper compute type (default: default)
- `--translation-target-language`: Volcengine translation target language code (default: zh)
- `--translation-batch-size`: Volcengine TranslateText batch size, max 16 (default: 16)
- `--voice`: Volc TTS speaker name (default: zh_male_m191_uranus_bigtts)
- `--tts-format`: Volc TTS output format: mp3, wav, aac (default: wav)
- `--tts-sample-rate`: Volc TTS sample rate: 8000, 16000, 22050, 24000, 32000, 44100, 48000 (default: 24000)
- `--background-volume`: Original audio volume in final mix, 0 to mute completely (default: 0)
- `--max-tts-speedup`: Maximum speedup factor for TTS segments (default: 1.35)
- `--sidecar-subtitles`: Embed subtitles as a soft track instead of burning them in

## Outputs

The pipeline writes these files into the selected work directory:

- `source.*`
- `audio.wav`
- `transcript.json`
- `translated_segments.json`
- `subtitles.zh.srt`
- `dub_track.wav`
- `final_audio.wav`
- `final.mp4`
