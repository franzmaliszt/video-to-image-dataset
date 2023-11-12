import os
import logging

import torch
from dotenv import load_dotenv
from PIL import Image
from clip import load


# load_dotenv()
# CLIP_MODEL = os.getenv("CLIP_MODEL")
CLIP_MODEL = "ViT-B/16"

def embed_images(model, preprocess, images: list[Image.Image]) -> torch.Tensor:
    """Embeds list of images using CLIP."""
    batch_tensor = torch.stack([preprocess(image) for image in images])#.cuda()
    with torch.no_grad():
        batch_features = model.encode_image(batch_tensor).float()
        batch_features /= batch_features.norm(dim=-1, keepdim=True)
    return batch_features#.to("cpu")

def similarity(img_embed: torch.Tensor, frm_embed: torch.Tensor) -> torch.Tensor:
    """Compares images and frames for similarity."""
    similarities = img_embed @ frm_embed.T * 100.0
    return similarities
