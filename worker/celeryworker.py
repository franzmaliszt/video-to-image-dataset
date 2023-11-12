import os
import time
import base64
from io import BytesIO
from itertools import islice
from typing import Iterable

import torch
from PIL import Image
from celery import Celery
from celery.utils.log import get_task_logger
from dotenv import load_dotenv

from clip import load
from retrieval import embed_images, similarity


load_dotenv()
logger = get_task_logger(__name__)

app = Celery(__name__)
app.config_from_object("config")

@app.task(name="hello_task")
def hello(text: str) -> str:
    time.sleep(5)
    return f"Hello {text}"

@app.task(name="sample_loop_task")
def sample_task():
    for i in range(5):  
        time.sleep(5)
    print(f"Task {i} completed!")

@app.task(name="submit_task")
def submit_task(video_encodings: list[str], image_encodings: list[str], output_size: int) -> list[int]:
    CLIP_MODEL = "ViT-B/16"
    images = [b64_to_pil(b64) for b64 in image_encodings]
    model, preprocess = load(CLIP_MODEL, download_root="models/", device="cpu")
    image_embeddings = embed_images(model, preprocess, images)
    sims = []
    for batch in batchify(video_encodings, 10):
        frames = [b64_to_pil(b64) for b64 in batch]
        frame_embeddings = embed_images(model, preprocess, frames)
        sims.appends(similarity(image_embeddings, frame_embeddings))
    all_sims = torch.cat(sims)
    return {"frame_indices": all_sims.topk(output_size).indices.tolist()}

def b64_to_pil(data: str) -> Image:
    """Converts base64 to PIL Image."""
    data = base64.b64decode(data)
    return Image.open(BytesIO(data))

def batchify(iterable: Iterable, batch_size: int = 10):
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch
