from dataclasses import dataclass
from typing import Optional

import torch


@dataclass
class PandoraConfig:
    version: str = "sd15"
    model_path: Optional[str] = None
    device: Optional[str] = None
    dtype: str = "float32"
    cache_dir: Optional[str] = None
    local_files_only: bool = False
    steps: int = 50
    guidance_scale: float = 1.0
    guidance_scale_ladg: float = 1.6
    percentile: float = 95.0
    step_query: Optional[int] = None
    layer_query: Optional[int] = None

    @property
    def resolved_device(self) -> str:
        return self.device or ("cuda" if torch.cuda.is_available() else "cpu")

    @property
    def image_size(self) -> int:
        if self.version == "sd15":
            return 512
        if self.version == "sd21":
            return 768
        if self.version == "sdxl":
            return 1024
        raise ValueError(f"Unsupported PANDORA version: {self.version}")

    @property
    def default_model_path(self) -> str:
        if self.version == "sd15":
            return "botp/stable-diffusion-v1-5"
        if self.version == "sd21":
            return "sd2-community/stable-diffusion-2-1"
        if self.version == "sdxl":
            return "stabilityai/stable-diffusion-xl-base-1.0"
        raise ValueError(f"Unsupported PANDORA version: {self.version}")

    @property
    def resolved_model_path(self) -> str:
        return self.model_path or self.default_model_path

    @property
    def step_query_value(self) -> int:
        return 45 if self.step_query is None else self.step_query

    @property
    def layer_query_value(self) -> int:
        return 17 if self.layer_query is None else self.layer_query
