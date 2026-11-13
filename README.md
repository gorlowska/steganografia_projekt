# Steganografia w obrazach

`pip install -r requirements.txt`

- `utils.py` – wspólne funkcje (obrazy, wiadomość ↔ bity, kolejność pikseli, PSNR)
- `chan_cheng.py` – Chan & Cheng 2004, LSB + OPAP (kolejne algorytmy: osobne pliki)
- `download_data.py` – pobranie danych do `data/raw/` (już pobrane)
- `prepare_data.py` – preprocessing → `data/covers/` (32 obrazy), `data/messages/` (30 tekstów)
- `experiments.py` – wyniki w `results/`
- `main.py` – ukrycie / odczyt pojedynczego pliku

```
python main.py embed --cover data/covers/06_cameraman_512x512.png --message data/messages/msg_17_002360B_pl_proza.txt --out stego.png --k 2
python main.py extract --stego stego.png --out odczyt.txt --k 2
```

## Dane

Obrazy (32): standardowe obrazy testowe (Baboon, Peppers, Boat, Barbara, Jetplane, Lake…,
https://github.com/mohammadimtiazz/standard-test-images-for-Image-Processing) oraz obrazy ze `skimage.data`.
Wejście: PNG/BMP/TIFF/JPG, kolor i szarość; po preprocessingu skala szarości, od 256×192 do 1000×872.

Wiadomości (30, od 10 B do 200 kB): fragmenty książek z Project Gutenberg, polskiego korpusu
pl196x (proza, prasa, publicystyka, dramat, popularnonaukowe) i Deklaracji Praw Człowieka (NLTK Data).

Obraz stego zapisywany tylko jako PNG. Maks. rozmiar wiadomości: (szer. × wys. × k − 32) / 8 bajtów.
