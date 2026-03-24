import os
import cairosvg
from PIL import Image

# ================= CONFIG =================
SVG_FOLDER = "img/svg"
PNG_FOLDER = "img/icons"

SIZE = 64  # Basisgröße (wird später runter skaliert im UI)

# Farbvarianten (für verschiedene Buttons)
COLOR_VARIANTS = {
    "white": (255, 255, 255),
    "green": (46, 125, 50),
    "red": (198, 40, 40),
    "blue": (21, 101, 192),
    "orange": (249, 168, 37),
}

# ================= HELPERS =================
def recolor_image(img, color):
    """Ersetzt alle nicht-transparenten Pixel mit neuer Farbe"""
    img = img.convert("RGBA")
    data = img.getdata()

    new_data = []
    for item in data:
        # wenn Pixel sichtbar ist
        if item[3] > 0:
            new_data.append((*color, item[3]))
        else:
            new_data.append(item)

    img.putdata(new_data)
    return img


def convert_svg_to_png(svg_path, png_path):
    cairosvg.svg2png(
        url=svg_path,
        write_to=png_path,
        output_width=SIZE,
        output_height=SIZE
    )


# ================= MAIN =================
def run_pipeline():
    os.makedirs(PNG_FOLDER, exist_ok=True)

    for file in os.listdir(SVG_FOLDER):
        if not file.endswith(".svg"):
            continue

        name = file.replace(".svg", "")
        svg_path = os.path.join(SVG_FOLDER, file)

        print(f"🔄 {file}")

        # 1. Standard PNG erzeugen
        base_png = os.path.join(PNG_FOLDER, f"{name}.png")
        convert_svg_to_png(svg_path, base_png)

        # 2. Farbvarianten erzeugen
        base_img = Image.open(base_png)

        for variant, color in COLOR_VARIANTS.items():
            colored = recolor_image(base_img, color)

            out_path = os.path.join(PNG_FOLDER, f"{name}_{variant}.png")
            colored.save(out_path)

    print("\n✅ Alle Icons generiert!")


if __name__ == "__main__":
    run_pipeline()