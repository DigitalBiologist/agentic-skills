"""Image Generation Provider Config - Single Source of Truth

Supports multiple providers with a single high-level interface.
Callers only need: generate_image(), check_credits(), get_api_key()

To switch providers: change ACTIVE_PROVIDER below.
To add a new provider: add its config to PROVIDERS and implement _xxx_generate().

Available providers:
  - "laozhang"    : LaoZhang AI proxy (sync, Google Native format, $0.05/image)
  - "nanobanana"  : NanoBanana Pro direct (async poll, $0.24/image equivalent)
"""

import base64
import os
import sys
import time
import requests

# ============================================================
# ACTIVE PROVIDER - 默认 laozhang；运行时可用环境变量 IMAGE_PROVIDER 覆盖
#   (e.g. IMAGE_PROVIDER=apiyi python3 image_generate.py ...)
# ============================================================

ACTIVE_PROVIDER = os.environ.get("IMAGE_PROVIDER", "apiyi")

# ============================================================
# Provider Registry
# ============================================================

PROVIDERS = {
    "laozhang": {
        "name": "LaoZhang AI (Nano Banana Pro)",
        "api_key_env": "LAOZHANG_API_KEY",  # 读取 ~/.zshrc export（当前密钥 2026-04-20 更新，值以环境变量为准）
        "api_base": "https://api.laozhang.ai",
        "model": "gemini-3-pro-image-preview",
        "mode": "sync",  # POST → base64 response
        "price": "$0.05/image",
    },
    "nanobanana": {
        "name": "NanoBanana Pro (Direct)",
        "api_key_env": "NANOBANANA_API_KEY",  # 备用 provider；key 从环境变量读，勿硬编码
        "api_base": "https://api.nanobananaapi.ai/api/v1",
        "mode": "async",  # submit → poll → download URL (备用)
        "price": "~18 credits/image (2K)",
    },
    "apiyi": {
        "name": "APIYI (Gemini 3 Pro Image / NBP)",
        "api_key_env": "APIYI_API_KEY",  # 推荐：export APIYI_API_KEY 到 ~/.zshrc，优先读环境变量
        "api_key_default": "",            # 可选 fallback：把你自己的 APIYI key 填到这两个引号之间即可（留空则必须用环境变量）
        "api_base": "https://api.apiyi.com",
        "model": "gemini-3-pro-image-preview",
        "mode": "sync",  # Google Native: POST :generateContent → base64（与 laozhang 同格式）
        "price": "按量计费",
    },
}

# Generation defaults
DEFAULT_RESOLUTION = "2K"
DEFAULT_ASPECT_RATIO = "1:1"
SUPPORTED_RESOLUTIONS = ["1K", "2K", "4K"]
SUPPORTED_ASPECT_RATIOS = [
    "1:1", "2:3", "3:2", "3:4", "4:3",
    "4:5", "5:4", "9:16", "16:9", "21:9", "auto",
]

# Retry / timeout config
MAX_RETRIES = 3
RETRY_DELAY = 3  # seconds
POLL_INTERVAL = 3  # seconds (nanobanana only)
MAX_WAIT = 300  # seconds

# Derived
PROVIDER_NAME = PROVIDERS[ACTIVE_PROVIDER]["name"]

# ============================================================
# Public API - Callers use these
# ============================================================


def get_api_key():
    """Get API key for the active provider."""
    cfg = PROVIDERS[ACTIVE_PROVIDER]
    env_var = cfg["api_key_env"]
    key = os.environ.get(env_var) or cfg.get("api_key_default")
    if not key:
        print(f"Error: {env_var} not set. Export it or add to ~/.zshrc", file=sys.stderr)
        sys.exit(1)
    return key


def check_credits(api_key):
    """Check remaining credits/balance. Returns value or None if unsupported."""
    if ACTIVE_PROVIDER == "nanobanana":
        return _nanobanana_check_credits(api_key)
    # LaoZhang: per-request billing, no credits endpoint
    return None


