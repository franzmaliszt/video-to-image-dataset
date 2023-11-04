import base64

import numpy as np
from decord import VideoReader


def encode_img(path: str) -> bytes:
    """Encodes an image into base64."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def dilute(video_path: str, dilution_rate: float, encode: bool) -> list[bytes] | np.ndarray:
    """
    Dilutes the video by the dilution rate and returns a list of frames.
    """
    vr = VideoReader(video_path)
    num_frames = len(vr)
    indices = [int(i) for i in np.linspace(0, num_frames - 1, int(num_frames * dilution_rate))]
    frames = vr.get_batch(indices).asnumpy()
    if encode:
        return [base64.b64encode(frame).decode() for frame in frames]
    return frames
