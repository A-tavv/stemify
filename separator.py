"""
separator.py — Core stem separation engine using Meta's Demucs v4.

Supported models:
  htdemucs     → 4 stems: vocals, drums, bass, other
  htdemucs_ft  → same, fine-tuned (better quality, slower)
  htdemucs_6s  → 6 stems: vocals, drums, bass, piano, guitar, other (best for music)
"""

import os
import tempfile
import numpy as np
import librosa
import soundfile as sf


MODELS = {
    "htdemucs_6s  (best quality — 6 stems)": "htdemucs_6s",
    "htdemucs_ft  (fine-tuned — 4 stems)":   "htdemucs_ft",
    "htdemucs     (fast — 4 stems)":          "htdemucs",
}

# All possible stems per model
MODEL_STEMS = {
    "htdemucs_6s": ["vocals", "drums", "bass", "piano", "guitar", "other"],
    "htdemucs_ft": ["vocals", "drums", "bass", "other"],
    "htdemucs":    ["vocals", "drums", "bass", "other"],
}


def separate(
    input_path: str,
    remove: list,           # list of stem names to remove, e.g. ["vocals"]
    model_key: str = "htdemucs_6s",
    work_dir: str = None,
) -> tuple[str, dict]:
    """
    Run Demucs separation and return a mixed output of all kept stems.

    Returns:
      (output_wav_path, info_dict)
      info_dict = { "kept": [...], "removed": [...], "model": str }
    """
    import torch
    from demucs.pretrained import get_model
    from demucs.apply import apply_model

    if work_dir is None:
        work_dir = tempfile.mkdtemp(prefix="stemify_")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"🔧  Device: {device}")
    print(f"📦  Loading model: {model_key}...")
    separator = get_model(model_key)
    separator.to(device)
    separator.eval()

    # Load audio using librosa (avoids torchaudio/torchcodec issues on Windows)
    print(f"📂  Loading: {input_path}")
    audio_np, _ = librosa.load(input_path, sr=separator.samplerate, mono=False)
    if audio_np.ndim == 1:
        audio_np = np.stack([audio_np, audio_np])
    audio_np = audio_np[:2]  # enforce stereo

    wav = torch.tensor(audio_np, dtype=torch.float32).unsqueeze(0).to(device)

    print("🎵  Separating stems...")
    with torch.no_grad():
        sources = apply_model(separator, wav, device=device)[0]
    # sources: (num_stems, 2, samples)

    # Mix all kept stems
    mixed = None
    kept = []
    removed_actual = []

    for i, name in enumerate(separator.sources):
        if name in remove:
            removed_actual.append(name)
            print(f"  ⏭  removed : {name}")
            continue
        kept.append(name)
        print(f"  ✅  kept    : {name}")
        stem = sources[i].cpu().numpy().astype(np.float64)
        if mixed is None:
            mixed = stem
        else:
            min_len = min(mixed.shape[1], stem.shape[1])
            mixed = mixed[:, :min_len] + stem[:, :min_len].astype(np.float64)

    if mixed is None:
        raise ValueError("All stems were removed — nothing left to output.")

    # Normalize
    peak = np.max(np.abs(mixed))
    if peak > 0:
        mixed = mixed / peak * 0.92

    output_path = os.path.join(work_dir, "output.wav")
    sf.write(output_path, mixed.T, separator.samplerate, subtype="PCM_24")

    info = {
        "kept":    kept,
        "removed": removed_actual,
        "model":   model_key,
        "device":  device,
    }

    print(f"✅  Output saved → {output_path}")
    return output_path, info
