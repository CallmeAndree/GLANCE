# Task 1 - GNN-LLM fusion gap

## Environment

Use the repository conda environment:

```powershell
conda activate graphdm
pip install -r sections/s1_trucmai/requirements.txt
```

Copy `.env.example` values into environment variables. Do not commit credentials.

PowerShell:

```powershell
$env:AZURE_SUBSCRIPTION_KEY="..."
$env:AZURE_SERVICE_REGION="eastasia"
```

The source reads credentials from the process environment. It does not contain an API key.

## Preview without network voiceover

This mode uses fallback durations for all 44 narration blocks and still writes an SRT file.

```powershell
$env:S1_USE_VOICEOVER="0"
manim -pql sections/s1_trucmai/s1_rebuilt_expanded_style.py S1CoreProblemExpanded --disable_caching
```

## Preview with gTTS

```powershell
$env:S1_USE_VOICEOVER="1"
$env:S1_USE_AZURE="0"
manim -pql sections/s1_trucmai/s1_rebuilt_expanded_style.py S1CoreProblemExpanded --disable_caching
```

## Preview with Azure Speech

```powershell
$env:S1_USE_VOICEOVER="1"
$env:S1_USE_AZURE="1"
manim -pql sections/s1_trucmai/s1_rebuilt_expanded_style.py S1CoreProblemExpanded --disable_caching
```

Default Azure voice: `vi-VN-HoaiMyNeural`, rate `-8%`.

## Final render

```powershell
manim -pqh sections/s1_trucmai/s1_rebuilt_expanded_style.py S1CoreProblemExpanded --disable_caching
```

Outputs are written under:

```text
media/videos/s1_rebuilt_expanded_style/480p15/
media/videos/s1_rebuilt_expanded_style/1080p60/
```

## Content map

See `STORYBOARD.md` for the 19-scene source map, all 44 narration beats, visual actions, transitions and estimated timing.
