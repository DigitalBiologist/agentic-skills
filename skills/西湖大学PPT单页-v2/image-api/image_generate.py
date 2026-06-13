#!/usr/bin/env python3
"""Image Generation CLI Tool

Usage:
    python image_generate.py "prompt" [options]

Examples:
    python image_generate.py "A cute cat eating sushi" -o cat.jpg
    python image_generate.py "Mountain landscape" -r 4K -a 16:9 -o landscape.jpg
    python image_generate.py "Transform this photo" -i https://example.com/photo.jpg -o result.jpg
    python image_generate.py "" --check-credits
    python image_generate.py "" --provider nanobanana --check-credits
"""

import argparse
import sys
import os
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import provider_config as api


def save_prompt_sidecar(output_path, prompt, resolution, aspect_ratio, provider_name, image_urls=None):
    """Save prompt + generation params next to the output image.

    Creates <output_dir>/_prompts/<image_basename>.md so the same prompt can be
    quickly re-edited and re-run without hunting through shell history.
    Also writes a bare <image_basename>.prompt.txt for fast diff/reuse.
    """
    out_dir = os.path.dirname(os.path.abspath(output_path)) or "."
    basename = os.path.splitext(os.path.basename(output_path))[0]
    prompts_dir = os.path.join(out_dir, "_prompts")
    os.makedirs(prompts_dir, exist_ok=True)

    # 1) Bare prompt file (easy to `cat` and pipe back)
    txt_path = os.path.join(prompts_dir, f"{basename}.prompt.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(prompt)

    # 2) Rich markdown sidecar with all parameters for reproducibility
    md_path = os.path.join(prompts_dir, f"{basename}.md")
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    img_refs = "\n".join(f"- {u}" for u in image_urls) if image_urls else "(none)"
    md = f"""# {basename}

- **image**: `../{os.path.basename(output_path)}`
- **generated**: {ts}
- **provider**: {provider_name}
- **resolution**: {resolution}
- **aspect_ratio**: {aspect_ratio}
- **reference images**:
{img_refs}

## Prompt

```
{prompt}
```

## Re-run command

```bash
python {os.path.abspath(__file__)} "$(cat "{txt_path}")" \\
  -r {resolution} -a {aspect_ratio} \\
  -o "{output_path}"
```
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    return md_path


def main():
    parser = argparse.ArgumentParser(description=f"Image Generation ({api.PROVIDER_NAME})")
    parser.add_argument("prompt", help="Text prompt for image generation")
    parser.add_argument("-o", "--output", default="output.jpg", help="Output file path (default: output.jpg)")
    parser.add_argument("-r", "--resolution", default=api.DEFAULT_RESOLUTION,
                        choices=api.SUPPORTED_RESOLUTIONS, help=f"Resolution (default: {api.DEFAULT_RESOLUTION})")
    parser.add_argument("-a", "--aspect-ratio", default=api.DEFAULT_ASPECT_RATIO,
                        choices=api.SUPPORTED_ASPECT_RATIOS, help=f"Aspect ratio (default: {api.DEFAULT_ASPECT_RATIO})")
    parser.add_argument("-i", "--images", nargs="+", help="Reference image URLs (image-to-image mode)")
    parser.add_argument("--check-credits", action="store_true", help="Check remaining credits and exit")
    parser.add_argument("--provider", choices=list(api.PROVIDERS.keys()),
                        help=f"Override active provider (current: {api.ACTIVE_PROVIDER})")
    parser.add_argument("--no-save-prompt", action="store_true",
                        help="Disable saving prompt sidecar files (default: save to _prompts/)")

    args = parser.parse_args()

    # Provider override
    if args.provider:
        api.ACTIVE_PROVIDER = args.provider
        api.PROVIDER_NAME = api.PROVIDERS[args.provider]["name"]

    api_key = api.get_api_key()

    # Check credits
    if args.check_credits:
        credits = api.check_credits(api_key)
        if credits is not None:
            print(f"Remaining credits: {credits}")
        else:
            print(f"Provider '{api.ACTIVE_PROVIDER}' uses per-request billing (no credit balance)")
        sys.exit(0)

    credits = api.check_credits(api_key)
    if credits is not None:
        print(f"Credits: {credits}")
        if credits <= 0:
            print("Error: No credits remaining", file=sys.stderr)
            sys.exit(1)

    # Generate
    print(f"Provider: {api.PROVIDER_NAME}")
    print(f"Prompt: {args.prompt}")
    print(f"Resolution: {args.resolution}, Aspect Ratio: {args.aspect_ratio}")

    try:
        result_path = api.generate_image(
            prompt=args.prompt,
            output_path=args.output,
            resolution=args.resolution,
            aspect_ratio=args.aspect_ratio,
            image_urls=args.images,
        )
        print(f"Saved to: {result_path}")

        if not args.no_save_prompt and args.prompt.strip():
            sidecar = save_prompt_sidecar(
                output_path=result_path,
                prompt=args.prompt,
                resolution=args.resolution,
                aspect_ratio=args.aspect_ratio,
                provider_name=api.PROVIDER_NAME,
                image_urls=args.images,
            )
            print(f"Prompt saved: {sidecar}")
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
