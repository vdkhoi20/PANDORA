# PANDORA

Official implementation for **PANDORA: Pixel-wise Attention Dissolution and Latent Guidance for Zero-Shot Object Removal**.

[![Project Page](https://img.shields.io/badge/Project-Page-blue)](https://vdkhoi20.github.io/PANDORA/)
[![arXiv](https://img.shields.io/badge/arXiv-2603.27555-b31b1b)](https://arxiv.org/abs/2603.27555)
[![Code](https://img.shields.io/badge/GitHub-Code-black)](https://github.com/vdkhoi20/PANDORA)
[![ICME 2026](https://img.shields.io/badge/Accepted-ICME%202026-emerald)](https://vdkhoi20.github.io/PANDORA/)

> **Accepted to IEEE International Conference on Multimedia and Expo (ICME) 2026.**

PANDORA removes objects directly on pretrained diffusion models without fine-tuning, text prompts, or per-image optimization. This repository provides a cleaned runner for Stable Diffusion v1.5, Stable Diffusion 2.1, and Stable Diffusion XL.

## Highlights

- **Prompt-free object removal** with only an input image and binary mask.
- **Pixel-wise Attention Dissolution (PAD)** for suppressing object evidence in self-attention.
- **Localized Attentional Disentanglement Guidance (LADG)** for masked latent guidance.
- Unified code path for **SD1.5**, **SD2.1**, and **SDXL**.
- Included object-removal benchmark under `datasets/object_removal`.
- Project page includes paper figures for the main pipeline, qualitative comparison, benchmark cases, and the Clutter Erase demo system.

## Installation

```bash
git clone https://github.com/vdkhoi20/PANDORA.git
cd PANDORA

conda create -n pandora python=3.10 -y
conda activate pandora
pip install torch torchvision diffusers transformers accelerate safetensors einops pillow numpy tqdm
```

The SDXL version is memory intensive. A GPU with at least 24 GB VRAM is recommended for 1024 x 1024 inference.

## Usage

Run one image:

```bash
python run_pandora.py \
  --version sd21 \
  --image path/to/image.jpg \
  --mask path/to/mask.png \
  --output results/example.png
```

Run the benchmark:

```bash
python run_pandora.py \
  --version sd15 \
  --dataset datasets/object_removal \
  --output results/pandora_sd15

python run_pandora.py \
  --version sd21 \
  --dataset datasets/object_removal \
  --output results/pandora_sd21

python run_pandora.py \
  --version sdxl \
  --dataset datasets/object_removal \
  --output results/pandora_sdxl
```

Useful options:

```bash
--steps 50
--guidance-scale-ladg 1.6
--percentile 95
--cache-dir /path/to/huggingface_cache
--local-files-only
--limit 5
```

## Supported Backbones

| Version | Default model | Resolution | Notes |
| --- | --- | ---: | --- |
| `sd15` | `botp/stable-diffusion-v1-5` | 512 | Original PANDORA backbone |
| `sd21` | `sd2-community/stable-diffusion-2-1` | 768 | Uses `v_prediction` scheduler |
| `sdxl` | `stabilityai/stable-diffusion-xl-base-1.0` | 1024 | Newly added SDXL backend |

## Dataset Layout

The included benchmark follows this structure:

```text
datasets/object_removal/
  Dataset_type1/
    Images/
    Masks/
  Dataset_type2/
    Images/
    Masks/
  Dataset_type3/
    Images/
    Masks/
```

Masks should be binary PNG files with the same stem as the corresponding image.

The benchmark covers **75 single-object**, **17 multi-object**, and **94 mass-similar object** samples, with manually or automatically prepared masks.

## Demo System

The accompanying **Clutter Erase** demo is powered by PANDORA and supports:

- Manual mask drawing.
- Prompt-based object selection.
- Click-based segmentation.
- Similar-object search for mass-similar removal.

These interactions are designed for prompt-free, fine-tuning-free object removal in a single forward pass.

## Method Overview

PANDORA first inverts the input image into the diffusion noise space and stores intermediate latents. During denoising, it uses **Background Preservation Attention (BPA)** to protect unmasked regions, **Pixel-wise Attention Dissolution (PAD)** to suppress object information in self-attention, and **Localized Attentional Disentanglement Guidance (LADG)** to steer the masked latent trajectory toward clean object removal.

## Limitations

PANDORA can be sensitive to the PAD percentile threshold and the quality of the binary mask. Undersized masks may leave residual artifacts, while moderately oversized masks are usually more forgiving. Future work includes adaptive thresholding and automatic mask selection.

## Verification

The refactored runner was checked with:

```bash
python -m compileall -q pandora_script run_pandora.py
python run_pandora.py --help
```

GPU smoke benchmarks were also completed for 5 samples with 50 DDIM steps on SD1.5, SD2.1, and SDXL.

## Related Projects

- [PANDORA Project Page](https://vdkhoi20.github.io/PANDORA/)
- [Paper on arXiv](https://arxiv.org/abs/2603.27555)
- [Public Code](https://github.com/vdkhoi20/PANDORA)
- [CPAM](https://vdkhoi20.github.io/CPAM/)
- [FocusDiff](https://vdkhoi20.github.io/FocusDiff/)

## Citation

```bibtex
@inproceedings{Vo2026ICME,
  title = {PANDORA: Pixel-wise Attention Dissolution and Latent Guidance for Zero-Shot Object Removal},
  author = {Vo, Dinh-Khoi and Nguyen, Van-Loc and Nguyen, Tam V. and Tran, Minh-Triet and Le, Trung-Nghia},
  booktitle = {IEEE International Conference on Multimedia and Expo (ICME)},
  year = {2026},
  url = {https://arxiv.org/abs/2603.27555},
  code = {https://github.com/vdkhoi20/PANDORA},
}

@inproceedings{Vo2026DemoICME,
  title={Zero-Shot Mass-Similar and Multi-Object Removal in Single Pass},
  author={Dinh-Khoi Vo and Van-Loc Nguyen and Tam V. Nguyen and Minh-Triet Tran and Trung-Nghia Le},
  booktitle={IEEE International Conference on Multimedia and Expo (ICME)},
  year={2026},
  url = {https://vdkhoi20.github.io/PANDORA/},
  code = {https://github.com/vdkhoi20/PANDORA},
}
```
