#!/usr/bin/env python3
"""
Generate favicon files with white circle + sprout design
"""
from PIL import Image, ImageDraw
from pathlib import Path

def create_favicon_image(size):
    """Create a single favicon image at given size with white circle + sprout"""
    # Scale factor for anti-aliasing
    scale = 4
    hi_res_size = size * scale

    # Circle should be most of the canvas
    circle_size = int(hi_res_size * 0.92)  # 92% of canvas
    padding = (hi_res_size - circle_size) // 2

    # Create high-resolution background with white circle
    background = Image.new('RGBA', (hi_res_size, hi_res_size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(background)

    # Draw white circle
    draw.ellipse([padding, padding, padding + circle_size - 1, padding + circle_size - 1],
                fill='white', outline='white')

    # Load and paste the sprout icon (centered)
    # Icon should be about 64% of circle (so there's white border)
    icon_size = int(circle_size * 0.64)

    # Load the highest res source we have
    icon_path = Path(__file__).parent / "sprout_icon_512.png"
    if not icon_path.exists():
        icon_path = Path(__file__).parent / "sprout_icon_128.png"

    icon_image = Image.open(icon_path)
    icon_image = icon_image.resize((icon_size, icon_size), Image.Resampling.LANCZOS)

    # Center the icon
    icon_offset = (hi_res_size - icon_size) // 2
    background.paste(icon_image, (icon_offset, icon_offset), icon_image if icon_image.mode == 'RGBA' else None)

    # Downsample to final size with high-quality Lanczos filter
    background = background.resize((size, size), Image.Resampling.LANCZOS)

    return background


def generate_favicons(output_dir):
    """Generate all favicon sizes"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate individual PNG sizes
    sizes = {
        16: 'favicon-16x16.png',
        32: 'favicon-32x32.png',
        48: 'favicon-48x48.png',
        180: 'apple-touch-icon.png',  # Apple touch icon
        192: 'android-chrome-192x192.png',  # Android
        512: 'android-chrome-512x512.png',  # Android
    }

    images_for_ico = []

    for size, filename in sizes.items():
        print(f"Generating {filename}...")
        img = create_favicon_image(size)
        img.save(output_dir / filename)

        # Collect sizes for .ico file (16, 32, 48)
        if size in [16, 32, 48]:
            # Convert RGBA to RGB with white background for ICO compatibility
            if img.mode == 'RGBA':
                rgb_img = Image.new('RGB', (size, size), 'white')
                rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                images_for_ico.append(rgb_img)
            else:
                images_for_ico.append(img)

    # Create multi-size .ico file
    print("Generating favicon.ico...")
    if images_for_ico:
        images_for_ico[0].save(
            output_dir / 'favicon.ico',
            format='ICO',
            sizes=[(img.width, img.height) for img in images_for_ico]
        )

    print(f"\n✓ Favicons generated in {output_dir}")


if __name__ == "__main__":
    import sys

    # Default to farming-advisor-ui/app directory
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        # Auto-detect farming-advisor-ui
        script_dir = Path(__file__).parent.parent.parent
        output_dir = script_dir / "farming-advisor-ui" / "app"

    generate_favicons(output_dir)
