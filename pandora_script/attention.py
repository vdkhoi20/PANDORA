import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange, repeat


class AttentionBase:
    def __init__(self, max_step=50):
        self.cur_step = 0
        self.num_att_layers = -1
        self.cur_att_layer = 0
        self.max_step = max_step

    def reset(self):
        self.cur_att_layer = 0
        self.cur_step = 0

    def after_step(self):
        self.cur_att_layer = 0
        self.cur_step = (self.cur_step + 1) % self.max_step
        if self.cur_step == 0:
            self.reset()

    def __call__(self, q, k, v, sim, attn, is_cross, place_in_unet, num_heads, **kwargs):
        out = self.forward(q, k, v, sim, attn, is_cross, place_in_unet, num_heads, **kwargs)
        self.cur_att_layer += 1
        if self.cur_att_layer == self.num_att_layers:
            self.after_step()
        return out

    def forward(self, q, k, v, sim, attn, is_cross, place_in_unet, num_heads, **kwargs):
        out = torch.einsum("b i j, b j d -> b i d", attn, v)
        return rearrange(out, "(b h) n d -> b n (h d)", h=num_heads)


def register_attention_editor_diffusers(model, editor: AttentionBase):
    def ca_forward(self, place_in_unet):
        def forward(x, encoder_hidden_states=None, attention_mask=None, context=None, mask=None):
            if encoder_hidden_states is not None:
                context = encoder_hidden_states
            if attention_mask is not None:
                mask = attention_mask

            to_out = self.to_out
            if isinstance(to_out, nn.modules.container.ModuleList):
                to_out = self.to_out[0]

            h = self.heads
            q = self.to_q(x)
            is_cross = context is not None
            context = context if is_cross else x
            k = self.to_k(context)
            v = self.to_v(context)
            q, k, v = map(lambda t: rearrange(t, "b n (h d) -> (b h) n d", h=h), (q, k, v))

            sim = torch.einsum("b i d, b j d -> b i j", q, k) * self.scale
            if mask is not None:
                mask = rearrange(mask, "b ... -> b (...)")
                max_neg_value = -torch.finfo(sim.dtype).max
                mask = repeat(mask, "b j -> (b h) () j", h=h)
                mask = mask[:, None, :].repeat(h, 1, 1)
                sim.masked_fill_(~mask, max_neg_value)

            attn = sim.softmax(dim=-1)
            out = editor(q, k, v, sim, attn, is_cross, place_in_unet, self.heads, scale=self.scale)
            return to_out(out)

        return forward

    def register_editor(net, count, place_in_unet):
        for _, subnet in net.named_children():
            if net.__class__.__name__ == "Attention":
                net.forward = ca_forward(net, place_in_unet)
                return count + 1
            if hasattr(net, "children"):
                count = register_editor(subnet, count, place_in_unet)
        return count

    count = 0
    for net_name, net in model.unet.named_children():
        if "down" in net_name:
            count += register_editor(net, 0, "down")
        elif "mid" in net_name:
            count += register_editor(net, 0, "mid")
        elif "up" in net_name:
            count += register_editor(net, 0, "up")
    editor.num_att_layers = count


class PandoraSelfAttentionControl(AttentionBase):
    MODEL_LAYERS = {"sd15": 16, "sd21": 16, "sdxl": 70}

    def __init__(self, start_step=45, start_layer=17, layer_idx=None, step_idx=None, total_steps=50, version="sd15"):
        super().__init__(total_steps)
        total_layers = self.MODEL_LAYERS.get(version, 16)
        self.version = version
        self.layer_idx = layer_idx if layer_idx is not None else list(range(start_layer, total_layers + 1))
        self.step_idx = step_idx if step_idx is not None else list(range(start_step, total_steps + 1))


