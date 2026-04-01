# Runtime Requirements

## Required Tools

- `ffmpeg`
- `ffprobe`

## Optional but Recommended Tools

- `yt-dlp`: download YouTube inputs
- `faster-whisper`: local speech-to-text with timestamps
- `volcengine-python-sdk`: already installed in this skill's `.venv` for Volcengine text translation

## Installed Layout On This Machine

This skill has a dedicated virtual environment at:

`/Users/bytedance/.codex/skills/youtube-chinese-localizer/.venv`

Prefer running:

```bash
/Users/bytedance/.codex/skills/youtube-chinese-localizer/scripts/run_localize_video.sh ...
```

instead of calling the system `python3` directly.

## Typical Setup

```bash
brew install ffmpeg yt-dlp
export VOLCENGINE_ACCESS_KEY="AK..."
export VOLCENGINE_SECRET_KEY="SK..."
export VOLCENGINE_REGION="cn-north-1"
export VOLCENGINE_TTS_API_KEY="your-tts-api-key"
export VOLCENGINE_TTS_RESOURCE_ID="volc.service_type.10029"
```

If a YouTube download fails with a bot check, rerun with:

```bash
scripts/run_localize_video.sh \
  --input "https://www.youtube.com/watch?v=..." \
  --workdir ./runs/demo \
  --cookies-from-browser edge
```

`faster-whisper` may require extra runtime libraries depending on the platform. If installation fails, fall back to providing `--transcript-json` instead of doing ASR inside the skill.

## Transcript JSON Shape

The bundled script accepts either:

1. A raw array of segment objects
2. An object with a top-level `segments` array

Each segment should look like:

```json
{
  "start": 0.0,
  "end": 2.4,
  "text": "Original speech",
  "translated_text": "中文字幕，可选"
}
```

If `translated_text` is present for every segment, the script skips Volcengine text translation and goes straight to subtitle rendering and TTS.

## Environment Variables

- `VOLCENGINE_ACCESS_KEY`: required for Volcengine `TranslateText`
- `VOLCENGINE_SECRET_KEY`: required for Volcengine `TranslateText`
- `VOLCENGINE_REGION`: translation region, defaults to `cn-north-1`
- `VOLCENGINE_TTS_API_KEY`: required for `openspeech.bytedance.com/api/v3/tts/unidirectional`
- `VOLCENGINE_TTS_RESOURCE_ID`: defaults to `volc.service_type.10029`

## Interface Choices In This Skill

- Subtitle translation:
  - interface: Volcengine `TranslateText`
  - target language default: `zh`
  - batch limit: 16 texts per request
- Chinese dubbing:
  - interface: Volc TTS `POST https://openspeech.bytedance.com/api/v3/tts/unidirectional`
  - headers: `x-api-key` and `X-Api-Resource-Id`
  - default speaker: `zh_female_qingxin`
  - default format: `wav`

This skill intentionally keeps ASR local with `faster-whisper`, because that avoids first uploading user video or audio into another cloud workflow just to obtain timestamps.

## Quality Tuning

- Use `--background-volume 0.08` to keep the original soundtrack very quiet.
- Use `--background-volume 0.18` to preserve more ambience under the Chinese dub.
- Use `--voice` to switch Volc TTS speakers.
- Use a better `faster-whisper` model such as `medium` or `large-v3` when subtitle timing matters more than speed.
- Keep `--translation-batch-size` at or below `16`.
## Common Failure Modes

### Missing `yt-dlp`

Pass a local file to `--input` instead of a URL, or install `yt-dlp`.

### YouTube Bot Check

Pass `--cookies-from-browser edge` or another installed browser name so `yt-dlp` can reuse your logged-in cookies.

### Missing `faster-whisper`

Install it, or pass `--transcript-json` with timestamped segments.

### Missing `VOLCENGINE_ACCESS_KEY` or `VOLCENGINE_SECRET_KEY`

Provide pre-translated `translated_text` in the transcript JSON, or stop after ASR and translate elsewhere before rerunning.

### Missing `VOLCENGINE_TTS_API_KEY`

Run with `--skip-tts` to produce subtitles only, or configure the speech application credentials in the Volcengine console.

### Invalid Speaker

If the API returns `TTSInvalidSpeaker`, switch `--voice` to a valid speaker from your enabled Volc TTS account.

### Burned Subtitles Fail

The script writes `subtitles.zh.srt` before muxing. Keep that file even if ffmpeg subtitle rendering fails and rerun without burn-in if needed.
