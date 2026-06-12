import csv
import os

# domyslny zbior danych
DOMYSLNE_DANE = [
    {"Pogoda": "slonecznie", "Temperatura": "goraco",   "Wiatr": "nie", "Wilgotnosc": "wysoka",  "Aktywnosc": "nie"},
    {"Pogoda": "slonecznie", "Temperatura": "goraco",   "Wiatr": "tak", "Wilgotnosc": "wysoka",  "Aktywnosc": "nie"},
    {"Pogoda": "pochmurno",  "Temperatura": "goraco",   "Wiatr": "nie", "Wilgotnosc": "wysoka",  "Aktywnosc": "tak"},
    {"Pogoda": "deszcz",     "Temperatura": "lagodnie", "Wiatr": "nie", "Wilgotnosc": "wysoka",  "Aktywnosc": "tak"},
    {"Pogoda": "deszcz",     "Temperatura": "chlodno",  "Wiatr": "nie", "Wilgotnosc": "normalna","Aktywnosc": "tak"},
    {"Pogoda": "deszcz",     "Temperatura": "chlodno",  "Wiatr": "tak", "Wilgotnosc": "normalna","Aktywnosc": "nie"},
    {"Pogoda": "pochmurno",  "Temperatura": "chlodno",  "Wiatr": "tak", "Wilgotnosc": "normalna","Aktywnosc": "tak"},
    {"Pogoda": "slonecznie", "Temperatura": "lagodnie", "Wiatr": "nie", "Wilgotnosc": "normalna","Aktywnosc": "tak"},
    {"Pogoda": "slonecznie", "Temperatura": "chlodno",  "Wiatr": "nie", "Wilgotnosc": "normalna","Aktywnosc": "tak"},
    {"Pogoda": "deszcz",     "Temperatura": "lagodnie", "Wiatr": "nie", "Wilgotnosc": "normalna","Aktywnosc": "tak"},
    {"Pogoda": "slonecznie", "Temperatura": "lagodnie", "Wiatr": "tak", "Wilgotnosc": "wysoka",  "Aktywnosc": "tak"},
    {"Pogoda": "pochmurno",  "Temperatura": "lagodnie", "Wiatr": "tak", "Wilgotnosc": "wysoka",  "Aktywnosc": "tak"},
    {"Pogoda": "pochmurno",  "Temperatura": "goraco",   "Wiatr": "nie", "Wilgotnosc": "normalna","Aktywnosc": "tak"},
    {"Pogoda": "deszcz",     "Temperatura": "lagodnie", "Wiatr": "tak", "Wilgotnosc": "wysoka",  "Aktywnosc": "nie"},
    {"Pogoda": "slonecznie", "Temperatura": "goraco",   "Wiatr": "nie", "Wilgotnosc": "normalna","Aktywnosc": "tak"},
    {"Pogoda": "deszcz",     "Temperatura": "chlodno",  "Wiatr": "nie", "Wilgotnosc": "wysoka",  "Aktywnosc": "nie"},
    {"Pogoda": "pochmurno",  "Temperatura": "chlodno",  "Wiatr": "nie", "Wilgotnosc": "normalna","Aktywnosc": "tak"},
    {"Pogoda": "slonecznie", "Temperatura": "lagodnie", "Wiatr": "tak", "Wilgotnosc": "normalna","Aktywnosc": "tak"},
    {"Pogoda": "pochmurno",  "Temperatura": "lagodnie", "Wiatr": "nie", "Wilgotnosc": "wysoka",  "Aktywnosc": "tak"},
    {"Pogoda": "deszcz",     "Temperatura": "goraco",   "Wiatr": "nie", "Wilgotnosc": "normalna","Aktywnosc": "tak"},
]
DOMYSLNA_DECYZJA = "Aktywnosc"


# wczytywanie dancyh z pliku csv
def wczytaj_csv(sciezka):
    # sprawdzamy czy plik istnieje
    if not os.path.exists(sciezka):
        raise FileNotFoundError("Nie ma pliku: " + sciezka)

    # wczytujemy wszystkie wiersze z pliku CSV
    dane = []
    plik = open(sciezka, newline='', encoding='utf-8')
    reader = csv.DictReader(plik)
    kolumny = []
    for nazwa in reader.fieldnames:
        kolumny.append(nazwa.strip())
    for wiersz in reader:
        nowy_wiersz = {}
        for klucz, wartosc in wiersz.items():
            nowy_wiersz[klucz.strip()] = wartosc.strip()
        dane.append(nowy_wiersz)
    plik.close()

    if len(kolumny) < 2:
        raise ValueError("CSV musi mieć co najmniej 2 kolumny.")

    # ostatnia kolumna to decyzja, reszta to atrybuty
    decyzja = kolumny[-1]
    atrybuty = kolumny[:-1]
    return dane, atrybuty, decyzja


def z_tekstu(tekst):
    # dzielimy tekst na linie i pomijamy puste
    wszystkie_linie = tekst.strip().split("\n")
    linie = []
    for linia in wszystkie_linie:
        if linia.strip() != "":
            linie.append(linia.strip())

    if len(linie) < 2:
        raise ValueError("Potrzeba nagłówka i co najmniej jednego wiersza.")

    # pierwsza linia to nagłówki kolumn
    naglowki = []
    for n in linie[0].split(","):
        naglowki.append(n.strip())

    # pozostałe linie to dane
    dane = []
    for linia in linie[1:]:
        wartosci = []
        for v in linia.split(","):
            wartosci.append(v.strip())
        if len(wartosci) != len(naglowki):
            raise ValueError("Wiersz '" + linia + "' ma złą liczbę kolumn.")
        dane.append(dict(zip(naglowki, wartosci)))

    # ostatnia kolumna to decyzja, reszta to atrybuty
    decyzja = naglowki[-1]
    atrybuty = naglowki[:-1]
    return dane, atrybuty, decyzja


def podziel(dane, procent=0.7):
    # obliczamy ile wierszy idzie do treningu
    n = int(len(dane) * procent)
    if n < 1:
        n = 1
    trening = dane[:n]
    test = dane[n:]
    return trening, test