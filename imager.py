from PIL import Image, ImageDraw

def create_icon(name, draw_fn):
    img = Image.new("RGBA", (64, 64), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw_fn(draw)
    img.save(f"img/icons/{name}.png")

# ▶ PLAY
create_icon("play", lambda d: d.polygon([(20,10),(50,32),(20,54)], fill="white"))

# ■ STOP
create_icon("stop", lambda d: d.rectangle([16,16,48,48], fill="white"))

# ↻ CENTER (circle + arrow)
def center_icon(d):
    d.arc([10,10,54,54], 0, 300, fill="white", width=4)
    d.polygon([(40,10),(54,10),(50,22)], fill="white")
create_icon("center", center_icon)

# LOAD
create_icon("load", lambda d: d.rectangle([10,20,54,50], outline="white", width=3))

# SAVE
create_icon("save", lambda d: d.rectangle([14,14,50,50], outline="white", width=3))

# LANGUAGE (globe)
def globe(d):
    d.ellipse([10,10,54,54], outline="white", width=3)
    d.line([32,10,32,54], fill="white", width=2)
create_icon("language", globe)

# EXIT (X)
create_icon("exit", lambda d: (
    d.line([15,15,50,50], fill="white", width=4),
    d.line([50,15,15,50], fill="white", width=4)
))