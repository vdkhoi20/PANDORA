import torch
from diffusers import DDIMInverseScheduler
from diffusers.image_processor import PipelineImageInput

@torch.no_grad()
def invert(
    self,
    image: PipelineImageInput,
    prompt: str = "",
    prompt_2: str = None,
    num_inference_steps: int = 50,
    guidance_scale: float = 1.0,  # Nên giữ 1.0 để kết quả tái tạo chính xác nhất
    generator: torch.Generator = None,
):
    # 1. Khởi tạo DDIM Inverse Scheduler
    inverse_scheduler = DDIMInverseScheduler.from_config(self.scheduler.config)
    inverse_scheduler.set_timesteps(num_inference_steps, device=self.device)
    timesteps = inverse_scheduler.timesteps

    # 2. Xử lý ảnh đầu vào và Fix lỗi NaN
    image = self.image_processor.preprocess(image)
    
    # Lưu lại dtype cũ, sau đó ép VAE và ảnh sang float32 để tránh tràn số
    vae_dtype = self.vae.dtype
    self.vae.to(dtype=torch.float32)
    image = image.to(device=self.device, dtype=torch.float32)

    # Encode ảnh thành latents
    latents = self.vae.encode(image).latent_dist.sample(generator)
    latents = latents * self.vae.config.scaling_factor
    batch_size = latents.shape[0]

    # Đưa VAE và latents trở về định dạng của UNet (thường là float16)
    self.vae.to(dtype=vae_dtype)
    latents = latents.to(dtype=self.unet.dtype)

    # In ra kiểm tra xem còn bị NaN không
    if torch.isnan(latents).any():
        print("Cảnh báo: Vẫn xuất hiện NaN trong latents!")

    # 3. Mã hóa Text Prompt (Chuẩn SDXL)
    do_classifier_free_guidance = guidance_scale > 1.0

    (
        prompt_embeds,
        negative_prompt_embeds,
        pooled_prompt_embeds,
        negative_pooled_prompt_embeds,
    ) = self.encode_prompt(
        prompt=prompt,
        prompt_2=prompt_2,
        device=self.device,
        num_images_per_prompt=1,
        do_classifier_free_guidance=do_classifier_free_guidance,
    )

    # 4. Chuẩn bị tham số thời gian và text nhúng (time_ids, add_text_embeds)
    height = int(latents.shape[2] * self.vae_scale_factor)
    width = int(latents.shape[3] * self.vae_scale_factor)
    original_size = (height, width)
    target_size = (height, width)
    crops_coords_top_left = (0, 0)

    text_encoder_projection_dim = (
        self.text_encoder_2.config.projection_dim 
        if self.text_encoder_2 is not None 
        else int(pooled_prompt_embeds.shape[-1])
    )

    add_time_ids = self._get_add_time_ids(
        original_size,
        crops_coords_top_left,
        target_size,
        dtype=prompt_embeds.dtype,
        text_encoder_projection_dim=text_encoder_projection_dim,
    )

    add_text_embeds = pooled_prompt_embeds

    if do_classifier_free_guidance:
        prompt_embeds = torch.cat([negative_prompt_embeds, prompt_embeds], dim=0)
        add_text_embeds = torch.cat([negative_pooled_prompt_embeds, add_text_embeds], dim=0)
        add_time_ids = torch.cat([add_time_ids, add_time_ids], dim=0)

    prompt_embeds = prompt_embeds.to(self.device)
    add_text_embeds = add_text_embeds.to(self.device)
    add_time_ids = add_time_ids.to(self.device).repeat(batch_size, 1)
    latentss=[]
    # 5. Vòng lặp Denoising Đảo Ngược
    with self.progress_bar(total=num_inference_steps) as progress_bar:
        for i, t in enumerate(timesteps):
            latent_model_input = torch.cat([latents] * 2) if do_classifier_free_guidance else latents
            latent_model_input = inverse_scheduler.scale_model_input(latent_model_input, t)

            added_cond_kwargs = {"text_embeds": add_text_embeds, "time_ids": add_time_ids}
            noise_pred = self.unet(
                latent_model_input,
                t,
                encoder_hidden_states=prompt_embeds,
                added_cond_kwargs=added_cond_kwargs,
                return_dict=False,
            )[0]

            if do_classifier_free_guidance:
                noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
                noise_pred = noise_pred_uncond + guidance_scale * (noise_pred_text - noise_pred_uncond)

            latents = inverse_scheduler.step(noise_pred, t, latents, return_dict=False)[0]
            progress_bar.update()
            latentss.append(latents)

    return latents,latentss





