import os
from pathlib import Path
import logging

import clip 
from dotenv import load_dotenv

# load_dotenv()
# CLIP_MODEL = os.getenv("CLIP_MODEL") #FIXME: This is returning None for some reason

model_dir = Path(__file__).parent / "models"
model_name = "ViT-B/16"

clip.load(model_name, download_root=model_dir, cache=True)