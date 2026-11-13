import numpy as np
from PIL import Image

HEADER_BITS = 32  # dlugosc wiadomosci w bajtach


# --- obrazy ---
def load_image(path):
    return np.array(Image.open(path).convert("L"), dtype=np.uint8)


def save_image(image, path):
    # tylko PNG - JPEG zniszczylby ukryte bity
    Image.fromarray(image.astype(np.uint8), mode="L").save(path, format="PNG")


# --- bity ---
def int_to_bits(value, n):
    return ((value >> np.arange(n - 1, -1, -1)) & 1).astype(np.uint8)


def bits_to_int(bits):
    return int(np.dot(bits, 2 ** np.arange(len(bits) - 1, -1, -1)))


def message_to_bits(data):
    body = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
    return np.concatenate([int_to_bits(len(data), HEADER_BITS), body])


def bits_to_bytes(bits):
    return np.packbits(np.asarray(bits, dtype=np.uint8)).tobytes()


def pixel_order(n, key=None):
    if key is None:
        return np.arange(n)
    return np.random.default_rng(key).permutation(n)


# --- pliki ---
def read_file(path):
    with open(path, "rb") as f:
        return f.read()


def write_file(path, data):
    with open(path, "wb") as f:
        f.write(data)


# --- jakosc ---
def mse(cover, stego):
    return float(np.mean((cover.astype(float) - stego.astype(float)) ** 2))


def psnr(cover, stego):
    e = mse(cover, stego)
    return float("inf") if e == 0 else float(10 * np.log10(255 ** 2 / e))
