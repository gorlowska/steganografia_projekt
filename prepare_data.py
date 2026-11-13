# data/raw/images -> data/covers (skala szarosci, rozne rozmiary, PNG)
# data/raw/texts  -> data/messages (30 plikow od 10 B do 200 kB)
import os
from PIL import Image

RAW_IMAGES, RAW_TEXTS = "data/raw/images", "data/raw/texts"
COVERS, MESSAGES = "data/covers", "data/messages"
SIZE_PLAN = [None, 256, 512, 384, None, 1024]   # dluzszy bok, tylko zmniejszanie
N_MESSAGES, MIN_SIZE, MAX_SIZE = 30, 10, 200_000


def to_grayscale(img):
    if img.mode in ("RGBA", "LA", "P", "PA"):
        img = img.convert("RGBA")
        img = Image.alpha_composite(Image.new("RGBA", img.size, "white"), img)
    return img.convert("L")


def resize(img, size):
    w, h = img.size
    if size is None or max(w, h) <= size:
        return img
    s = size / max(w, h)
    return img.resize((round(w * s), round(h * s)), Image.LANCZOS)


def prepare_covers():
    os.makedirs(COVERS, exist_ok=True)
    for i, name in enumerate(sorted(os.listdir(RAW_IMAGES))):
        img = resize(to_grayscale(Image.open(os.path.join(RAW_IMAGES, name))), SIZE_PLAN[i % len(SIZE_PLAN)])
        w, h = img.size
        img.save(os.path.join(COVERS, f"{i + 1:02d}_{os.path.splitext(name)[0]}_{w}x{h}.png"))
    print("obrazy:", len(os.listdir(COVERS)))


def prepare_messages():
    os.makedirs(MESSAGES, exist_ok=True)
    texts = []
    for name in sorted(os.listdir(RAW_TEXTS)):
        with open(os.path.join(RAW_TEXTS, name), encoding="utf-8") as f:
            texts.append((os.path.splitext(name)[0], f.read()))

    ratio = (MAX_SIZE / MIN_SIZE) ** (1 / (N_MESSAGES - 1))
    for i in range(N_MESSAGES):
        size = round(MIN_SIZE * ratio ** i)
        ok = [t for t in texts if len(t[1].encode("utf-8")) >= size * 1.15]
        name, text = ok[i % len(ok)]
        start = text.find(". ", len(text) // 10) + 2                 # pomijamy naglowek ksiazki
        content = text[start:].encode("utf-8")[:size].decode("utf-8", errors="ignore")
        n = len(content.encode("utf-8"))
        with open(os.path.join(MESSAGES, f"msg_{i + 1:02d}_{n:06d}B_{name}.txt"), "w", encoding="utf-8", newline="") as f:
            f.write(content)
    print("wiadomosci:", N_MESSAGES)


if __name__ == "__main__":
    prepare_covers()
    prepare_messages()
