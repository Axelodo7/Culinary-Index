"""Generate app icon matching the Warm Ember website theme."""

import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def draw_icon(size=512):
    """Draw a clean icon matching the Warm Ember website."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded square background
    radius = int(size * 0.20)

    # Warm charcoal gradient background (matches website)
    for y in range(size):
        t = y / size
        r = int(26 + 16 * t)
        g = int(20 + 14 * t)
        b = int(16 + 8 * t)
        draw.line([(0, y), (size - 1, y)], fill=(r, g, b))

    # Rounded square mask
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    img.putalpha(mask)

    cx = size // 2
    cy = size // 2

    # ===== Cooking Pot =====
    pot_w = int(size * 0.22)
    pot_h = int(size * 0.18)
    pot_y = int(size * 0.48)

    # Pot body - warm orange ellipse
    draw.ellipse(
        [cx - pot_w, pot_y - pot_h // 2, cx + pot_w, pot_y + pot_h // 2],
        fill=(232, 115, 74),
    )

    # Pot rim - gold bar
    rim_w = int(size * 0.26)
    rim_h = int(size * 0.035)
    draw.rounded_rectangle(
        [cx - rim_w, pot_y - pot_h // 2 - rim_h,
         cx + rim_w, pot_y - pot_h // 2 + rim_h],
        radius=int(size * 0.015),
        fill=(212, 168, 67),
    )

    # ===== Steam Wisps =====
    steam_color = (240, 232, 220, 170)
    steam_w = max(3, size // 85)
    start_y = pot_y - pot_h // 2 - rim_h - int(size * 0.02)

    for offset in [-0.14, 0, 0.14]:
        sx = cx + int(size * offset)
        end_y = start_y - int(size * 0.16)
        points = []
        segments = 10
        for t in range(segments + 1):
            tt = t / segments
            wave = int(size * 0.015 * (1 if t % 2 == 0 else -1))
            px = sx + wave
            py = start_y - int((start_y - end_y) * tt)
            points.append((px, py))
        if len(points) > 1:
            draw.line(points, fill=steam_color, width=steam_w)

    # ===== Magnifying Glass =====
    mg_r = int(size * 0.11)
    mg_cx = cx + int(size * 0.16)
    mg_cy = cy + int(size * 0.14)
    mg_line = max(2, size // 64)

    if mg_r > 4:
        # Glass circle
        draw.ellipse(
            [mg_cx - mg_r, mg_cy - mg_r, mg_cx + mg_r, mg_cy + mg_r],
            outline=(212, 168, 67),
            width=mg_line,
        )

        # Glass fill
        inner = [mg_cx - mg_r + mg_line, mg_cy - mg_r + mg_line,
                 mg_cx + mg_r - mg_line, mg_cy + mg_r - mg_line]
        if inner[2] > inner[0] and inner[3] > inner[1]:
            draw.ellipse(
                inner,
                fill=(255, 255, 255, 40),
            )

        # Handle
        handle_len = max(2, int(size * 0.11))
        hx = mg_cx + int(mg_r * 0.7)
        hy = mg_cy + int(mg_r * 0.7)
        draw.line(
            [(hx, hy), (hx + handle_len, hy + handle_len)],
            fill=(212, 168, 67),
            width=mg_line,
        )

        # Handle end dot
        dot_r = mg_line
        ex = hx + handle_len
        ey = hy + handle_len
        draw.ellipse([ex - dot_r, ey - dot_r, ex + dot_r, ey + dot_r], fill=(212, 168, 67))

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
        sizes=[(s, s) for s in sizes[:-1]],
        append_images=ico_images[1:-1],
    )
    print(f"Created: {ico_path}")

    # Generate PNGs
    for s in [64, 128, 256, 512]:
        png_path = os.path.join(ASSETS_DIR, f"icon_{s}.png")
        draw_icon(s).save(png_path, format="PNG")
        print(f"Created: {png_path}")

    # PWA icon
    pwa_dir = os.path.join(os.path.dirname(ASSETS_DIR), "static")
    os.makedirs(pwa_dir, exist_ok=True)
    draw_icon(512).save(os.path.join(pwa_dir, "icon-512.png"), format="PNG")
    draw_icon(192).save(os.path.join(pwa_dir, "icon-192.png"), format="PNG")
    print(f"Created: PWA icons (512px, 192px)")

    # Android launcher icons
    android_dir = os.path.join(
        os.path.dirname(ASSETS_DIR), "mobile", "android", "app", "src", "main", "res"
    )
    for name, size in [
        ("mipmap-mdpi", 48), ("mipmap-hdpi", 72), ("mipmap-xhdpi", 96),
        ("mipmap-xxhdpi", 144), ("mipmap-xxxhdpi", 192),
    ]:
        path = os.path.join(android_dir, name, "ic_launcher.png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        draw_icon(size).save(path, format="PNG")
        print(f"Created: {name} ({size}px)")

    # Splash screen
    splash_path = os.path.join(android_dir, "drawable", "splash.png")
    os.makedirs(os.path.dirname(splash_path), exist_ok=True)
    draw_icon(1024).save(splash_path, format="PNG")
    print(f"Created: splash screen")

    print("\nAll assets generated successfully!")


if __name__ == "__main__":
    generate_all_assets()
