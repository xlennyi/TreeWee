import math
from collections import Counter


# zliczamy ile razy każda klasa pojawia się w danych
def policz_klasy(dane, decyzja):
    liczniki = Counter()
    for wiersz in dane:
        klasa = wiersz[decyzja]
        liczniki[klasa] += 1
    return liczniki


# obliczamy entropię jako miarę nieuporządkowania zbioru
def entropia(dane, decyzja):
    n = len(dane)
    if n == 0:
        return 0

    liczniki = policz_klasy(dane, decyzja)
    wynik = 0
    for liczba in liczniki.values():
        p = float(liczba / n)
        wynik = wynik - p * math.log2(p)
    return wynik


# obliczamy zysk informacyjny dla danego atrybutu
def information_gain(dane, atrybut, decyzja):
    n = len(dane)
    entropia_przed = entropia(dane, decyzja)

    # zbieramy unikalne wartości atrybutu
    unikalne = set()
    for wiersz in dane:
        unikalne.add(wiersz[atrybut])

    # liczymy entropię po podziale
    entropia_po = 0
    for v in unikalne:
        podzbior = []
        for wiersz in dane:
            if wiersz[atrybut] == v:
                podzbior.append(wiersz)
        waga = len(podzbior) / n
        entropia_po = entropia_po + waga * entropia(podzbior, decyzja)

    return entropia_przed - entropia_po


# obliczamy gain ratio dzieląc zysk informacyjny przez liczbę wartości
def gain_ratio(dane, atrybut, decyzja):
    ig = information_gain(dane, atrybut, decyzja)

    unikalne = set()
    for wiersz in dane:
        unikalne.add(wiersz[atrybut])
    n_wartosci = len(unikalne)

    if n_wartosci == 0:
        return 0
    return ig / n_wartosci


# obliczamy współczynnik gini dla danego atrybutu
def gini(dane, atrybut, decyzja):
    n = len(dane)

    # gini dla węzła rodzica
    liczniki = policz_klasy(dane, decyzja)
    gini_rodzic = 1
    for k in liczniki.values():
        gini_rodzic = gini_rodzic - (k / n) ** 2

    # gini dla węzłów dzieci
    unikalne = set()
    for wiersz in dane:
        unikalne.add(wiersz[atrybut])

    gini_dzieci = 0
    for v in unikalne:
        podzbior = []
        for wiersz in dane:
            if wiersz[atrybut] == v:
                podzbior.append(wiersz)
        nv = len(podzbior)
        liczniki_v = policz_klasy(podzbior, decyzja)
        g = 1
        for k in liczniki_v.values():
            g = g - (k / nv) ** 2
        gini_dzieci = gini_dzieci + (nv / n) * g

    n_wartosci = len(unikalne)
    if n_wartosci == 0:
        return 0
    return (gini_rodzic - gini_dzieci) / n_wartosci


# wybieramy najlepszy atrybut do podziału według wybranej metody
def wybierz_atrybut(dane, atrybuty, decyzja, metoda):
    najlepszy = None
    najlepsza_wartosc = -1

    for atrybut in atrybuty:
        if metoda == "Information Gain":
            wartosc = information_gain(dane, atrybut, decyzja)
        elif metoda == "Gain Ratio":
            wartosc = gain_ratio(dane, atrybut, decyzja)
        else:
            wartosc = gini(dane, atrybut, decyzja)

        if wartosc > najlepsza_wartosc:
            najlepsza_wartosc = wartosc
            najlepszy = atrybut

    return najlepszy, najlepsza_wartosc


