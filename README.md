# sd-hiresfix-batch-upscaler

A Python script to batch upscale multiple images at once using Stable Diffusion WebUI(Automatic1111)'s **Hires.fix** feature.
It reads each image's metadata (PNG Info) and regenerates it under the same conditions with Hires.fix enabled.


## Features

- Reads images from a specified folder and parses metadata (PNG Info)
- Sends the original prompt and settings to the WebUI API
- Enables Hires.fix to upscale the images
- Saves the upscaled images to a specified output folder
- Moves the original processed images to another folder


## Installation & Initial Setup

### 1. Clone this repository

```bash
git clone https://github.com/nelke-jp/sd-hiresfix-batch-upscaler.git
````


### 2. Configure the script

Open `hires_batch_upscaler.py` in a text editor.


### 3. Set directory paths

Edit the following lines in `hires_batch_upscaler.py` to match your environment:

**Settings:**

* `INPUT_DIR` : Directory for images you want to upscale
* `OUTPUT_DIR` : Directory to save upscaled images
* `DONE_DIR` : Directory to move original images after processing (set to `None` if you don't want to move them)

**Example:**

```python
# Input directory
INPUT_DIR = r"C:\StableDiffusion\upscale"
# Output directory
OUTPUT_DIR = r"C:\StableDiffusion\upscale\output"
# Directory to move original files after processing (if None, do not move)
DONE_DIR = r"C:\StableDiffusion\upscale\done"
# DONE_DIR = None
```


### 4. Set Hires.fix upscaler settings

Edit these values in `hires_batch_upscaler.py` as needed:

**Example:**

```python
# Upscaler
HR_UPSCALER = "4x-UltraSharp"
# Denoising strength
DENOISING_STRENGTH = 0.2
# Upscale factor
HR_SCALE = 2
# Hires steps (if None, same as original sampling steps)
HR_SECOND_PASS_STEPS = 20
```


### 5. Set URL settings

Edit these values in `hires_batch_upscaler.py` as needed:

**Example:**

```python
BASE_URL = "http://127.0.0.1:7860"
```


### 6. Enable API in Stable Diffusion WebUI

Open your `webui-user.bat` in a text editor.

Add the `--api` option to `COMMANDLINE_ARGS`.

**Example:**

```
set COMMANDLINE_ARGS=--xformers --api
```


## How to Use

1. Start your Stable Diffusion Automatic1111 WebUI locally.

2. Make sure the images you want to upscale are placed in the directory specified by `INPUT_DIR`.
   Each image must contain the correct prompt and parameter metadata.

3. On Windows, run the script by double-clicking `run_hires_batch_upscaler.bat`.
   On other platforms, use the commands below.


## Commands


### 1. Create a virtual environment

```bash
python -m venv venv
```


### 2. Activate the virtual environment

* Windows

  ```bash
  venv\Scripts\activate
  ```

* macOS/Linux

  ```bash
  source venv/bin/activate
  ```


### 3. Install dependencies

```bash
pip install -r requirements.txt
```


### 4. Run the script

```bash
python hires_batch_upscaler.py
```

When finished, upscaled images will be saved to the directory specified by `OUTPUT_DIR`.
The original processed images will be moved to the `DONE_DIR` folder.


## Requirements

* Python 3.9+
* Stable Diffusion WebUI(Automatic1111) running
* Images must contain valid PNG Info metadata


## License

MIT License
