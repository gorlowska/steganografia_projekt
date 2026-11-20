# Mielikainen (2006) - LSB Matching Revisited
# para pikseli (x1, x2) niesie 2 bity: m1 = LSB(y1), m2 = f(y1, y2)
# dla porownania (jak w artykule) zwykle LSB matching: revisited=False
import numpy as np
from utils import bits_to_int, bits_to_bytes, pixel_order, HEADER_BITS

NAME = "Mielikainen 2006 (LSB Matching Revisited)"


def f(a, b):
    return (a // 2 + b) % 2


def usable_pairs(pixels, order):
    # kolejne piksele w kolejnosci order tworza pary; pomijamy pary z pikselem 0 lub 255
    pairs = order[:len(order) // 2 * 2].reshape(-1, 2)
    v = pixels[pairs]
    return pairs[((v > 0) & (v < 255)).all(axis=1)]


def capacity_bits(cover, key=None, revisited=True, **_):
    if not revisited:
        return cover.size
    pixels = cover.flatten()
    return 2 * len(usable_pairs(pixels, pixel_order(pixels.size, key)))


def embed(cover, bits, key=None, revisited=True, **_):
    if len(bits) > capacity_bits(cover, key, revisited):
        raise ValueError(f"Wiadomosc za dluga ({len(bits)} b, pojemnosc {capacity_bits(cover, key, revisited)} b)")
    if not revisited:
        return embed_lsbm(cover, bits, key)

    pixels = cover.flatten().astype(np.int32)
    pairs = usable_pairs(pixels, pixel_order(pixels.size, key)).tolist()
    bits = np.concatenate([bits, np.zeros(len(bits) % 2, dtype=np.uint8)]).tolist()
    p = pixels.tolist()
    rng = np.random.default_rng(key)
    diff_sum = [0, 0]   # suma zmian osobno dla parzystych i nieparzystych pikseli

    def plus_minus(x):
        # +1 albo -1: tak, zeby suma zmian w obszarze (parzyste / nieparzyste) byla blisko 0
        if x == 1:
            d = 1
        elif x == 254:
            d = -1
        elif diff_sum[x % 2] != 0:
            d = -1 if diff_sum[x % 2] > 0 else 1
        else:
            d = int(rng.choice([-1, 1]))
        diff_sum[x % 2] += d
        return x + d

    for i in range(len(bits) // 2):
        a, b = pairs[i]
        x1, x2 = p[a], p[b]
        m1, m2 = bits[2 * i], bits[2 * i + 1]

        if m1 == x1 % 2:                                   # Fig. 1 - lewa galaz
            y1 = x1
            y2 = x2 if m2 == f(x1, x2) else plus_minus(x2)
        else:                                              # Fig. 1 - prawa galaz
            y1 = x1 - 1 if m2 == f(x1 - 1, x2) else x1 + 1
            y2 = x2
            if y1 == 0 or y1 == 255:     # poza zakresem: zmiana w druga strone + korekta x2
                y1 = 2 * x1 - y1
                y2 = plus_minus(x2)
            diff_sum[x1 % 2] += y1 - x1

        p[a], p[b] = y1, y2

    stego = np.array(p, dtype=np.uint8).reshape(cover.shape)
    return stego, {"used_pixels": len(bits)}


def embed_lsbm(cover, bits, key=None):
    # zwykle LSB matching: gdy bit sie nie zgadza, losowo +1 albo -1
    pixels = cover.flatten().astype(np.int32)
    idx = pixel_order(pixels.size, key)[:len(bits)]
    p = pixels[idx]
    d = np.random.default_rng(key).choice([-1, 1], size=len(p))
    d[p == 0] = 1
    d[p == 255] = -1
    wrong = p % 2 != bits
    p[wrong] += d[wrong]
    pixels[idx] = p
    return pixels.reshape(cover.shape).astype(np.uint8), {"used_pixels": len(bits)}


def extract(stego, key=None, revisited=True, **_):
    pixels = stego.flatten().astype(np.int32)
    order = pixel_order(pixels.size, key)

    if revisited:
        v = pixels[usable_pairs(pixels, order)]
        bits = np.stack([v[:, 0] % 2, f(v[:, 0], v[:, 1])], axis=1).flatten()
    else:
        bits = pixels[order] % 2

    length = bits_to_int(bits[:HEADER_BITS])
    total = HEADER_BITS + 8 * length
    if total > len(bits):
        raise ValueError("Bledny naglowek (zly klucz albo brak wiadomosci)")
    return bits_to_bytes(bits[HEADER_BITS:total])
