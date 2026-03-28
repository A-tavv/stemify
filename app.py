"""
app.py — Stemify: Audio Stem Remover
Step 1: Vocal removal (clean, production-ready)
Step 2: Drum removal (hi-hat, kick, snare) — coming soon
Step 3: Genre conversion (hip hop / rap → LoFi / Jazz) — coming soon

Run:
  python app.py
  → open http://localhost:7860
"""

import os
import shutil
import tempfile
import gradio as gr

from separator import separate, MODELS, MODEL_STEMS


# ─────────────────────────────────────────────
#  CONVERSION FUNCTION
# ─────────────────────────────────────────────

def run(audio_file, model_label, remove_vocals, remove_drums,
        progress=gr.Progress(track_tqdm=True)):

    if audio_file is None:
        return None, "❌  Please upload an audio file."

    # Build remove list from checkboxes
    remove = []
    if remove_vocals:
        remove.append("vocals")
    if remove_drums:
        remove.append("drums")

    if not remove:
        return None, "⚠️  Select at least one stem to remove."

    # Resolve model key from label
    model_key = MODELS.get(model_label, "htdemucs_6s")

    work_dir = tempfile.mkdtemp(prefix="stemify_")
    log = []

    try:
        log.append(f"📦  Model   : {model_key}")
        log.append(f"🗑️   Removing: {', '.join(remove)}")
        log.append("─" * 40)

        progress(0.1, desc="Loading model...")
        output_path, info = separate(
            input_path = audio_file,
            remove     = remove,
            model_key  = model_key,
            work_dir   = work_dir,
        )
        progress(0.9, desc="Finalizing...")

        log.append(f"✅  Kept    : {', '.join(info['kept'])}")
        log.append(f"⏭️   Removed : {', '.join(info['removed'])}")
        log.append(f"💻  Device  : {info['device']}")
        log.append("─" * 40)
        log.append("✅  Done!")

        final = os.path.join(tempfile.gettempdir(), "stemify_output.wav")
        shutil.copy(output_path, final)
        progress(1.0, desc="Done!")
        return final, "\n".join(log)

    except Exception as e:
        log.append(f"❌  Error: {e}")
        return None, "\n".join(log)


# ─────────────────────────────────────────────
#  UI
# ─────────────────────────────────────────────

css = """
.gr-button-primary { font-size: 1.1em !important; }
footer { display: none !important; }
"""

with gr.Blocks(css=css, title="Stemify — Audio Stem Remover") as demo:

    gr.Markdown("""
    # 🎵 Stemify — Audio Stem Remover
    Powered by **Meta Demucs v4**. Remove vocals and/or drums from any track.
    Upload → Select what to remove → Download clean instrumental.
    """)

    with gr.Row():

        # ── Left: upload + controls ───────────────────────────────────
        with gr.Column(scale=1):

            audio_in = gr.Audio(
                label="🎵 Upload Track (MP3, WAV, FLAC)",
                type="filepath",
                sources=["upload"],
            )

            model_label = gr.Radio(
                choices=list(MODELS.keys()),
                value=list(MODELS.keys())[0],
                label="🤖 Demucs Model",
            )

            gr.Markdown("### 🗑️ What to Remove")

            remove_vocals = gr.Checkbox(
                label="🎤 Remove Vocals",
                value=True,
            )
            remove_drums = gr.Checkbox(
                label="🥁 Remove Drums  (kick, snare, hi-hat, cymbals)",
                value=False,
            )

            btn = gr.Button("🚀 Process", variant="primary", size="lg")

        # ── Right: output + log ───────────────────────────────────────
        with gr.Column(scale=1):

            audio_out = gr.Audio(
                label="🎧 Output (instrumental)",
                type="filepath",
            )

            log_out = gr.Textbox(
                label="📋 Processing Log",
                lines=12,
                interactive=False,
            )

    btn.click(
        fn=run,
        inputs=[audio_in, model_label, remove_vocals, remove_drums],
        outputs=[audio_out, log_out],
    )

    gr.Markdown("""
    ---
    ### 📍 Roadmap
    | Step | Feature | Status |
    |------|---------|--------|
    | ✅ 1 | Vocal removal | **Done** |
    | 🔜 2 | Individual drum stem removal (kick / snare / hi-hat separately) | Coming |
    | 🔜 3 | Genre conversion: Hip-Hop / Rap → LoFi / Jazz | Coming |

    ### 🤖 Model Guide
    | Model | Stems | Speed | Best for |
    |-------|-------|-------|---------|
    | `htdemucs_6s` | 6 (vocals, drums, bass, piano, guitar, other) | Medium | Music with piano/guitar |
    | `htdemucs_ft` | 4 (vocals, drums, bass, other) | Slow | Best overall quality |
    | `htdemucs` | 4 (vocals, drums, bass, other) | Fast | Quick results |
    """)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