# budujemy rekurencyjnie drzewo decyzyjne
def buduj_drzewo(dane, atrybuty, decyzja, metoda, max_glab, min_prob, glab=0, logi=None):
    if logi is None:
        logi = []

    klasy = policz_klasy(dane, decyzja)
    dominujaca = max(klasy, key=klasy.get)
    spacja = "  " * glab

    # warunek stopu: wszystkie obiekty tej samej klasy
    if len(klasy) == 1:
        logi.append(spacja + "LIŚĆ → " + dominujaca + " (jedna klasa)")
        return {"lisc": True, "decyzja": dominujaca}

    # warunek stopu: brak atrybutów do podziału
    if len(atrybuty) == 0:
        logi.append(spacja + "LIŚĆ → " + dominujaca + " (brak atrybutów)")
        return {"lisc": True, "decyzja": dominujaca}

    # warunek stopu: za mało próbek
    if len(dane) < min_prob:
        logi.append(spacja + "LIŚĆ → " + dominujaca + " (za mało próbek)")
        return {"lisc": True, "decyzja": dominujaca}

    # warunek stopu: osiągnięto maksymalną głębokość
    if glab >= max_glab:
        logi.append(spacja + "LIŚĆ → " + dominujaca + " (max głębokość)")
        return {"lisc": True, "decyzja": dominujaca}

    # wybieramy najlepszy atrybut do podziału
    atrybut, wartosc_kryterium = wybierz_atrybut(dane, atrybuty, decyzja, metoda)
    logi.append(spacja + "WĘZEŁ głęb=" + str(glab) + ": atrybut='" + atrybut + "', obiektów=" + str(len(dane)))

    # tworzymy węzeł
    wezel = {"lisc": False, "atrybut": atrybut, "galęzie": {}, "domyslna": dominujaca}

    # usuwamy wybrany atrybut z listy
    pozostale = []
    for a in atrybuty:
        if a != atrybut:
            pozostale.append(a)

    # tworzymy gałąź dla każdej unikalnej wartości atrybutu
    unikalne = set()
    for wiersz in dane:
        unikalne.add(wiersz[atrybut])

    for v in unikalne:
        podzbior = []
        for wiersz in dane:
            if wiersz[atrybut] == v:
                podzbior.append(wiersz)
        logi.append(spacja + "  gałąź '" + str(v) + "': " + str(len(podzbior)) + " obiektów")
        wezel["galęzie"][v] = buduj_drzewo(podzbior, pozostale, decyzja, metoda, max_glab, min_prob, glab + 1, logi)

    return wezel


# klasyfikujemy jeden obiekt przechodząc po strukturze drzewa
def klasyfikuj(obiekt, drzewo):
    if drzewo["lisc"]:
        return drzewo["decyzja"]

    wartosc = obiekt.get(drzewo["atrybut"])

    if wartosc not in drzewo["galęzie"]:
        return drzewo["domyslna"]

    return klasyfikuj(obiekt, drzewo["galęzie"][wartosc])


# obliczamy procent poprawnych klasyfikacji na zbiorze danych
def dokladnosc(dane, decyzja, drzewo):
    poprawne = 0
    for wiersz in dane:
        if klasyfikuj(wiersz, drzewo) == wiersz[decyzja]:
            poprawne += 1
    if len(dane) == 0:
        return 0
    return poprawne / len(dane)


# zliczamy węzły wewnętrzne drzewa decyzyjnego
def policz_wezly(drzewo):
    if drzewo["lisc"]:
        return 0
    liczba = 1
    for poddrzewo in drzewo["galęzie"].values():
        liczba = liczba + policz_wezly(poddrzewo)
    return liczba


# zliczamy liście drzewa decyzyjnego
def policz_liscie(drzewo):
    if drzewo["lisc"]:
        return 1
    liczba = 0
    for poddrzewo in drzewo["galęzie"].values():
        liczba = Maxwell = liczba + policz_liscie(poddrzewo)
    return liczba


# obliczamy wysokość drzewa decyzyjnego
def wysokosc(drzewo):
    if drzewo["lisc"]:
        return 0
    najwyzsza = 0
    for poddrzewo in drzewo["galęzie"].values():
        h = wysokosc(poddrzewo)
        if h > najwyzsza:
            najwyzsza = h
    return 1 + najwyzsza