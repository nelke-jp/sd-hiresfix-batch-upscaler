import os
import base64
import shutil
import requests
import logging
from requests.exceptions import RequestException

# ===============================
# Directories
# ===============================

# Input directory
INPUT_DIR = r"your input directory"
# Output directory
OUTPUT_DIR = r"your output directory"
# Directory to move original files after processing (if None, do not move)
DONE_DIR = r"your done directory"

# ===============================
# Hires.fix
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
# URL
# ===============================

BASE_URL = "http://127.0.0.1:7860"

# ===============================
# Logging
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)


def get_parameters(image_path: str) -> dict | None:
    try:
        with open(image_path, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode("utf-8")
        payload = {"image": f"data:image/png;base64,{encoded_image}"}
        response = requests.post(f"{BASE_URL}/sdapi/v1/png-info", json=payload)
        response.raise_for_status()
        return response.json().get("parameters")
    except RequestException as e:
        logging.warning(
            f"❌ Failed to get PNG info for {os.path.basename(image_path)}: {e}"
        )
        return None


def create_payload(parameters: dict) -> dict | None:
    try:
        required = {
            "sampler_name": parameters.get("Sampler"),
            "steps": int(parameters.get("Steps")) if parameters.get("Steps") else None,
            "cfg_scale": (
                float(parameters.get("CFG scale"))
                if parameters.get("CFG scale")
                else None
            ),
            "seed": int(parameters.get("Seed")) if parameters.get("Seed") else None,
            "width": (
                int(parameters.get("Size-1")) if parameters.get("Size-1") else None
            ),
            "height": (
                int(parameters.get("Size-2")) if parameters.get("Size-2") else None
            ),
        }
    except ValueError as e:
        logging.warning(f"❌ Invalid numeric value: {e}")
        return None

    missing = [k for k, v in required.items() if v is None or v == ""]
    if missing:
        logging.warning(f"❌ Missing required parameters : {missing}")
        return None

    payload = {
        **required,
        "prompt": parameters.get("Prompt"),
        "negative_prompt": parameters.get("Negative prompt"),
        "enable_hr": True,
        "denoising_strength": DENOISING_STRENGTH,
        "hr_scale": HR_SCALE,
        "hr_upscaler": HR_UPSCALER,
        "hr_second_pass_steps": HR_SECOND_PASS_STEPS or required["steps"],
    }

    return payload


def hires_upscale(filename: str) -> None:
    logging.info(f"🚀 Processing : {filename}")

    file_path = os.path.join(INPUT_DIR, filename)
    parameters = get_parameters(file_path)
    if not parameters:
        logging.warning(f"⏭️ Skipped: {filename} (No valid parameters)")
        return

    payload = create_payload(parameters)
    if not payload:
        logging.warning(f"⏭️ Skipped: {filename} (Invalid or missing parameters)")
        return

    try:
        response = requests.post(f"{BASE_URL}/sdapi/v1/txt2img", json=payload)
        response.raise_for_status()
    except RequestException as e:
        logging.error(f"❌ Request failed for {filename} : {e}")
        return

    for i, image in enumerate(response.json().get("images", [])):
        output_path = os.path.join(
            OUTPUT_DIR, f"{os.path.splitext(filename)[0]}_hires.png"
        )
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(image))
        logging.info(f"✅ Saved: {output_path}")

    if DONE_DIR:
        shutil.move(file_path, os.path.join(DONE_DIR, filename))
        logging.info(f"➡️ Moved original file to: {DONE_DIR}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if DONE_DIR:
        os.makedirs(DONE_DIR, exist_ok=True)

    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".png"):
            hires_upscale(filename)

    logging.info("✅ All images processed with Hires.fix.")


if __name__ == "__main__":
    main()
