import base64
import io

import requests
from PIL import Image

from app.schemas.multimodal import ImageEvidence


OLLAMA_URL = "http://localhost:11434/api/generate"
VISION_MODEL_NAME = "qwen3-vl:2b-instruct"

# CPU-only machine ke liye screenshot ko lightweight rakho.
MAX_IMAGE_SIZE = 640


def optimize_image(image_bytes: bytes) -> bytes:
    if not image_bytes:
        raise ValueError("Image data is empty.")

    try:
        image = Image.open(
            io.BytesIO(image_bytes)
        )

        image = image.convert("RGB")

    except Exception as exc:
        raise ValueError(
            "Uploaded file could not be opened as an image."
        ) from exc

    width, height = image.size
    largest_side = max(width, height)

    if largest_side > MAX_IMAGE_SIZE:
        scale = MAX_IMAGE_SIZE / largest_side

        new_width = max(
            1,
            int(width * scale)
        )

        new_height = max(
            1,
            int(height * scale)
        )

        image = image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS,
        )

    output = io.BytesIO()

    image.save(
        output,
        format="JPEG",
        quality=78,
        optimize=True,
    )

    return output.getvalue()


def analyze_image_with_ollama(
    prompt: str,
    image_bytes: bytes,
) -> str:

    optimized_image = optimize_image(
        image_bytes
    )

    encoded_image = base64.b64encode(
        optimized_image
    ).decode("utf-8")

    # IMPORTANT:
    # Instead of only saying format="json",
    # provide the actual Pydantic JSON schema.
    #
    # This strongly constrains Ollama/Qwen3-VL
    # to produce the structure our application expects.
    output_schema = (
        ImageEvidence.model_json_schema()
    )

    payload = {
        "model": VISION_MODEL_NAME,
        "prompt": prompt,
        "images": [
            encoded_image
        ],
        "stream": False,
        "think": False,

        # Structured output schema
        "format": output_schema,

        "options": {
            "temperature": 0.0,

            # 900 is a maximum, not a requirement.
            # Model may stop earlier after valid JSON.
            "num_predict": 900,
        },
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=900,
        )

        response.raise_for_status()

        data = response.json()

        model_response = data.get(
            "response"
        )

        if not model_response:
            raise RuntimeError(
                "Vision model returned an empty response."
            )

        return model_response

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running."
        ) from exc

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "Vision model request timed out."
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Ollama vision request failed: {exc}"
        ) from exc