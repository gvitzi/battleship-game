import base64
from pathlib import Path

root = Path(__file__).resolve().parent
html = (root / "index.html").read_text(encoding="utf-8")

files = [
    ("audio/welcome-screen.mp3", "audio/mpeg"),
    ("audio/game-soundtrack2.mp3", "audio/mpeg"),
    ("audio/01_water_splash.wav", "audio/wav"),
    ("audio/02_ship_hit_explosion.wav", "audio/wav"),
    ("audio/04_cannon_fire.wav", "audio/wav"),
    ("images/cover.png", "image/png"),
    ("images/carrier.png", "image/png"),
    ("images/battleship.png", "image/png"),
    ("images/cruiser.png", "image/png"),
    ("images/submarine.png", "image/png"),
    ("images/destroyer.png", "image/png"),
]

parts = []
for name, mime in files:
    if not (root / name).is_file():
        raise SystemExit("missing file " + name)
    data = base64.b64encode((root / name).read_bytes()).decode("ascii")
    parts.append('"' + name + '":"data:' + mime + ";base64," + data + '"')

marker = "    const letters = "
if marker not in html:
    raise SystemExit("missing letters marker")
html = html.replace(
    marker,
    "    const embeddedFiles = {" + ",".join(parts) + "};\n" + marker,
    1,
)

html = html.replace(' src="audio/welcome-screen.mp3"', "", 1)
html = html.replace(' src="images/cover.png"', "", 1)

old_music = '    const music = document.getElementById("music");\n'
new_music = old_music + '    music.src = embeddedFiles["audio/welcome-screen.mp3"];\n'
if html.count(old_music) != 1:
    raise SystemExit("music element count")
html = html.replace(old_music, new_music, 1)

html = html.replace(
    marker,
    '    document.querySelector(".welcome-ship").src = embeddedFiles["images/cover.png"];\n' + marker,
    1,
)

old_play = "    function playMusicFile(src) {\n"
new_play = old_play + "      src = embeddedFiles[src] || src;\n"
if html.count(old_play) != 1:
    raise SystemExit("playMusicFile count")
html = html.replace(old_play, new_play, 1)

for name, _mime in files:
    html = html.replace('new Audio("' + name + '")', 'new Audio(embeddedFiles["' + name + '"])')

old_picture = 'picture.src = "images/" + ship.id + ".png";'
if html.count(old_picture) != 2:
    raise SystemExit("picture src count " + str(html.count(old_picture)))
html = html.replace(old_picture, 'picture.src = embeddedFiles["images/" + ship.id + ".png"];')

for name, _mime in files:
    if html.count('"' + name + '"') < 1:
        raise SystemExit("key missing " + name)

out = root / "maya-battleship-game.html"
out.write_text(html, encoding="utf-8")
text = out.read_text(encoding="utf-8")
print("bytes", out.stat().st_size)
print("data-uris", text.count("data:"))