import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from diffusers.pipelines.stable_diffusion_xl.pipeline_output import StableDiffusionXLPipelineOutput
from diffusers.callbacks import MultiPipelineCallbacks, PipelineCallback
from diffusers.utils import deprecate
from diffusers.pipelines.stable_diffusion.pipeline_stable_diffusion import rescale_noise_cfg, retrieve_timesteps

@torch.no_grad()
def custom_call(
    self,
    prompt: Union[str, List[str]] = None,
    prompt_2: Optional[Union[str, List[str]]] = None,
    height: Optional[int] = None,
    width: Optional[int] = None,
    num_inference_steps: int = 50,
    timesteps: List[int] = None,
    sigmas: List[float] = None,
    denoising_end: Optional[float] = None,
    guidance_scale: float = 5.0,
    negative_prompt: Optional[Union[str, List[str]]] = None,
    negative_prompt_2: Optional[Union[str, List[str]]] = None,
    num_images_per_prompt: Optional[int] = 1,
    eta: float = 0.0,
    generator: Optional[Union[torch.Generator, List[torch.Generator]]] = None,
    latents: Optional[torch.Tensor] = None,
    prompt_embeds: Optional[torch.Tensor] = None,
    negative_prompt_embeds: Optional[torch.Tensor] = None,
    pooled_prompt_embeds: Optional[torch.Tensor] = None,
    negative_pooled_prompt_embeds: Optional[torch.Tensor] = None,
    ip_adapter_image: Optional[PipelineImageInput] = None,
    ip_adapter_image_embeds: Optional[List[torch.Tensor]] = None,
    output_type: Optional[str] = "pil",
    return_dict: bool = True,
    cross_attention_kwargs: Optional[Dict[str, Any]] = None,
    guidance_rescale: float = 0.0,
    original_size: Optional[Tuple[int, int]] = None,
    crops_coords_top_left: Tuple[int, int] = (0, 0),
    target_size: Optional[Tuple[int, int]] = None,
    negative_original_size: Optional[Tuple[int, int]] = None,
    negative_crops_coords_top_left: Tuple[int, int] = (0, 0),
    negative_target_size: Optional[Tuple[int, int]] = None,
    clip_skip: Optional[int] = None,
    callback_on_step_end: Optional[
        Union[Callable[[int, int, Dict], None], PipelineCallback, MultiPipelineCallbacks]
    ] = None,
    callback_on_step_end_tensor_inputs: List[str] = ["latents"],
    # ==========================================
    ref_intermediates: Optional[List[torch.Tensor]] = None,
    guidance_scale_LADG: float = 0.0,
    local_mask=None,
    # ==========================================
    **kwargs,
):
    callback = kwargs.pop("callback", None)
    callback_steps = kwargs.pop("callback_steps", None)

    if callback is not None:
        deprecate("callback", "1.0.0", "Passing `callback` is deprecated, consider use `callback_on_step_end`")
    if callback_steps is not None:
        deprecate("callback_steps", "1.0.0", "Passing `callback_steps` is deprecated, consider use `callback_on_step_end`")

    if isinstance(callback_on_step_end, (PipelineCallback, MultiPipelineCallbacks)):
        callback_on_step_end_tensor_inputs = callback_on_step_end.tensor_inputs

    height = height or self.default_sample_size * self.vae_scale_factor
    width = width or self.default_sample_size * self.vae_scale_factor

    original_size = original_size or (height, width)
    target_size = target_size or (height, width)

    self.check_inputs(
        prompt, prompt_2, height, width, callback_steps, negative_prompt, negative_prompt_2,
        prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds,
        ip_adapter_image, ip_adapter_image_embeds, callback_on_step_end_tensor_inputs,
    )

    self._guidance_scale = guidance_scale
    self._guidance_rescale = guidance_rescale
    self._clip_skip = clip_skip
    self._cross_attention_kwargs = cross_attention_kwargs
    self._denoising_end = denoising_end
    self._interrupt = False

    if prompt is not None and isinstance(prompt, str):
        batch_size = 1
    elif prompt is not None and isinstance(prompt, list):
        batch_size = len(prompt)
    else:
        batch_size = prompt_embeds.shape[0]

    device = self._execution_device
    lora_scale = self.cross_attention_kwargs.get("scale", None) if self.cross_attention_kwargs is not None else None

    (
        prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds,
    ) = self.encode_prompt(
        prompt=prompt, prompt_2=prompt_2, device=device, num_images_per_prompt=num_images_per_prompt,
        do_classifier_free_guidance=True, negative_prompt=negative_prompt,
        negative_prompt_2=negative_prompt_2, prompt_embeds=prompt_embeds, negative_prompt_embeds=negative_prompt_embeds,
        pooled_prompt_embeds=pooled_prompt_embeds, negative_pooled_prompt_embeds=negative_pooled_prompt_embeds,
        lora_scale=lora_scale, clip_skip=self.clip_skip,
    )

    timesteps, num_inference_steps = retrieve_timesteps(self.scheduler, num_inference_steps, device, timesteps, sigmas)

    num_channels_latents = self.unet.config.in_channels
    latents = self.prepare_latents(
        batch_size * num_images_per_prompt, num_channels_latents, height, width,
        prompt_embeds.dtype, device, generator, latents,
    )

    extra_step_kwargs = self.prepare_extra_step_kwargs(generator, eta)

    if local_mask is not None:
        local_mask = local_mask.unsqueeze(0).unsqueeze(0)
        local_mask = torch.nn.functional.interpolate(local_mask, size=(latents.shape[-2], latents.shape[-1]), mode="nearest")

    add_text_embeds = pooled_prompt_embeds
    text_encoder_projection_dim = int(pooled_prompt_embeds.shape[-1]) if self.text_encoder_2 is None else self.text_encoder_2.config.projection_dim

    add_time_ids = self._get_add_time_ids(
        original_size, crops_coords_top_left, target_size, dtype=prompt_embeds.dtype,
        text_encoder_projection_dim=text_encoder_projection_dim,
    )
    if negative_original_size is not None and negative_target_size is not None:
        negative_add_time_ids = self._get_add_time_ids(
            negative_original_size, negative_crops_coords_top_left, negative_target_size,
            dtype=prompt_embeds.dtype, text_encoder_projection_dim=text_encoder_projection_dim,
        )
    else:
        negative_add_time_ids = add_time_ids

    # =========================================================
    # ĐOẠN ĐÃ SỬA: ĐỒNG BỘ TEXT EMBEDDINGS LÊN BATCH SIZE 3
    # =========================================================
    if True:
        # Nhánh 1: Ref (dùng prompt_embeds hoặc rỗng, ở đây dùng prompt_embeds)
        # Nhánh 2: Uncond
        # Nhánh 3: Cond
        prompt_embeds = torch.cat([negative_prompt_embeds, negative_prompt_embeds, prompt_embeds], dim=0)
        
        # Tương tự cho pooled_embeds
        add_text_embeds = torch.cat([negative_pooled_prompt_embeds, negative_pooled_prompt_embeds, add_text_embeds], dim=0)
        
        # Tương tự cho time_ids
        add_time_ids = torch.cat([negative_add_time_ids, negative_add_time_ids, add_time_ids], dim=0)
        

    prompt_embeds = prompt_embeds.to(device)
    add_text_embeds = add_text_embeds.to(device)
    add_time_ids = add_time_ids.to(device).repeat(batch_size * num_images_per_prompt, 1)

    if ip_adapter_image is not None or ip_adapter_image_embeds is not None:
        image_embeds = self.prepare_ip_adapter_image_embeds(
            ip_adapter_image, ip_adapter_image_embeds, device, batch_size * num_images_per_prompt,
            True,
        )

    num_warmup_steps = max(len(timesteps) - num_inference_steps * self.scheduler.order, 0)
    if self.denoising_end is not None and isinstance(self.denoising_end, float) and 0 < self.denoising_end < 1:
        discrete_timestep_cutoff = int(
            round(self.scheduler.config.num_train_timesteps - (self.denoising_end * self.scheduler.config.num_train_timesteps))
        )
        num_inference_steps = len(list(filter(lambda ts: ts >= discrete_timestep_cutoff, timesteps)))
        timesteps = timesteps[:num_inference_steps]

    timestep_cond = None
    if self.unet.config.time_cond_proj_dim is not None:
        guidance_scale_tensor = torch.tensor(self.guidance_scale - 1).repeat(batch_size * num_images_per_prompt)
        timestep_cond = self.get_guidance_scale_embedding(
            guidance_scale_tensor, embedding_dim=self.unet.config.time_cond_proj_dim
        ).to(device=device, dtype=self.unet.dtype)
        if True:
            # Đồng bộ timestep_cond lên 3 phần
            timestep_cond = torch.cat([timestep_cond, timestep_cond, timestep_cond], dim=0)

    self._num_timesteps = len(timesteps)
    
    with self.progress_bar(total=num_inference_steps) as progress_bar:
        for i, t in enumerate(timesteps):
            if self.interrupt:
                continue

            if True:
                if ref_intermediates is not None and i < len(ref_intermediates):
                    ref_latent = ref_intermediates[-(i + 1)].to(device=latents.device, dtype=latents.dtype)
                    latent_model_input = torch.cat([ref_latent, latents, latents], dim=0)
                else:
                    latent_model_input = torch.cat([latents] * 3, dim=0)
            else:
                latent_model_input = latents

            latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)
            latent_model_input = latent_model_input.to(dtype=self.unet.dtype)

            added_cond_kwargs = {"text_embeds": add_text_embeds, "time_ids": add_time_ids}
            if ip_adapter_image is not None or ip_adapter_image_embeds is not None:
                added_cond_kwargs["image_embeds"] = image_embeds
            noise_pred = self.unet(
                latent_model_input,
                t,
                encoder_hidden_states=prompt_embeds,
                timestep_cond=timestep_cond,
                cross_attention_kwargs=self.cross_attention_kwargs,
                added_cond_kwargs=added_cond_kwargs,
                return_dict=False,
            )[0]

            # =========================================================
            # ĐOẠN ĐÃ SỬA: CHIA 3 NHÁNH TRƯỚC KHI TÍNH CFG
            # =========================================================
            if True:
                noise_pred_ref, noise_pred_uncond, noise_pred_text = noise_pred.chunk(3)
                noise_pred = noise_pred_uncond + self.guidance_scale * (noise_pred_text - noise_pred_uncond)

                if local_mask is not None and guidance_scale_LADG > 0.0:
                    noise_pred = (
                        noise_pred_uncond + guidance_scale_LADG * (noise_pred_text - noise_pred_uncond)
                    ) * local_mask + noise_pred_text * (1 - local_mask)

            if True and self.guidance_rescale > 0.0:
                noise_pred = rescale_noise_cfg(noise_pred, noise_pred_text, guidance_rescale=self.guidance_rescale)

            latents_dtype = latents.dtype
            latents = self.scheduler.step(noise_pred, t, latents, **extra_step_kwargs, return_dict=False)[0]
            if latents.dtype != latents_dtype:
                if torch.backends.mps.is_available():
                    latents = latents.to(latents_dtype)

            if callback_on_step_end is not None:
                callback_kwargs = {}
                for k in callback_on_step_end_tensor_inputs:
                    callback_kwargs[k] = locals()[k]
                callback_outputs = callback_on_step_end(self, i, t, callback_kwargs)
                latents = callback_outputs.pop("latents", latents)
                prompt_embeds = callback_outputs.pop("prompt_embeds", prompt_embeds)
                add_text_embeds = callback_outputs.pop("add_text_embeds", add_text_embeds)
                add_time_ids = callback_outputs.pop("add_time_ids", add_time_ids)

            if i == len(timesteps) - 1 or ((i + 1) > num_warmup_steps and (i + 1) % self.scheduler.order == 0):
                progress_bar.update()
                if callback is not None and i % callback_steps == 0:
                    step_idx = i // getattr(self.scheduler, "order", 1)
                    callback(step_idx, t, latents)

    if not output_type == "latent":
        needs_upcasting = self.vae.dtype == torch.float16 and self.vae.config.force_upcast
        if needs_upcasting:
            self.upcast_vae()
            latents = latents.to(next(iter(self.vae.post_quant_conv.parameters())).dtype)
        elif latents.dtype != self.vae.dtype:
            if torch.backends.mps.is_available():
                self.vae = self.vae.to(latents.dtype)

        has_latents_mean = hasattr(self.vae.config, "latents_mean") and self.vae.config.latents_mean is not None
        has_latents_std = hasattr(self.vae.config, "latents_std") and self.vae.config.latents_std is not None
        if has_latents_mean and has_latents_std:
            latents_mean = torch.tensor(self.vae.config.latents_mean).view(1, 4, 1, 1).to(latents.device, latents.dtype)
            latents_std = torch.tensor(self.vae.config.latents_std).view(1, 4, 1, 1).to(latents.device, latents.dtype)
            latents = latents * latents_std / self.vae.config.scaling_factor + latents_mean
        else:
            latents = latents / self.vae.config.scaling_factor

        image = self.vae.decode(latents, return_dict=False)[0]

        if needs_upcasting:
            self.vae.to(dtype=torch.float16)
    else:
        image = latents

    if not output_type == "latent":
        if self.watermark is not None:
            image = self.watermark.apply_watermark(image)
        image = self.image_processor.postprocess(image, output_type=output_type)

    self.maybe_free_model_hooks()

    if not return_dict:
        return (image,)

    return StableDiffusionXLPipelineOutput(images=image)