def generate_image(prompt, output_path, resolution=None, aspect_ratio=None, image_urls=None):
    """Generate an image and save to output_path.

    This is the only function callers need. It handles all provider differences internally.

    Args:
        prompt: Text prompt for generation
        output_path: Where to save the image (str or Path)
        resolution: "1K", "2K", or "4K" (default: 2K)
        aspect_ratio: e.g. "16:9", "1:1" (default: 1:1)
        image_urls: Optional list of reference image URLs (image-to-image)

    Returns:
        str: output_path on success

    Raises:
        RuntimeError: on failure
    """
    resolution = resolution or DEFAULT_RESOLUTION
    aspect_ratio = aspect_ratio or DEFAULT_ASPECT_RATIO
    api_key = get_api_key()
    output_path = str(output_path)

    if ACTIVE_PROVIDER in ("laozhang", "apiyi"):
        return _laozhang_generate(api_key, prompt, output_path, resolution, aspect_ratio, image_urls)
    elif ACTIVE_PROVIDER == "nanobanana":
        return _nanobanana_generate(api_key, prompt, output_path, resolution, aspect_ratio, image_urls)
    else:
        raise RuntimeError(f"Unknown provider: {ACTIVE_PROVIDER}")


# ============================================================
# LaoZhang AI Implementation (sync, Google Native format)
# ============================================================


def _laozhang_generate(api_key, prompt, output_path, resolution, aspect_ratio, image_urls=None):
    """Google Native format: POST → base64 response. 服务于所有 google-native sync provider
    (laozhang / apiyi)，base_url + model 取自当前 ACTIVE_PROVIDER 的配置。"""
    base_url = PROVIDERS[ACTIVE_PROVIDER]["api_base"]
    model = PROVIDERS[ACTIVE_PROVIDER]["model"]
    url = f"{base_url}/v1beta/models/{model}:generateContent"

    # Build parts. Reference images can be remote URLs (fileData.fileUri) or
    # LOCAL FILE PATHS — local files are read + base64-inlined (inlineData),
    # which enables true image-editing on files that aren't publicly hosted.
    parts = [{"text": prompt}]
    if image_urls:
        for img_ref in image_urls:
            is_remote = img_ref.startswith(("http://", "https://"))
            local_path = img_ref[7:] if img_ref.startswith("file://") else img_ref
            if not is_remote and os.path.exists(local_path):
                ext = os.path.splitext(local_path)[1].lower()
                mime = "image/png" if ext == ".png" else "image/webp" if ext == ".webp" else "image/jpeg"
                with open(local_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("ascii")
                parts.append({"inlineData": {"mimeType": mime, "data": b64}})
            else:
                parts.append({"fileData": {"fileUri": img_ref, "mimeType": "image/jpeg"}})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio if aspect_ratio != "auto" else "1:1",
                "imageSize": resolution,
            },
        },
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = None
    elapsed = 0
    for attempt in range(MAX_RETRIES):
        try:
            print(f"\r  Generating...", end="", flush=True)
            start = time.time()
            resp = requests.post(url, headers=headers, json=payload, timeout=180)
            elapsed = int(time.time() - start)
            resp.raise_for_status()
            data = resp.json()
            break
        except requests.exceptions.HTTPError:
            if resp.status_code in (429, 502, 503) and attempt < MAX_RETRIES - 1:
                print(f"\r  HTTP {resp.status_code}, retry {attempt+1}/{MAX_RETRIES}...", file=sys.stderr)
                time.sleep(RETRY_DELAY * (2 ** attempt))
                continue
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"Network failed after {MAX_RETRIES} retries: {e}")
            print(f"\r  Network error, retry {attempt+1}/{MAX_RETRIES}...", file=sys.stderr)
            time.sleep(RETRY_DELAY)

    if data is None:
        raise RuntimeError("No response received")

    # Extract base64 image from response
    try:
        candidates = data.get("candidates", [])
        if not candidates:
            error = data.get("error", {}).get("message", "No candidates in response")
            raise RuntimeError(f"Generation failed: {error}")

        parts = candidates[0]["content"]["parts"]
        image_part = None
        for part in parts:
            if "inlineData" in part:
                image_part = part["inlineData"]
                break

        if not image_part:
            raise RuntimeError("No image data in response")

        image_bytes = base64.b64decode(image_part["data"])
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Failed to parse response: {e}")

    # Save
    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print(f"\r  Done! ({elapsed}s)       ")
    return output_path


# ============================================================
# NanoBanana Pro Direct Implementation (async poll)
# ============================================================


