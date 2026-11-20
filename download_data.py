# Pobiera surowe dane do data/raw/ (w paczce sa juz pobrane).
# Obrazy: standardowe obrazy testowe (GitHub) + skimage.data
# Teksty: NLTK Data - Project Gutenberg, polski korpus pl196x, Deklaracja Praw Czlowieka (PL)
import io
import os
import re
import zipfile
import urllib.request
from PIL import Image

IMG_URL = "https://raw.githubusercontent.com/mohammadimtiazz/standard-test-images-for-Image-Processing/master/standard_test_images/"
NLTK_URL = "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/"

STANDARD = {"baboon.png": "baboon.png", "boat.png": "boat.png",
            "cameraman.tif": "cameraman.tif", "fruits.png": "fruits.png", "house.tif": "house.png",
            "jetplane.tif": "jetplane.png", "lake.tif": "lake.png", "livingroom.tif": "livingroom.tif",
            "peppers.png": "peppers.png", "pirate.tif": "pirate.tif", "tulips.png": "tulips.png",
            "walkbridge.tif": "walkbridge.png", "woman_blonde.tif": "woman_blonde.tif",
            "woman_darkhair.tif": "woman_darkhair.tif", "HappyFish.jpg": "happyfish.jpg"}
SKIMAGE = ["astronaut", "brick", "grass", "gravel", "moon", "coffee", "chelsea", "coins", "clock",
           "rocket", "page", "immunohistochemistry", "hubble_deep_field", "text", "retina", "colorwheel",
           "stereo_motorcycle"]
GUTENBERG = ["austen-emma", "austen-persuasion", "blake-poems", "bryant-stories", "burgess-busterbrown",
             "carroll-alice", "chesterton-thursday", "melville-moby_dick", "milton-paradise",
             "shakespeare-hamlet", "shakespeare-macbeth", "whitman-leaves"]
PL196X = {"a-publi": "pl_publicystyka", "b-prasa": "pl_prasa", "c-popul": "pl_popularnonaukowe",
          "d-proza": "pl_proza", "e-dramat": "pl_dramat"}
MAX_BYTES = 300_000


def get(url):
    print(url)
    return urllib.request.urlopen(url, timeout=120).read()


def save_text(name, text):
    text = text.encode("utf-8")[:MAX_BYTES].decode("utf-8", errors="ignore")
    with open(f"data/raw/texts/{name}.txt", "w", encoding="utf-8") as f:
        f.write(text)


def tei_to_text(xml):
    # pl196x: slowa w <w>, interpunkcja w <c>, zdania w <s>
    out = []
    for s in re.findall(r"<s>(.*?)</s>", xml, flags=re.S):
        sent = ""
        for kind, tok in re.findall(r"<([wc])[^>]*>([^<]*)</\1>", s):
            sent += tok if kind == "c" or not sent else " " + tok
        out.append(sent)
    return " ".join(out)


if __name__ == "__main__":
    os.makedirs("data/raw/images", exist_ok=True)
    os.makedirs("data/raw/texts", exist_ok=True)

    for src, dst in STANDARD.items():
        raw = get(IMG_URL + src)
        try:
            Image.open(io.BytesIO(raw)).load()
            open(f"data/raw/images/{dst}", "wb").write(raw)
        except Exception:                       # czesci TIFF-ow Pillow nie czyta
            import tifffile
            a = tifffile.imread(io.BytesIO(raw))
            if a.ndim == 3:
                a = a[:, :, 0]
            Image.fromarray(a).save(f"data/raw/images/{dst}")

    import skimage.data
    for name in SKIMAGE:
        a = getattr(skimage.data, name)()
        if isinstance(a, tuple):                # stereo_motorcycle zwraca pare obrazow
            a = a[0]
        Image.fromarray(a).save(f"data/raw/images/{name}.png")

    z = zipfile.ZipFile(io.BytesIO(get(NLTK_URL + "gutenberg.zip")))
    for book in GUTENBERG:
        save_text("en_" + book, z.read(f"gutenberg/{book}.txt").decode("latin-1"))

    z = zipfile.ZipFile(io.BytesIO(get(NLTK_URL + "pl196x.zip")))
    for src, dst in PL196X.items():
        save_text(dst, tei_to_text(z.read(f"pl196x/{src}.xml").decode("utf-8")))

    z = zipfile.ZipFile(io.BytesIO(get(NLTK_URL + "udhr2.zip")))
    save_text("pl_deklaracja_praw_czlowieka", z.read("udhr2/pol.txt").decode("utf-8"))
