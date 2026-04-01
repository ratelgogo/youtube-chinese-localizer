# video-Zebra-china

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

```bash
export VOLCENGINE_ACCESS_KEY="AK..."
export VOLCENGINE_SECRET_KEY="SK..."
export VOLCENGINE_REGION="cn-north-1"
export VOLCENGINE_TTS_API_KEY="your-tts-api-key"
export VOLCENGINE_TTS_RESOURCE_ID="volc.service_type.10029"
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
