# handler.py
import runpod
import io
import gc
import traceback
import torch
import pybase64
import zstandard
from time import time
from typing import TypedDict

from engine.data_structures import (
    RequestData,
    ResponseData,
    GaussianSplattingData,
    TimeStat,
    ValidationResultData,
)
from engine.io.ply import PlyLoader
from engine.rendering.renderer import Renderer
from engine.utils.gs_data_checker_utils import is_input_data_valid
from engine.validation_engine import ValidationEngine
from PIL import Image


# --- Global components (loaded once per worker) ---
validator = ValidationEngine()
validator.load_pipelines()
ply_data_loader = PlyLoader()
renderer = Renderer()
zstd_decompressor = zstandard.ZstdDecompressor()


# --- Input schema for RunPod ---
class RunPodInput(TypedDict):
    data: str
    prompt: str
    compression: int
    generate_preview: bool
    preview_score_threshold: float


# --- Helper functions ---
def decode_assets(request: RequestData) -> bytes:
    t1 = time()
    assets = pybase64.b64decode(request.data, validate=True)
    if request.compression == 1:
        assets = zstd_decompressor.decompress(assets)
    elif request.compression == 2:
        import pyspz
        assets = pyspz.decompress(assets, include_normals=False)
    return assets


def prepare_input_data(assets: bytes) -> tuple[GaussianSplattingData | None, list[torch.Tensor], TimeStat]:
    time_stat = TimeStat()
    t1 = time()
    pcl_buffer = io.BytesIO(assets)
    gs_data = ply_data_loader.from_buffer(pcl_buffer)
    t2 = time()
    time_stat.loading_data_time = t2 - t1

    if not is_input_data_valid(gs_data):
        return None, [], time_stat

    gs_data_gpu = gs_data.send_to_device(validator.device)
    images = renderer.render_gs(gs_data_gpu, 16, 224, 224)
    t3 = time()
    time_stat.image_rendering_time = t3 - t2
    return gs_data_gpu, images, time_stat


def validate_text_vs_image(prompt: str, images: list[torch.Tensor]) -> 'ValidationResult':
    t1 = time()
    result = validator.validate_text_to_gs(prompt, images)
    result.validation_time = time() - t1
    return result


def render_preview_image(gs_data: GaussianSplattingData, score: float, threshold: float) -> str | None:
    if score > threshold:
        buffered = io.BytesIO()
        image = renderer.render_gs(gs_data, 1, 512, 512, [25.0], [-10.0])[0]
        preview = Image.fromarray(image.detach().cpu().numpy())
        preview.save(buffered, format="PNG")
        return pybase64.b64encode(buffered.getvalue()).decode("utf-8")
    return None


def finalize_results(result, gs_data, generate_preview, threshold) -> ResponseData:
    preview = render_preview_image(gs_data, result.final_score, threshold) if generate_preview else None
    return ResponseData(
        score=result.final_score,
        iqa=result.combined_quality_score,
        alignment_score=result.alignment_score,
        ssim=result.ssim_score,
        lpips=result.lpips_score,
        preview=preview,
    )


def cleanup():
    gc.collect()
    torch.cuda.empty_cache()


# --- Main RunPod Job Handler ---
def handler(job_input: RunPodInput) -> dict:
    try:
        request = RequestData(**job_input)

        # Decode and load data
        assets = decode_assets(request)
        gs_data, images, time_stat = prepare_input_data(assets)

        if gs_data and request.prompt:
            result = validate_text_vs_image(request.prompt, images)
            time_stat.validation_time = result.validation_time
            response = finalize_results(result, gs_data, request.generate_preview, request.preview_score_threshold)
        else:
            response = ResponseData(score=0.0)

        return response.dict()

    except Exception as e:
        traceback.print_exc()
        return {"score": 0.0, "error": str(e)}

    finally:
        cleanup()


runpod.serverless.start({"handler": handler})
