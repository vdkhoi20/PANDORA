import types
from pathlib import Path

import torch
from diffusers import DDIMScheduler, StableDiffusionXLPipeline
from torchvision.utils import save_image

from .attention import AttentionBase, PandoraSelfAttentionControlMask, register_attention_editor_diffusers
from .config import PandoraConfig
from .image_utils import extract_object_mask, normalized_image, open_rgb


class PandoraRemoval:
    """Unified PANDORA runner for SD1.5, SD2.1, and SDXL object removal."""

    BORDER_SIZE = {
        "Dataset_type1": 2,
        "Dataset_type2": 2,
        "Dataset_type3": 17,
    }

    def __init__(self, config: PandoraConfig):
        self.config = config
        self.diffuser_utils = self._load_diffuser_utils(config.version)
        self.model = self._load_model()

    def _load_diffuser_utils(self, version: str):
        if version == "sd15":
            from .backends.sd15 import diffuser_utils

            return diffuser_utils
        if version == "sd21":
            from .backends.sd21 import diffuser_utils

            return diffuser_utils
        if version == "sdxl":
            from .backends.sdxl import diffuser_utils

            return diffuser_utils
        raise ValueError(f"Unsupported PANDORA version: {version}")

    def _torch_dtype(self):
        if self.config.dtype == "float16":
            return torch.float16
        if self.config.dtype == "bfloat16":
            return torch.bfloat16
        return torch.float32

    def _common_model_kwargs(self):
        return {
            "cache_dir": self.config.cache_dir,
            "local_files_only": self.config.local_files_only,
            "safety_checker": None,
            "requires_safety_checker": False,
        }

    def _load_model(self):
        model_path = self.config.resolved_model_path
        device = self.config.resolved_device
        common_kwargs = self._common_model_kwargs()

        if self.config.version == "sd15":
            scheduler = DDIMScheduler(
                beta_start=0.00085,
                beta_end=0.012,
                beta_schedule="scaled_linear",
                clip_sample=False,
                set_alpha_to_one=False,
            )
            model = self.diffuser_utils.OIICtrlPipeline.from_pretrained(
                model_path,
                scheduler=scheduler,
                **common_kwargs,
            )
            model.text_encoder.to(device)
            return model.to(device)

        if self.config.version == "sd21":
            scheduler = DDIMScheduler(
                beta_start=0.00085,
                beta_end=0.012,
                beta_schedule="scaled_linear",
                clip_sample=False,
                set_alpha_to_one=False,
                prediction_type="v_prediction",
                steps_offset=1,
            )
            model = self.diffuser_utils.OIICtrlPipeline.from_pretrained(
                model_path,
                scheduler=scheduler,
                torch_dtype=self._torch_dtype(),
                **common_kwargs,
            )
            return model.to(device)

        sdxl_kwargs = {
            "torch_dtype": self._torch_dtype(),
            "use_safetensors": True,
            **common_kwargs,
        }
        if self.config.dtype == "float16":
            sdxl_kwargs["variant"] = "fp16"
        model = StableDiffusionXLPipeline.from_pretrained(model_path, **sdxl_kwargs).to(device)
        model.scheduler = DDIMScheduler.from_config(model.scheduler.config)
        model.invert = types.MethodType(self.diffuser_utils.invert, model)
        model.custom_call = types.MethodType(self.diffuser_utils.custom_call, model)
        return model

    def _invert(self, image_path: str | Path):
        register_attention_editor_diffusers(self.model, AttentionBase(self.config.steps))

        if self.config.version == "sd15":
            source = normalized_image(image_path, self.config.resolved_device, self.config.image_size)
            start_code, intermediates = self.model.invert(
                source,
                prompt="",
                guidance_scale=0,
                num_inference_steps=self.config.steps,
                return_intermediates=True,
                DEVICE=self.config.resolved_device,
            )
            return torch.cat([start_code.clone(), start_code.clone()]), intermediates

        image = open_rgb(image_path, self.config.image_size)
        if self.config.version == "sd21":
            intermediates, start_code = self.model.invert(
                prompt="",
                image=image,
                guidance_scale=0.0,
                num_inference_steps=self.config.steps,
            )
            return torch.cat([start_code.clone(), start_code.clone()]), intermediates

        start_code, intermediates = self.model.invert(
            image,
            prompt="",
            guidance_scale=1.0,
            num_inference_steps=self.config.steps,
        )
        return start_code, intermediates

    def remove_image(
        self,
        image_path: str | Path,
        mask_path: str | Path,
        output_path: str | Path,
        *,
        border_size: int = 17,
    ) -> None:
        object_mask = extract_object_mask(
            mask_path,
            self.config.resolved_device,
            self.config.image_size,
            border_size,
        )
        background_mask = 1.0 - object_mask
        start_code, intermediates = self._invert(image_path)

        editor = PandoraSelfAttentionControlMask(
            start_step=self.config.step_query_value,
            start_layer=self.config.layer_query_value,
            mask=object_mask,
            dilated_mask=background_mask,
            total_steps=self.config.steps,
            percentile=self.config.percentile,
            version=self.config.version,
        )
        register_attention_editor_diffusers(self.model, editor)

        if self.config.version == "sd15":
            images = self.model(
                ["", ""],
                latents=start_code,
                ref_intermediates=intermediates,
                num_inference_steps=self.config.steps,
                guidance_scale_LADG=self.config.guidance_scale_ladg,
                local_mask=object_mask,
                DEVICE=self.config.resolved_device,
            )
            result = images[1]
        elif self.config.version == "sd21":
            images = self.model(
                prompt=["", ""],
                latents=start_code,
                latents_intermediate=intermediates,
                num_inference_steps=self.config.steps,
                guidance_scale_LADG=self.config.guidance_scale_ladg,
                local_mask=object_mask,
            )
            result = images[1]
        else:
            images = self.model.custom_call(
                prompt="",
                latents=start_code,
                ref_intermediates=intermediates,
                num_inference_steps=self.config.steps,
                guidance_scale=self.config.guidance_scale,
                guidance_scale_LADG=self.config.guidance_scale_ladg,
                local_mask=object_mask,
            ).images
            result = images[0]

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(result, torch.Tensor):
            save_image(result, str(output_path))
        else:
            result.save(output_path)

    def run_dataset(
        self,
        dataset_root: str | Path,
        output_dir: str | Path,
        *,
        dataset_types: list[str] | None = None,
        limit: int | None = None,
    ) -> None:
        dataset_root = Path(dataset_root)
        output_dir = Path(output_dir)
        dataset_types = dataset_types or ["Dataset_type1", "Dataset_type2", "Dataset_type3"]

        jobs = []
        for dataset_name in dataset_types:
            images_dir = dataset_root / dataset_name / "Images"
            masks_dir = dataset_root / dataset_name / "Masks"
            if not images_dir.exists():
                print(f"[WARN] Missing images folder: {images_dir}")
                continue
            files = sorted(
                [p for p in images_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}],
                key=lambda p: int(p.stem),
            )
            for image_path in files:
                mask_path = masks_dir / f"{image_path.stem}.png"
                if mask_path.exists():
                    jobs.append((dataset_name, image_path, mask_path))

        if limit is not None:
            jobs = jobs[:limit]

        for index, (dataset_name, image_path, mask_path) in enumerate(jobs, start=1):
            border_size = self.BORDER_SIZE.get(dataset_name, 17)
            out_path = output_dir / dataset_name / f"{image_path.stem}.png"
            print(f"[{index}/{len(jobs)}] {self.config.version} {dataset_name}/{image_path.name}")
            self.remove_image(image_path, mask_path, out_path, border_size=border_size)
