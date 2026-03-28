# 🎵 Stemify — Audio Stem Remover

Remove vocals and drums from any song using **Meta's Demucs v4**.
Clean, simple, local — no cloud, no API key needed.

## Roadmap

| Step | Feature | Status |
|------|---------|--------|
| ✅ 1 | Vocal removal | **Done** |
| 🔜 2 | Individual drum stem removal (kick / snare / hi-hat) | Coming |
| 🔜 3 | Genre conversion: Hip-Hop / Rap → LoFi / Jazz | Coming |

---

## Quickstart

```bash
pip install -r requirements.txt
python app.py
# → open http://localhost:7860
```

---

## Models

| Model | Stems | Best for |
|-------|-------|---------|
| `htdemucs_6s` | 6 (vocals, drums, bass, piano, guitar, other) | Music with piano/guitar |
| `htdemucs_ft` | 4 (vocals, drums, bass, other) | Best overall quality |
| `htdemucs`    | 4 (vocals, drums, bass, other) | Fast results |

First run downloads the model (~300MB) once, then it's cached locally.

---

## File Structure

```
stemify/
├── app.py          ← Gradio web UI
├── separator.py    ← Demucs separation engine
├── requirements.txt
└── README.md
```

---

## Hardware

| Setup | Speed (3-min track) |
|-------|-------------------|
| CPU only | ~5–10 min |
| NVIDIA GPU (4GB+ VRAM) | ~20–30 sec |
