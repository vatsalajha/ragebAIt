from google import genai
from google.genai import types
import base64
import os
from PIL import Image
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def process_image(image_path: str, output_path: str = None) -> dict:
    """
    Process a sports image through Nano Banana (Gemini's native image generation):
    1. Analyze the image and generate a gen-z sports meme prompt + caption
    2. Use Nano Banana to generate/edit the image based on the prompt
    
    Args:
        image_path: Path to the input sports image file
        output_path: Optional path to save the generated image
        
    Returns:
        Dictionary payload ready for social media posting:
        - image: PIL Image object of the generated meme
        - caption: Social media caption with hashtags
        - image_prompt: The prompt used to generate the image
        - output_path: Path where image was saved (if provided)
    """
    # Initialize client with Vertex AI (uses gcloud auth)
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    client = genai.Client(vertexai=True, project=project_id, location=location)
    
    # Load the input image bytes
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    # Determine mime type
    extension = image_path.lower().split(".")[-1]
    mime_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp"
    }
    mime_type = mime_types.get(extension, "image/jpeg")
    
    # Step 1: Analyze the image and get meme content from Gemini
    analysis_prompt = """Analyze this sports image and create gen-z meme content for it.
    
    This is a SPORTS image - focus on the athletic context, players, teams, game moments, 
    fan reactions, or sports culture shown.
    
    Respond in this exact JSON format:
    {
        "image_prompt": "<a detailed prompt for generating/editing the image into a sports meme>",
        "caption": "<a short, punchy social media caption with relevant hashtags for Twitter/Instagram, max 280 chars>",
        "style": "<choose one: deepfried, surreal, wholesome, cursed, clean, chaotic>"
    }
    
    STYLE OPTIONS (pick what fits the vibe best):
    - "deepfried": Oversaturated colors, lens flares, emojis, warped/distorted, ironic humor. Best for absurd or ironic moments.
    - "surreal": Weird edits, unexpected objects, dreamlike, makes no sense but is funny. Good for bizarre plays or reactions.
    - "wholesome": Clean edit with heartwarming twist, feel-good energy. For touching sports moments.
    - "cursed": Unsettling, weird cropping, ominous energy, "this image has an aura". For awkward or creepy frames.
    - "clean": Professional-looking meme, clear text overlays, polished. For moments that speak for themselves.
    - "chaotic": Maximum chaos, multiple elements, sensory overload, gen-z brain rot energy. For wild game moments.
    
    Make it funny, relatable to sports fans, and capture that chaotic gen-z meme energy.
    Use sports references, player/team jokes, and current meme formats.
    Only respond with the JSON, nothing else."""

    analysis_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    types.Part.from_text(text=analysis_prompt)
                ]
            )
        ]
    )
    
    # Parse the JSON response
    import json
    import re
    try:
        response_text = analysis_response.text.strip()
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            response_text = json_match.group(1).strip()
        meme_content = json.loads(response_text)
    except json.JSONDecodeError:
        meme_content = {
            "image_prompt": analysis_response.text.strip(),
            "caption": "🔥 Sports moment hits different #sports #meme"
        }
    
    print(f"Gemini generated prompt: {meme_content['image_prompt']}")
    print(f"Social caption: {meme_content['caption']}")
    print(f"Style: {meme_content.get('style', 'clean')}")
    
    # Step 2: Use Nano Banana (Gemini 3 Pro Image) to generate/edit the image
    style = meme_content.get('style', 'clean')
    
    style_instructions = {
        "deepfried": "Deep fry this image with oversaturated colors, add lens flares, random emojis (😂🔥💀), slight warping/distortion, and crusty JPEG artifacts.",
        "surreal": "Make this surreal and dreamlike - add unexpected objects, weird perspective shifts, or absurd elements that don't belong.",
        "wholesome": "Keep this clean and heartwarming - subtle edits that enhance the feel-good moment.",
        "cursed": "Make this cursed - unsettling cropping, ominous lighting, weird blur effects, 'this image has an aura' energy.",
        "clean": "Create a clean, polished meme - clear composition with any text overlays crisp and readable.",
        "chaotic": "Maximum chaos - add multiple meme elements, overlay effects, sensory overload, pure gen-z brain rot energy."
    }
    
    style_prompt = style_instructions.get(style, style_instructions["clean"])
    edit_prompt = f"{style_prompt} Transform this sports image into a gen-z meme: {meme_content['image_prompt']}"
    
    from io import BytesIO
    
    image_response = client.models.generate_content(
        model="gemini-3-pro-image-preview",  # Nano Banana Pro - Gemini 3 Pro Image
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    types.Part.from_text(text=edit_prompt)
                ]
            )
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"]
        )
    )
    
    # Extract the generated image from the response
    generated_image = None
    for part in image_response.candidates[0].content.parts:
        if part.inline_data is not None:
            # The data is already bytes
            image_data = part.inline_data.data
            if isinstance(image_data, str):
                image_data = base64.b64decode(image_data)
            generated_image = Image.open(BytesIO(image_data))
            break
    
    if generated_image is None:
        raise ValueError("No image was generated by Nano Banana")
    
    # Save if output path provided
    if output_path:
        generated_image.save(output_path)
    
    print(f"Image generated successfully!")
    
    # Return payload ready for social media platforms
    return {
        "image": generated_image,
        "caption": meme_content['caption'],
        "image_prompt": meme_content['image_prompt'],
        "output_path": output_path
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python banana.py <image_path> [output_path]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "generated_meme.png"
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        sys.exit(1)
    
    result = process_image(image_path, output_path)
    print("\n--- Results ---")
    print(f"Image Prompt: {result['image_prompt']}")
    print(f"Caption: {result['caption']}")
    print(f"Image saved to: {output_path}")
