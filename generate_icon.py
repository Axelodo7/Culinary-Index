"""Generate modern app icon matching the Warm Ember theme."""

import os
from PIL import Image, ImageDraw

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def draw_icon(size=512):
    """Draw a modern app icon with warm ember theme."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded square background with warm charcoal gradient
    radius = int(size * 0.22)
    margin = int(size * 0.02)
    
    # Create gradient background
    for y in range(size):
        # Gradient from dark charcoal (#1a1410) to slightly lighter (#2a2218)
        r = int(26 + (42 - 26) * (y / size))
        g = int(20 + (34 - 20) * (y / size))
        b = int(16 + (24 - 16) * (y / size))
        draw.line([(margin, y), (size - margin, y)], fill=(r, g, b))
    
    # Rounded square overlay for shape
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=radius,
        outline=(232, 115, 74, 40),
        width=max(2, size // 128),
    )

    cx = size // 2
    cy = size // 2

    # Cooking pot - simplified modern design
    pot_w = int(size * 0.28)
    pot_h = int(size * 0.22)
    pot_y = int(size * 0.42)
    
    # Pot body (rounded bowl)
    pot_x0 = cx - pot_w
    pot_y0 = pot_y - pot_h // 2
    pot_x1 = cx + pot_w
    pot_y1 = pot_y + pot_h // 2
    if pot_x1 > pot_x0 and pot_y1 > pot_y0:
        draw.ellipse(
            [pot_x0, pot_y0, pot_x1, pot_y1],
            fill=(232, 115, 74),
        )
    
    # Pot rim (wider)
    rim_w = int(size * 0.32)
    rim_h = int(size * 0.04)
    rim_x0 = cx - rim_w
    rim_y0 = pot_y - pot_h // 2 - rim_h
    rim_x1 = cx + rim_w
    rim_y1 = pot_y - pot_h // 2 + rim_h
    if rim_x1 > rim_x0 and rim_y1 > rim_y0:
        draw.rounded_rectangle(
            [rim_x0, rim_y0, rim_x1, rim_y1],
            radius=int(size * 0.02),
            fill=(212, 168, 67),
        )

    # Steam lines (3 vertical wavy lines)
    steam_color = (240, 232, 220, 180)
    steam_w = max(3, size // 85)
    for i, offset in enumerate([-0.15, 0, 0.15]):
        sx = cx + int(size * offset)
        start_y = pot_y - pot_h // 2 - rim_h - int(size * 0.02)
        end_y = start_y - int(size * 0.18)
        
        # Wavy line
        points = []
        segments = 12
        for t in range(segments + 1):
            tt = t / segments
            wave = int(size * 0.02 * (1 if t % 2 == 0 else -1))
            px = sx + wave
            py = start_y - int((start_y - end_y) * tt)
            points.append((px, py))
        
        if len(points) > 1:
            draw.line(points, fill=steam_color, width=steam_w)

    # Magnifying glass (bottom right, overlapping pot slightly)
    mg_r = int(size * 0.12)
    mg_cx = cx + int(size * 0.18)
    mg_cy = cy + int(size * 0.15)
    mg_line = max(2, size // 64)

    mg_x0 = mg_cx - mg_r
    mg_y0 = mg_cy - mg_r
    mg_x1 = mg_cx + mg_r
    mg_y1 = mg_cy + mg_r
    if mg_x1 > mg_x0 and mg_y1 > mg_y0 and mg_r > 2:
        # Glass circle with gold outline
        draw.ellipse(
            [mg_x0, mg_y0, mg_x1, mg_y1],
            outline=(212, 168, 67),
            width=mg_line,
        )
        
        # Glass fill (semi-transparent white)
        inner = [mg_x0 + mg_line, mg_y0 + mg_line, mg_x1 - mg_line, mg_y1 - mg_line]
        if inner[2] > inner[0] and inner[3] > inner[1]:
            draw.ellipse(
                inner,
                fill=(255, 255, 255, 50),
            )
        
        # Handle (diagonal, gold color)
        handle_len = max(2, int(size * 0.12))
        angle_start = (mg_cx + int(mg_r * 0.7), mg_cy + int(mg_r * 0.7))
        angle_end = (angle_start[0] + handle_len, angle_start[1] + handle_len)
        draw.line(
            [angle_start, angle_end],
            fill=(212, 168, 67),
            width=mg_line,
        )
        
        # Handle end cap
        cap_r = mg_line
        draw.ellipse(
            [angle_end[0] - cap_r, angle_end[1] - cap_r,
             angle_end[0] + cap_r, angle_end[1] + cap_r],
            fill=(212, 168, 67),
        )

    return img


def generate_all_assets():
    """Generate all icon sizes and formats."""
    # Generate .ico with multiple sizes
    sizes = [16, 32, 48, 64, 128, 256, 512]
    ico_images = []
    for s in sizes:
        ico_images.append(draw_icon(s))

    ico_path = os.path.join(ASSETS_DIR, "icon.ico")
    ico_images[0].save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in sizes[:-1]],  # ICO max 256
        append_images=ico_images[1:-1],
    )
    print(f"Created: {ico_path}")

    # Generate PNG at various sizes
    for s in [64, 128, 256, 512]:
        png_path = os.path.join(ASSETS_DIR, f"icon_{s}.png")
        draw_icon(s).save(png_path, format="PNG")
        print(f"Created: {png_path}")

    # Generate the PWA icon (512x512)
    pwa_path = os.path.join(os.path.dirname(ASSETS_DIR), "static", "icon-512.png")
    draw_icon(512).save(pwa_path, format="PNG")
    print(f"Created: {pwa_path}")

    # Generate Android adaptive icon components
    fg_path = os.path.join(ASSETS_DIR, "ic_launcher_foreground.png")
    draw_icon(432).save(fg_path, format="PNG")
    print(f"Created: {fg_path}")

    print("\nAll assets generated successfully!")


if __name__ == "__main__":
    generate_all_assets()
