import json
from datetime import datetime


# zamieniamy strukturę drzewa na "w miare" czytelny tekst z wcięciami
def drzewo_na_tekst(drzewo, poziom=0):
    spacja = "  " * poziom

    if drzewo["lisc"]:
        return spacja + "LIŚĆ: " + drzewo["decyzja"] + "\n"

    tekst = spacja + "WĘZEŁ: " + drzewo["atrybut"] + "\n"

    for wartosc, poddrzewo in drzewo["galęzie"].items():
        tekst = tekst + spacja + "  [" + wartosc + "]:\n"
        tekst = tekst + drzewo_na_tekst(poddrzewo, poziom + 2)

    return tekst


# zapisujemy pełny raport tekstowy oraz format json do pliku wyjściowego
def zapisz(sciezka, parametry, drzewo, wyniki):
    plik = open(sciezka, 'w', encoding='utf-8')

    teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plik.write("RAPORT - DRZEWO DECYZYJNE\n")
    plik.write("Data: " + teraz + "\n\n")

    plik.write("PARAMETRY:\n")
    for nazwa, wartosc in parametry.items():
        plik.write("  " + nazwa + ": " + str(wartosc) + "\n")

    plik.write("\nWYNIKI:\n")
    dokladnosc_procent = round(wyniki["dokladnosc"] * 100, 1)
    plik.write("  Dokładność: " + str(dokladnosc_procent) + "%\n")
    plik.write("  Poprawne: " + str(wyniki["poprawne"]) + "/" + str(wyniki["wszystkich"]) + "\n")
    plik.write("  Węzły: " + str(wyniki["wezly"]) + "\n")
    plik.write("  Liście: " + str(wyniki["liscie"]) + "\n")
    plik.write("  Wysokość: " + str(wyniki["wysokosc"]) + "\n")

    plik.write("\nSTRUKTURA DRZEWA:\n")
    plik.write(drzewo_na_tekst(drzewo))

    plik.write("\nJSON:\n")
    plik.write(json.dumps(drzewo, indent=2, ensure_ascii=False))

    plik.close()