class PandoraSelfAttentionControlMask(PandoraSelfAttentionControl):
    def __init__(
        self,
        start_step=45,
        start_layer=17,
        layer_idx=None,
        step_idx=None,
        total_steps=50,
        mask=None,
        dilated_mask=None,
        percentile=95,
        version="sd15",
    ):
        super().__init__(start_step, start_layer, layer_idx, step_idx, total_steps, version)
        self.mask = mask
        self.dilated_mask = dilated_mask
        self.percentile = percentile

    def _mask(self, h, w, dtype, device):
        mask = self.mask.clone().to(device=device)
        mask = F.interpolate(mask.unsqueeze(0).unsqueeze(0), (h, w), mode="nearest")
        return mask.flatten().to(dtype)

    def attn_mask(self, q, k, v, num_heads, **kwargs):
        batch = q.shape[0] // num_heads
        h = w = int(np.sqrt(q.shape[1]))
        q = rearrange(q, "(b h) n d -> b h n d", h=num_heads)
        sim = torch.einsum("b h i d, h j d -> b h i j", q, k) * kwargs.get("scale")
        mask = self._mask(h, w, sim.dtype, sim.device)
        sim = sim + mask.view(1, 1, 1, -1).masked_fill(mask.view(1, 1, 1, -1) == 1, torch.finfo(sim.dtype).min)
        attn = sim.softmax(-1)
        out = torch.einsum("b h i j, h j d -> b h i d", attn, v)
        return rearrange(out, "b h n d -> b n (h d)", b=batch, h=num_heads)

    def threshold_by_percentile(self, sim_softmax, percentile):
        threshold = torch.quantile(sim_softmax.float(), percentile / 100.0, dim=-1, keepdim=True)
        return sim_softmax >= threshold.to(sim_softmax.device)

    def cngd_ao(self, q, k, v, num_heads, percentile=95, **kwargs):
        batch = q.shape[0] // num_heads
        h = w = int(np.sqrt(q.shape[1]))
        q = rearrange(q, "(b h) n d -> b h n d", h=num_heads)
        sim = torch.einsum("b h i d, h j d -> b h i j", q, k) * kwargs.get("scale")
        mask_sr = self._mask(h, w, sim.dtype, sim.device)
        mask_sr = mask_sr.view(1, 1, 1, -1)
        sim_softmax = sim.masked_fill(mask_sr == 1, torch.finfo(sim.dtype).min).softmax(-1)
        mask = self.threshold_by_percentile(sim_softmax, percentile)
        sim = sim.masked_fill(mask == 1, torch.finfo(sim.dtype).min)
        sim = sim.masked_fill(mask_sr == 1, torch.finfo(sim.dtype).min)
        attn = sim.softmax(-1)
        out = torch.einsum("b h i j, h j d -> b h i d", attn, v)
        return rearrange(out, "b h n d -> b n (h d)", b=batch, h=num_heads)

    def forward(self, q, k, v, sim, attn, is_cross, place_in_unet, num_heads, **kwargs):
        h = w = int(np.sqrt(q.shape[1]))
        out_self = super().forward(q, k, v, sim, attn, is_cross, place_in_unet, num_heads, **kwargs)
        batch = out_self.shape[0]
        invert = batch == 1

        if invert or is_cross or self.cur_step in self.step_idx:
            return out_self

        if batch == 2:
            out_source, _ = out_self.chunk(2)
            q_target = q[-num_heads:]
        elif batch == 3:
            out_source, out_u, out_c = out_self.chunk(3)
            q_target = q[-2 * num_heads :]
        else:
            return out_self

        out_object = self.cngd_ao(q_target, k[:num_heads], v[:num_heads], num_heads, self.percentile, **kwargs)
        out_background = self.attn_mask(q_target, k[:num_heads], v[:num_heads], num_heads, **kwargs)
        mask = self._mask(h, w, out_object.dtype, out_object.device).reshape(-1, 1).clamp(0.01, 0.99)
        if batch == 3:
            mask = mask.unsqueeze(0)

        out_target = out_object * mask + out_background * (1 - mask)
        if batch == 2:
            return torch.cat([out_source, out_target], dim=0)

        out_u, out_c = out_target.chunk(2)
        return torch.cat([out_source, out_u, out_c], dim=0)
