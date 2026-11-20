# Chan, Cheng (2004) - Hiding data in images by simple LSB substitution
# k-bitowe LSB + OPAP
import numpy as np
from utils import bits_to_int, bits_to_bytes, pixel_order, HEADER_BITS

NAME = "Chan & Cheng 2004 (LSB + OPAP)"


def capacity_bits(cover, k=2, **_):
    return cover.size * k


def embed(cover, bits, k=2, use_opap=True, key=None, **_):
    if len(bits) > capacity_bits(cover, k):
        raise ValueError(f"Wiadomosc za dluga ({len(bits)} b, pojemnosc {capacity_bits(cover, k)} b)")

    pixels = cover.flatten().astype(np.int32)
    bits = np.concatenate([bits, np.zeros(-len(bits) % k, dtype=np.uint8)])
    m = bits.reshape(-1, k) @ (2 ** np.arange(k - 1, -1, -1))   # k bitow -> liczba

    idx = pixel_order(pixels.size, key)[:len(m)]
    p = pixels[idx]
    p1 = p - p % 2**k + m                                         # wzor (4)

    cases = {}
    if use_opap:
        d = p1 - p
        high = d > 2**(k - 1)
        low = d < -2**(k - 1)
        c1 = high & (p1 >= 2**k)
        c4 = low & (p1 < 256 - 2**k)
        cases = {1: c1.sum(), 2: (high & ~c1).sum(), 3: (~high & ~low).sum(),
                 4: c4.sum(), 5: (low & ~c4).sum()}
        p1[c1] -= 2**k
        p1[c4] += 2**k

    pixels[idx] = p1
    return pixels.reshape(cover.shape).astype(np.uint8), {"used_pixels": len(m), "cases": cases}


def read_bits(pixels, order, k, n_bits):
    n_px = -(-n_bits // k)
    m = pixels[order[:n_px]] % 2**k                               # wzor (5)
    bits = (m[:, None] >> np.arange(k - 1, -1, -1)) & 1
    return bits.flatten()[:n_bits].astype(np.uint8)


def extract(stego, k=2, key=None, **_):
    pixels = stego.flatten().astype(np.int32)
    order = pixel_order(pixels.size, key)

    length = bits_to_int(read_bits(pixels, order, k, HEADER_BITS))
    total = HEADER_BITS + 8 * length
    if total > pixels.size * k:
        raise ValueError("Bledny naglowek (zle k, klucz albo brak wiadomosci)")

    return bits_to_bytes(read_bits(pixels, order, k, total)[HEADER_BITS:])
