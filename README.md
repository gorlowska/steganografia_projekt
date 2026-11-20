# Steganografia w obrazach

`pip install -r requirements.txt`

- `utils.py` – wspólne funkcje (obrazy, wiadomość ↔ bity, kolejność pikseli, PSNR)
- `chan_cheng.py` – Chan & Cheng 2004, LSB + OPAP
- `mielikainen.py` – Mielikäinen 2006, LSB Matching Revisited (+ zwykłe LSB matching do porównania)
- `download_data.py` – pobranie danych do `data/raw/` (już pobrane)
- `prepare_data.py` – preprocessing → `data/covers/` (32 obrazy), `data/messages/` (30 tekstów)
- `experiments.py` – wszystkie metody na wszystkich danych, wyniki w `results/` (ok. 1 min)
- `main.py` – ukrycie / odczyt pojedynczego pliku

```
python main.py embed --alg chan_cheng --cover data/covers/05_cameraman_512x512.png --message data/messages/msg_17_002360B_pl_proza.txt --out stego.png --k 2
python main.py extract --alg chan_cheng --stego stego.png --out odczyt.txt --k 2
python main.py embed --alg mielikainen --cover data/covers/05_cameraman_512x512.png --message data/messages/msg_17_002360B_pl_proza.txt --out stego.png
python main.py extract --alg mielikainen --stego stego.png --out odczyt.txt
```
Opcje: `--key 1234` (kolejność pikseli z klucza), `--no-opap` (zwykłe LSB), `--lsbm` (zwykłe LSB matching).

## Dane

Obrazy (32): standardowe obrazy testowe (Baboon, Peppers, Boat, Jetplane, Lake…,
https://github.com/mohammadimtiazz/standard-test-images-for-Image-Processing) oraz obrazy ze `skimage.data`.
Wejście: PNG/TIFF/JPG, kolor i szarość; po preprocessingu skala szarości, od 256×147 do 1411×1411.

Wiadomości (30, od 10 B do 200 kB): fragmenty książek z Project Gutenberg, polskiego korpusu
pl196x (proza, prasa, publicystyka, dramat, popularnonaukowe) i Deklaracji Praw Człowieka (NLTK Data).

Obraz stego zapisywany tylko jako PNG. Maks. rozmiar wiadomości: Chan & Cheng (szer. × wys. × k − 32) / 8 B, Mielikäinen ok. (szer. × wys. − 32) / 8 B
(pary z pikselem 0 lub 255 są pomijane).
