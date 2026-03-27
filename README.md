# Photoshop Aftermarket

## Cerinte sistem
- Python 3.13+
- Librarii necesare:
  - `Pillow` (PIL)
  - `matplotlib`
  - `numpy`

## Instalare
```bash
pip install Pillow matplotlib numpy
```

## Rulare
```bash
python main.py
```

## Functionalitati
- **Conversii spatiu de culoare:** Gri (3 metode), CMYK, YUV, YCbCr, HSV
- **Efecte:** Inversare imagine + vizualizare canale R, G, B individual; Binarizare
- **Analiza:**
  - Histograma intensitatii de gri
  - Momente de ordin 1 si 2 (centru de masa, orientare, matrice de covarianta)
  - Proiectii orizontala si verticala
- Suport formate BMP: 4bpp, 8bpp, 16bpp, 24bpp, 32bpp

## Structura proiect
- `main.py` - Fereastra principala, meniuri, afisare UI
- `image_io.py` - Citirea fisierelor BMP
- `conversions.py` - Conversii spatiu de culoare
- `effects.py` - Efecte (inversare, binarizare, canale RGB)
- `analysis.py` - Calcule histograma, momente, proiectii