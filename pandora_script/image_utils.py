from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision.io import read_image


def open_rgb(path: str | Path, size: int) -> Image.Image:
    return Image.open(path).convert("RGB").resize((size, size), resample=Image.BICUBIC)


def normalized_image(path: str | Path, device: str, size: int) -> torch.Tensor:
    image = read_image(str(path))[:3].unsqueeze(0).float() / 127.5 - 1.0
    image = F.interpolate(image, (size, size), mode="bilinear", align_corners=False)
    return image.to(device)


def extract_object_mask(mask_path: str | Path, device: str, size: int, border_size: int) -> torch.Tensor:
    mask = read_image(str(mask_path)).to(device)
    if mask.shape[0] == 4:
        mask = mask[1:]
    mask = mask.float().mean(dim=0)
    object_mask = 1.0 - (mask < 255.0).float()
    object_mask = F.interpolate(
        object_mask.unsqueeze(0).unsqueeze(0),
        (size, size),
        mode="nearest",
    ).squeeze()
    return get_border_from_mask(object_mask, border_size)


def get_border_from_mask(mask_tensor: torch.Tensor, border_size: int) -> torch.Tensor:
    mask_np = mask_tensor.detach().cpu().numpy().astype(np.uint8)
    kernel = np.ones((border_size, border_size), np.uint8)
    dilated = cv2.dilate(mask_np, kernel, iterations=1)
    return torch.from_numpy(dilated).float().to(mask_tensor.device)
