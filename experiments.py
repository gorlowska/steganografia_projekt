# Eksp. 1: pelne wypelnienie losowymi danymi - PSNR, zmiany na piksel, asymetria (jak w artykulach)
# Eksp. 2: kazdy obraz x kazda wiadomosc x kazda metoda - poprawnosc odczytu, PSNR
import os
import csv
import numpy as np
from utils import load_image, save_image, read_file, message_to_bits, psnr, mse, HEADER_BITS
import chan_cheng
import mielikainen

COVERS, MESSAGES, RESULTS = "data/covers", "data/messages", "results"

# (nazwa, modul, parametry)
METHODS = [(f"LSB k={k}", chan_cheng, {"k": k, "use_opap": False}) for k in (1, 2, 3, 4)] \
        + [(f"OPAP k={k}", chan_cheng, {"k": k, "use_opap": True}) for k in (1, 2, 3, 4)] \
        + [("LSBM", mielikainen, {"revisited": False}),
           ("LSBMR", mielikainen, {"revisited": True})]


def files(folder):
    return [os.path.join(folder, f) for f in sorted(os.listdir(folder))]


def save_csv(rows, name):
    with open(os.path.join(RESULTS, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def bias(cover, stego, parity):
    # |srednia zmiana| w obszarze pikseli parzystych / nieparzystych (asymetria LSB replacement)
    mask = cover % 2 == parity
    if not mask.any():
        return float("nan")
    return abs(float(np.mean(stego[mask].astype(int) - cover[mask])))


def experiment_full(covers):
    rng = np.random.default_rng(0)
    rows = []
    for path in covers:
        cover = load_image(path)
        for name, alg, params in METHODS:
            data = rng.integers(0, 256, (alg.capacity_bits(cover, **params) - HEADER_BITS) // 8, dtype=np.uint8).tobytes()
            stego, stats = alg.embed(cover, message_to_bits(data), **params)
            row = {"method": name, "cover": os.path.basename(path),
                   "ok": alg.extract(stego, **params) == data,
                   "psnr": round(psnr(cover, stego), 4),
                   "bpp": round(8 * len(data) / cover.size, 4),
                   "changes_per_pixel": round(int((cover != stego).sum()) / stats["used_pixels"], 4),
                   "bias_even": round(bias(cover, stego, 0), 4),
                   "bias_odd": round(bias(cover, stego, 1), 4)}
            rows.append(row)
    save_csv(rows, "full_capacity.csv")

    print("Pelne wypelnienie, srednie po obrazach:")
    print(f"  {'metoda':10s} {'bpp':>5s} {'PSNR':>6s} {'zmiany/px':>9s} {'asym.':>6s}  odczyt")
    for name, _, _ in METHODS:
        r = [x for x in rows if x["method"] == name]
        print(f"  {name:10s} {np.mean([x['bpp'] for x in r]):5.2f} {np.mean([x['psnr'] for x in r]):6.2f}"
              f" {np.mean([x['changes_per_pixel'] for x in r]):9.3f}"
              f" {np.nanmean([x['bias_even'] for x in r] + [x['bias_odd'] for x in r]):6.3f}"
              f"  {sum(x['ok'] for x in r)}/{len(r)}")


def experiment_messages(covers, messages):
    rows = []
    for cpath in covers:
        cover = load_image(cpath)
        for mpath in messages:
            data = read_file(mpath)
            bits = message_to_bits(data)
            for name, alg, params in METHODS:
                row = {"method": name, "cover": os.path.basename(cpath), "message": os.path.basename(mpath),
                       "bytes": len(data), "fits": len(bits) <= alg.capacity_bits(cover, **params)}
                if row["fits"]:
                    stego, _ = alg.embed(cover, bits, **params)
                    row.update(ok=alg.extract(stego, **params) == data, psnr=round(psnr(cover, stego), 4),
                               mse=round(mse(cover, stego), 6), changed=int((cover != stego).sum()))
                else:
                    row.update(ok="", psnr="", mse="", changed="")
                rows.append(row)
    save_csv(rows, "messages.csv")

    print("Wiadomosci (zmiescilo sie / poprawny odczyt):")
    for name, _, _ in METHODS:
        fits = [r for r in rows if r["method"] == name and r["fits"]]
        print(f"  {name:10s} {len(fits):4d}/{len(covers) * len(messages)}  {sum(r['ok'] for r in fits)}/{len(fits)}")


def save_examples(covers, messages):
    os.makedirs(os.path.join(RESULTS, "examples"), exist_ok=True)
    cover = load_image(covers[5])
    data = read_file(messages[20])
    save_image(cover, os.path.join(RESULTS, "examples", "cover.png"))
    for name, alg, params in METHODS:
        stego, _ = alg.embed(cover, message_to_bits(data), **params)
        save_image(stego, os.path.join(RESULTS, "examples", name.replace(" ", "_").replace("=", "") + ".png"))


if __name__ == "__main__":
    os.makedirs(RESULTS, exist_ok=True)
    covers, messages = files(COVERS), files(MESSAGES)
    experiment_full(covers)
    experiment_messages(covers, messages)
    save_examples(covers, messages)
