# python main.py embed --alg chan_cheng --cover obraz.png --message tekst.txt --out stego.png --k 2
# python main.py extract --alg chan_cheng --stego stego.png --out odczyt.txt --k 2
# --alg mielikainen (--lsbm = zwykle LSB matching), --key 1234 = kolejnosc pikseli z klucza
import argparse
from utils import load_image, save_image, read_file, write_file, message_to_bits, psnr
import chan_cheng
import mielikainen

ALGORITHMS = {"chan_cheng": chan_cheng, "mielikainen": mielikainen}

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["embed", "extract"])
parser.add_argument("--alg", choices=ALGORITHMS, default="chan_cheng")
parser.add_argument("--cover")
parser.add_argument("--stego")
parser.add_argument("--message")
parser.add_argument("--out", required=True)
parser.add_argument("--key", type=int)
parser.add_argument("--k", type=int, default=2)
parser.add_argument("--no-opap", action="store_true")
parser.add_argument("--lsbm", action="store_true")
args = parser.parse_args()

alg = ALGORITHMS[args.alg]
params = {"key": args.key, "k": args.k, "use_opap": not args.no_opap, "revisited": not args.lsbm}

if args.mode == "embed":
    cover = load_image(args.cover)
    data = read_file(args.message)
    stego, _ = alg.embed(cover, message_to_bits(data), **params)
    save_image(stego, args.out)
    print(f"ukryto {len(data)} B, zmienione piksele: {int((cover != stego).sum())}, PSNR = {psnr(cover, stego):.2f} dB")
else:
    data = alg.extract(load_image(args.stego), **params)
    write_file(args.out, data)
    print(f"odczytano {len(data)} B")