def _nanobanana_check_credits(api_key):
    base_url = PROVIDERS["nanobanana"]["api_base"]
    try:
        resp = requests.get(
            f"{base_url}/common/credit",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=15,
        )
        data = resp.json()
        if data.get("code") == 200:
            return data.get("data", 0)
        print(f"Warning: Failed to check credits: {data.get('msg')}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Credit check failed: {e}", file=sys.stderr)
    return None


def _nanobanana_generate(api_key, prompt, output_path, resolution, aspect_ratio, image_urls=None):
    """Async flow: submit → poll → download URL."""
    base_url = PROVIDERS["nanobanana"]["api_base"]
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # Submit. Reference images may be remote URLs OR local file paths; local
    # files are downscaled (<=2048px long edge) and inlined as base64 data URIs
    # so editing works without any third-party image host.
    payload = {"prompt": prompt, "resolution": resolution, "aspectRatio": aspect_ratio}
    if image_urls:
        resolved = []
        for ref in image_urls:
            if ref.startswith(("http://", "https://", "data:")):
                resolved.append(ref)
                continue
            path = ref[7:] if ref.startswith("file://") else ref
            if not os.path.exists(path):
                resolved.append(ref)
                continue
            try:
                from PIL import Image
                import io
                im = Image.open(path).convert("RGB")
                im.thumbnail((2048, 2048))
                buf = io.BytesIO()
                im.save(buf, format="JPEG", quality=92)
                b64 = base64.b64encode(buf.getvalue()).decode("ascii")
                resolved.append(f"data:image/jpeg;base64,{b64}")
            except Exception:
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("ascii")
                ext = os.path.splitext(path)[1].lower().lstrip(".") or "png"
                resolved.append(f"data:image/{ext};base64,{b64}")
        payload["imageUrls"] = resolved

    data = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(f"{base_url}/nanobanana/generate-pro", headers=headers, json=payload, timeout=30)
            data = resp.json()
            break
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"Network failed after {MAX_RETRIES} retries: {e}")
            print(f"  Network error, retry {attempt+1}/{MAX_RETRIES}...", file=sys.stderr)
            time.sleep(RETRY_DELAY)

    if data is None:
        raise RuntimeError("No response received")
    if data.get("code") != 200:
        raise RuntimeError(f"Submit failed: {data.get('msg') or data.get('message')}")

    task_id = data["data"]["taskId"]

    # Poll
    poll_headers = {"Authorization": f"Bearer {api_key}"}
    start = time.time()
    retries = 0

    while time.time() - start < MAX_WAIT:
        try:
            resp = requests.get(
                f"{base_url}/nanobanana/record-info",
                headers=poll_headers, params={"taskId": task_id}, timeout=15,
            )
            result = resp.json()
            retries = 0
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
            retries += 1
            if retries > MAX_RETRIES:
                raise RuntimeError(f"Network failed after {MAX_RETRIES} retries: {e}")
            time.sleep(POLL_INTERVAL)
            continue

        if result.get("code") != 200:
            raise RuntimeError(f"Poll error: {result.get('msg')}")

        flag = result.get("data", {}).get("successFlag", 0)
        if flag == 0:
            elapsed = int(time.time() - start)
            print(f"\r  Generating... ({elapsed}s)", end="", flush=True)
            time.sleep(POLL_INTERVAL)
        elif flag == 1:
            elapsed = int(time.time() - start)
            print(f"\r  Done! ({elapsed}s)       ")
            response = result["data"].get("response", {})
            image_url = response.get("resultImageUrl") or response.get("originImageUrl")
            if not image_url:
                raise RuntimeError("No image URL in response")
            # Download
            return _download_url(image_url, output_path)
        elif flag == 2:
            raise RuntimeError(f"Task creation failed: {result['data'].get('errorMessage', 'unknown')}")
        elif flag == 3:
            raise RuntimeError(f"Generation failed: {result['data'].get('errorMessage', 'unknown')}")

    raise RuntimeError("Timeout waiting for generation")


def _download_url(url, output_path):
    """Download image from URL to file."""
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, stream=True, timeout=120)
            resp.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            return output_path
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
            if attempt == MAX_RETRIES - 1:
                raise
            print(f"  Download error, retry {attempt+1}/{MAX_RETRIES}...", file=sys.stderr)
            time.sleep(RETRY_DELAY)
