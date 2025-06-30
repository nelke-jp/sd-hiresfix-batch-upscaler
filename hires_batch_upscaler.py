import os
import re
import base64
import shutil
import requests
import logging
from requests.exceptions import RequestException
from PIL import Image, PngImagePlugin

# ===============================
# Directories
# ===============================

# Input folder
INPUT_DIR = r"your input directory"
# Output folder
OUTPUT_DIR = r"your output directory"
# Folder to move original files after processing (if None, do not move)
DONE_DIR = r"your done directory"

# ===============================
# Hires.fix Constants
# ===============================

# Upscaler
HR_UPSCALER = "4x-UltraSharp"
# Denoising strength
DENOISING_STRENGTH = 0.2
# Upscale factor
HR_SCALE = 2
# Hires steps (if None, same as original sampling steps)
HR_SECOND_PASS_STEPS = 20

# ===============================
# API endpoint
# ===============================

# txt2img API endpoint
API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"

# ===============================
# Setup logging
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)


def parse_parameters(parameters: str):
    """
    Parse PNG Info parameters.
    Returns ready-to-use payload dict or None if required fields are missing.
    """
    parts = parameters.split("Negative prompt:")
    prompt = parts[0].strip() if len(parts) > 0 else None

    negative_prompt, others = "", ""
    if len(parts) > 1:
        negative_prompt, others = parts[1].split("\n", 1)
        negative_prompt = negative_prompt.strip()

    settings = {}
    for line in others.strip().split(", "):
        if ": " in line:
            k, v = line.split(": ", 1)
            settings[k.strip()] = v.strip()

    width, height = None, None
    if "Size" in settings:
        match = re.match(r"(\d+)x(\d+)", settings["Size"])
        if match:
            width, height = int(match.group(1)), int(match.group(2))

    steps = int(settings.get("Steps")) if "Steps" in settings else None
    sampler_name = settings.get("Sampler") if "Sampler" in settings else None
    cfg_scale = float(settings.get("CFG scale")) if "CFG scale" in settings else None
    seed = int(settings.get("Seed")) if "Seed" in settings else None

    required = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "sampler_name": sampler_name,
        "cfg_scale": cfg_scale,
        "seed": seed,
        "width": width,
        "height": height,
    }

    missing = [k for k, v in required.items() if v is None or v == ""]
    if missing:
        logging.warning(f"❌ Missing required parameters : {missing}")
        return None

    payload = {
        **required,
        "enable_hr": True,
        "denoising_strength": DENOISING_STRENGTH,
        "hr_scale": HR_SCALE,
        "hr_upscaler": HR_UPSCALER,
        "hr_second_pass_steps": HR_SECOND_PASS_STEPS or steps,
    }

    return payload


def hires_upscale(file_path: str, filename: str) -> None:
    """
    Process a single PNG image with hires fix.
    """
    if not filename.lower().endswith(".png"):
        return

    with PngImagePlugin.PngImageFile(file_path) as img:
        parameters = img.info.get("parameters")

    if not parameters:
        logging.warning(f"⏭️ Skipped : {filename} (No parameters found)")
        return

    payload = parse_parameters(parameters)
    if not payload:
        logging.warning(f"⏭️ Skipped : {filename} (Invalid parameters)")
        return

    logging.info(f"🚀 Processing : {filename}")

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
    except RequestException as e:
        logging.error(f"❌ Request failed for {filename} : {e}")
        return

    result = response.json()
    for i, image in enumerate(result.get("images", [])):
        output_path = os.path.join(
            OUTPUT_DIR,
            f"{os.path.splitext(filename)[0]}_hires.png"
        )
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(image))
        logging.info(f"✅ Saved: {output_path}")

    if DONE_DIR:
        shutil.move(file_path, os.path.join(DONE_DIR, filename))
        logging.info(f"➡️ Moved original file to: {DONE_DIR}")


def main():
    """
    Main processing loop.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if DONE_DIR:
        os.makedirs(DONE_DIR, exist_ok=True)

    for filename in os.listdir(INPUT_DIR):
        hires_upscale(os.path.join(INPUT_DIR, filename), filename)

    logging.info("✅ All images processed with Hires.fix.")


if __name__ == "__main__":
    main()
