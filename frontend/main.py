import os

import httpx
import gradio as gr
from dotenv import load_dotenv

# from decord import VideoReader


load_dotenv()
BACKEND_PORT = os.environ["BACKEND_PORT"]
FRONTEND_PORT = int(os.environ["FRONTEND_PORT"])


def on_upload_frames(paths: set[str], evt: gr.EventData):
    new_paths = {img["orig_name"]: img["name"] for img in evt._data}
    paths.update(new_paths)


def on_upload_video(paths: dict[str, str], evt: gr.EventData):
    paths.update({evt._data["orig_name"]: evt._data["name"]})


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


def display_images(files, gallery, evt: gr.SelectData):
    in_gallery = [
        img["name"] for img in gallery if not img["name"].split("/")[-1] == evt.value
    ]
    if len(in_gallery) == len(gallery):
        for file in files:
            if file.name.split("/")[-1] == evt.value:
                in_gallery.append(file.name)
                break
    return in_gallery


async def submit(
    video_path: str, frame_objs: list[dict], output_size: int, sample_rate: float
) -> list:
    if not 2 < len(frame_objs) < 6:
        raise gr.Error("Please upload between 3 and 5 frames.")
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
    with gr.Row():
        with gr.Column(scale=2):
            with gr.Tab("Search"):
                with gr.Row():
                    in_video_dropdown = gr.Dropdown(
                        scale=5,
                        label="Sample video",
                        interactive=False,
                    )
                    upload_video = gr.UploadButton(
                        "Upload", variant="primary", file_types=["mp4"]
                    )
                with gr.Row():
                    input_frames = gr.Dropdown(
                        multiselect=True,
                        max_choices=5,
                        label="Sample frames",
                        interactive=False,
                        scale=5,
                    )
                    upload_frames = gr.UploadButton(
                        "Upload",
                        variant="primary",
                        file_count="multiple",
                        file_types=["image"],
                    )
                with gr.Row(variant="compact"):
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
                run_btn = gr.Button(value="Run", variant="primary")
            with gr.Tab("Files"):
                uploaded = gr.State(dict())
                file_system = gr.File(
                    # value=["data/stomach-ulcer.mp4", "data/ulcer-01.jpg"],
                    file_count="multiple",
                    file_types=["image", "mp4"],
                    label="File system",
                    interactive=False,
                )
        with gr.Column(scale=1):
            with gr.Tab("Display"):
                input_video = gr.Video(format="mp4", label="Video", interactive=False)
                input_gallery = gr.Gallery(
                    label="Sample frames",
                    allow_preview=False,
                    columns=3,
                    object_fit="contain",
                    show_download_button=False,
                )
            with gr.Tab("Result"):
                dataset = gr.Gallery(label="Result dataset")
                with gr.Box():
                    with gr.Row(variant="default", equal_height=True):
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

    demo.load(initialize, outputs=[])
    upload_video.upload(on_upload_video, inputs=[uploaded]).success(
        upload_success,
        inputs=uploaded,
        outputs=[file_system, in_video_dropdown, input_frames],
    )
    upload_frames.upload(on_upload_frames, inputs=[uploaded]).success(
        upload_success,
        inputs=uploaded,
        outputs=[file_system, in_video_dropdown, input_frames],
    )
    in_video_dropdown.select(display_video, inputs=file_system, outputs=[input_video])
    input_frames.select(
        display_images, inputs=[file_system, input_gallery], outputs=[input_gallery]
    )
    run_btn.click(
        submit,
        inputs=[input_video, input_gallery, output_size, sample_rate],
        outputs=[dataset],
    )


if __name__ == "__main__":
    demo.launch(server_port=FRONTEND_PORT, server_name="0.0.0.0")
    # demo.launch(debug=True, server_port=8022, server_name="0.0.0.0")
