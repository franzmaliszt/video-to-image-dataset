import os

import httpx
import gradio as gr
from dotenv import load_dotenv
import numpy as np

# from decord import VideoReader


load_dotenv()
BACKEND_PORT = os.environ["BACKEND_PORT"]
FRONTEND_PORT = int(os.environ["FRONTEND_PORT"])


def on_upload(paths: set[str], evt: gr.EventData):
    new_paths = {img["orig_name"]: img["name"] for img in evt._data}
    paths.update(new_paths)


def upload_success(paths: dict[str, str]):
    videos = [p for p in paths if p.endswith(".mp4")]
    images = [p for p in paths if not p.endswith(".mp4")]
    video_dropdown = gr.Dropdown(choices=videos, interactive=len(videos))
    image_dropdown = gr.Dropdown(choices=images, interactive=len(images))
    return list(paths.values()), video_dropdown, image_dropdown


def display_video(files, evt: gr.SelectData):
    for file in files:
        if file.name.split("/")[-1] == evt.value:
            return file.name


# inputs=[file_system, input_gallery], outputs=[input_gallery]
# def display_images(files, gallery, evt: gr.SelectData):
#     in_gallery = [
#         img["name"] for img in gallery if not img["name"].split("/")[-1] == evt.value
#     ]
#     if len(in_gallery) == len(gallery):
#         for file in files:
#             if file.name.split("/")[-1] == evt.value:
#                 in_gallery.append(file.name)
#                 break
#     return in_gallery


def display_img(selected: str, files):
    for file in files:
        if file.name.split("/")[-1] == selected:
            return file.name


def sketch(canvas, gallery):
    # if len(gallery) == 5:
    #     raise gr.Error("Can't have more than 5 frames.")
    in_gallery = [img["name"] for img in gallery]

    nonzero_indices = np.nonzero(canvas["mask"])
    min_x, max_x = np.min(nonzero_indices[1]), np.max(nonzero_indices[1])
    min_y, max_y = np.min(nonzero_indices[0]), np.max(nonzero_indices[0])
    roi = canvas["image"][min_y:max_y, min_x:max_x]

    return in_gallery + [roi]


def undo(gallery):
    return [img["name"] for img in gallery][:-1]


async def submit(
    video_path: str, frame_objs: list[dict], output_size: int, sample_rate: float
) -> list:
    if len(frame_objs) < 3:
        raise gr.Error("Please upload minimum 3 frames.")
    frame_paths = [metadata["name"] for metadata in frame_objs]
    async with httpx.AsyncClient() as client:
        response = client.post(
            f"http://backend:{BACKEND_PORT}/test",
            json={
                "video_path": video_path,
                "frame_paths": frame_paths,
                "output_size": output_size,
                "sample_rate": sample_rate,
            },
        )
        response.raise_for_status()
        return response.json().get("result", [])
    # return list of images


async def hello(text: str):
    url = f"http://backend:{BACKEND_PORT}/test/hello{text}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
    return response.json().get("message", "Error")

    # url = f"http://backend:{BACKEND_PORT}/test/hello"
    # data = {"text": text}
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(url, json=data)
    #     response.raise_for_status()
    # return response.json().get("message", "Error")


def initialize():
    ...


with gr.Blocks(title="Towards Gesund") as demo:
    gr.Markdown("""# Content based image retrieval""")
    with gr.Accordion("Docs", open=False):
        gr.HTML("""<h3>To be added...</h3>""")
    with gr.Row(equal_height=False):
        with gr.Column(variant="panel", scale=2):
            with gr.Row():
                with gr.Column():
                    gr.HTML("""<h3>1. Select a video</h3>""")
                    video_dropdown = gr.Dropdown(show_label=False, min_width=480, interactive=True)
                    gr.HTML("""<h3>2. Select images to annotate</h3>""")
                    image_dropdown = gr.Dropdown(show_label=False, min_width=480)
                    gr.HTML("""<h3>3. Options</h3>""")
                    with gr.Row():
                        output_size = gr.Slider(
                            minimum=1,
                            maximum=100,
                            value=40,
                            step=1,
                            label="Result size in images",
                            interactive=True,
                        )
                        sample_rate = gr.Number(
                            minimum=0.1,
                            maximum=1,
                            value=0.5,
                            step=0.1,
                            label="Auto-stride",
                            interactive=True,
                        )
                with gr.Column(scale=3):
                    # TODO: make canvas interactive=False, see issue: #5945
                    sketch_pad = gr.Image(tool="sketch")
                    with gr.Row(variant="panel"):
                        annotate_btn = gr.Button(
                            value="Confirm Annotation", variant="primary", scale=0
                        )
                        undo_btn = gr.Button(value="Undo", scale=0, min_width=80)
        with gr.Column(scale=1):
            with gr.Tab("Experiments"):
                input_video = gr.Video(format="mp4", label="Video", interactive=False)
                input_gallery = gr.Gallery(
                    label="Sample frames",
                    allow_preview=False,
                    columns=3,
                    object_fit="contain",
                    show_download_button=False,
                )
                run_btn = gr.Button(value="Run", variant="primary", scale=0, min_width=160)
            with gr.Tab("Result"):
                dataset = gr.Gallery(label="Result dataset")
                with gr.Group():
                    with gr.Row(equal_height=True):
                        output_formats = gr.Dropdown(
                            ["DICOM", "NIFTI", "PNG", "JPEG", "TIFF"],
                            label="Output Format",
                            scale=4,
                            min_width=50,
                            interactive=True,
                        )
                        download_btn = gr.Button(
                            value="↓", variant="secondary", min_width=50
                        )
            with gr.Accordion("Files"):
                uploaded = gr.State(dict())
                upload_btn = gr.UploadButton(
                    "Upload",
                    scale=0,
                    file_count="multiple",
                    file_types=["jpg", "jpeg", "png", "mp4"],
                )
                file_system = gr.File(
                    file_count="multiple",
                    file_types=["image", "mp4"],
                    label="File system",
                    interactive=False,
                )

    demo.load(initialize, outputs=[])
    upload_btn.upload(on_upload, inputs=[uploaded]).success(
        upload_success,
        inputs=uploaded,
        outputs=[file_system, video_dropdown, image_dropdown],
    )
    video_dropdown.select(display_video, inputs=file_system, outputs=[input_video])
    image_dropdown.select(
        display_img, inputs=[image_dropdown, file_system], outputs=[sketch_pad]
    )
    annotate_btn.click(
        sketch, inputs=[sketch_pad, input_gallery], outputs=input_gallery
    ).then(display_img, inputs=[image_dropdown, file_system], outputs=[sketch_pad])
    undo_btn.click(undo, inputs=input_gallery, outputs=input_gallery)
    run_btn.click(
        submit,
        inputs=[input_video, input_gallery, output_size, sample_rate],
        outputs=[dataset],
    )


if __name__ == "__main__":
    # demo.launch(server_port=FRONTEND_PORT, server_name="0.0.0.0")
    demo.launch(debug=True, server_port=8022, server_name="0.0.0.0")
