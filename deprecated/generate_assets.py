"""Generate application icon and logo assets programmatically using Pillow."""

import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

def draw_icon(size=256):
    """Draw a cooking pot with steam and a magnifying glass overlay."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle
    margin = int(size * 0.05)
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=(74, 111, 165),  # Slate blue
        outline=(54, 91, 145),
        width=max(2, size // 64),
    )

    # Cooking pot body
    cx = size // 2
    pot_top = int(size * 0.35)
    pot_bottom = int(size * 0.72)
    pot_left = int(size * 0.22)
    pot_right = int(size * 0.78)

    # Pot body (trapezoid-ish)
    pot_points = [
        (pot_left, pot_top),
        (pot_right, pot_top),
        (int(size * 0.72), pot_bottom),
        (int(size * 0.28), pot_bottom),
    ]
    draw.polygon(pot_points, fill=(200, 200, 200), outline=(180, 180, 180))

    # Pot rim
    rim_height = int(size * 0.04)
    draw.rectangle(
        [pot_left - int(size * 0.04), pot_top - rim_height,
         pot_right + int(size * 0.04), pot_top + rim_height],
        fill=(220, 220, 220),
        outline=(190, 190, 190),
    )

    # Pot handles
    handle_w = int(size * 0.06)
    handle_h = int(size * 0.08)
    # Left handle
    draw.rounded_rectangle(
        [pot_left - handle_w - int(size * 0.02), pot_top + int(size * 0.04),
         pot_left - int(size * 0.01), pot_top + int(size * 0.04) + handle_h],
        radius=int(size * 0.015),
        fill=(180, 180, 180),
    )
    # Right handle
    draw.rounded_rectangle(
        [pot_right + int(size * 0.01), pot_top + int(size * 0.04),
         pot_right + handle_w + int(size * 0.02), pot_top + int(size * 0.04) + handle_h],
        radius=int(size * 0.015),
        fill=(180, 180, 180),
    )

    # Steam wisps
    steam_color = (255, 255, 255, 180)
    steam_w = max(2, size // 64)
    for offset_x, offset_h in [(-0.12, 0.08), (0.0, 0.12), (0.12, 0.06)]:
        sx = cx + int(size * offset_x)
        sy = pot_top - rim_height - int(size * 0.02)
        curve_points = []
        for t in range(20):
            tt = t / 19.0
            px = sx + int(size * 0.03 * (1 if offset_x >= 0 else -1) *
                          (0.5 - abs(tt - 0.5)) * 2)
            py = sy - int(size * offset_h * tt)
            curve_points.append((px, py))
        if len(curve_points) > 1:
            draw.line(curve_points, fill=steam_color, width=steam_w)

    # Magnifying glass (bottom-right)
    mg_cx = int(size * 0.65)
    mg_cy = int(size * 0.65)
    mg_r = max(4, int(size * 0.15))
    mg_line_w = max(2, size // 48)

    # Glass circle
    bbox = [mg_cx - mg_r, mg_cy - mg_r, mg_cx + mg_r, mg_cy + mg_r]
    if bbox[2] > bbox[0] and bbox[3] > bbox[1]:
        draw.ellipse(bbox, outline=(255, 255, 255), width=mg_line_w)
        # Glass fill (semi-transparent)
        inner = [bbox[0] + mg_line_w, bbox[1] + mg_line_w,
                 bbox[2] - mg_line_w, bbox[3] - mg_line_w]
        if inner[2] > inner[0] and inner[3] > inner[1]:
            draw.ellipse(inner, fill=(255, 255, 255, 60))
    # Handle
    handle_start_x = mg_cx + int(mg_r * 0.7)
    handle_start_y = mg_cy + int(mg_r * 0.7)
    handle_end_x = handle_start_x + max(2, int(size * 0.15))
    handle_end_y = handle_start_y + max(2, int(size * 0.15))
    draw.line(
        [(handle_start_x, handle_start_y), (handle_end_x, handle_end_y)],
        fill=(255, 255, 255),
        width=mg_line_w,
    )

    return img


def generate_all_assets():
    """Generate all icon sizes and formats."""
    # Generate .ico with multiple sizes (Windows needs this)
    sizes = [16, 32, 48, 64, 128, 256]
    ico_images = []
    for s in sizes:
        ico_images.append(draw_icon(s))

    ico_path = os.path.join(ASSETS_DIR, "icon.ico")
    ico_images[0].save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=ico_images[1:],
    )
    print(f"Created: {ico_path}")

    # Generate PNG at 256x256
    png_path = os.path.join(ASSETS_DIR, "icon.png")
    draw_icon(256).save(png_path, format="PNG")
    print(f"Created: {png_path}")

    # Generate small PNG for in-app use
    small_png = os.path.join(ASSETS_DIR, "icon_small.png")
    draw_icon(64).save(small_png, format="PNG")
    print(f"Created: {small_png}")

    print("\nAll assets generated successfully!")


if __name__ == "__main__":
    generate_all_assets()
