import os

import httpx
import gradio as gr 
from dotenv import load_dotenv


load_dotenv()
BACKEND_PORT = os.environ['BACKEND_PORT']
FRONTEND_PORT = int(os.environ['FRONTEND_PORT'])


def on_upload_frames(frames: list):
    file_names = [f.name for f in frames]
    if not 2 < len(frames) < 6:
        raise gr.Error("Please upload between 3 and 5 frames.")
    return file_names


def on_upload_video(video):
    url = f"http://worker"


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

with gr.Blocks(title="Towards Gesund") as demo:
    gr.Markdown("""# Content based image retrieval""")
    with gr.Accordion("Docs", open=False):
        gr.HTML("""<h3>To be added...</h3>""")
    with gr.Row():
        with gr.Column(scale=2):
            with gr.Tab("Video") as video_tab:
                input_video = gr.Video(format="mp4", label="Video", interactive=True, include_audio=False)
            with gr.Tab("Samples") as samples_tab:
                frame_samples = gr.Gallery(
                    label="Sample frames",
                    allow_preview=False,
                    columns=3,
                    object_fit="contain",
                    show_download_button=False,
                )
                upload_frames = gr.UploadButton(
                    label="Upload frames",
                    variant="primary",
                    file_count="multiple",
                    file_types=["image"],
                )
            with gr.Tab("Configuration") as config_tab:
                output_size = gr.Slider(
                    minimum=1, maximum=100, value=50, step=1, interactive=True
                )
        with gr.Column(scale=1):
            dataset = gr.Gallery()  # TODO: Consider gr.Dataset()
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
                        value="↓", variant="primary", size="lg", min_width=50
                    )

    upload_frames.upload(
        on_upload_frames, inputs=[upload_frames], outputs=[frame_samples]
    )
    input_video.upload(on_upload_video, inputs=[input_video])


if __name__ == "__main__":
    demo.launch(server_port=FRONTEND_PORT, server_name="0.0.0.0")