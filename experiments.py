# Eksp. 1: pelne wypelnienie losowymi danymi (jak tab. 2 w artykule), LSB vs OPAP
# Eksp. 2: kazdy obraz x kazda wiadomosc x k = 1..4
import os
import csv
import numpy as np
from utils import load_image, save_image, read_file, message_to_bits, psnr, mse, HEADER_BITS
import chan_cheng as alg

COVERS, MESSAGES, RESULTS = "data/covers", "data/messages", "results"
K_VALUES = [1, 2, 3, 4]

def files(folder):
    return [os.path.join(folder, f) for f in sorted(os.listdir(folder))]

def save_csv(rows, name):
    with open(os.path.join(RESULTS, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

def experiment_full(covers):
    rng = np.random.default_rng(0)
    rows = []
    for path in covers:
        cover = load_image(path)
        for k in K_VALUES:
            data = rng.integers(0, 256, (alg.capacity_bits(cover, k) - HEADER_BITS) // 8, dtype=np.uint8).tobytes()
            row = {"cover": os.path.basename(path), "k": k}
            for opap in (False, True):
                stego, stats = alg.embed(cover, message_to_bits(data), k, opap)
                name = "opap" if opap else "lsb"
                row["psnr_" + name] = round(psnr(cover, stego), 4)
                row["ok_" + name] = alg.extract(stego, k) == data
            for c, n in stats["cases"].items():
                row[f"case{c}_%"] = round(100 * n / stats["used_pixels"], 2)
            rows.append(row)
    save_csv(rows, "full_capacity.csv")

    print("Srednie PSNR [dB], pelne wypelnienie:")
    for k in K_VALUES:
        r = [x for x in rows if x["k"] == k]
        print(f"  k={k}  LSB {np.mean([x['psnr_lsb'] for x in r]):.2f}  OPAP {np.mean([x['psnr_opap'] for x in r]):.2f}")

def experiment_messages(covers, messages):
    rows = []
    for cpath in covers:
        cover = load_image(cpath)
        for mpath in messages:
            data = read_file(mpath)
            bits = message_to_bits(data)
            for k in K_VALUES:
                row = {"cover": os.path.basename(cpath), "message": os.path.basename(mpath),
                       "bytes": len(data), "k": k, "fits": len(bits) <= alg.capacity_bits(cover, k)}
                if row["fits"]:
                    stego, _ = alg.embed(cover, bits, k)
                    row.update(ok=alg.extract(stego, k) == data, psnr=round(psnr(cover, stego), 4),
                               mse=round(mse(cover, stego), 6), changed=int((cover != stego).sum()))
                else:
                    row.update(ok="", psnr="", mse="", changed="")
                rows.append(row)
    save_csv(rows, "messages.csv")

    fits = [r for r in rows if r["fits"]]
    print(f"Wiadomosci: zmiescilo sie {len(fits)}/{len(rows)}, poprawny odczyt {sum(r['ok'] for r in fits)}/{len(fits)}")

def save_examples(covers, messages):
    os.makedirs(os.path.join(RESULTS, "examples"), exist_ok=True)
    cover = load_image(covers[5])
    data = read_file(messages[20])
    save_image(cover, os.path.join(RESULTS, "examples", "cover.png"))
    for k in K_VALUES:
        stego, _ = alg.embed(cover, message_to_bits(data), k)
        save_image(stego, os.path.join(RESULTS, "examples", f"stego_k{k}.png"))

if __name__ == "__main__":
    os.makedirs(RESULTS, exist_ok=True)
    covers, messages = files(COVERS), files(MESSAGES)
    experiment_full(covers)
    experiment_messages(covers, messages)
    save_examples(covers, messages)
