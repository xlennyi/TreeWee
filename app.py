import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from decision_tree import buduj_drzewo, klasyfikuj, dokladnosc, policz_wezly, policz_liscie, wysokosc
from data_handler import DOMYSLNE_DANE, DOMYSLNA_DECYZJA, wczytaj_csv, z_tekstu, podziel
from exporter import zapisz


# obliczamy wysokosc
def oblicz_wysokosc(drzewo):
    if drzewo["lisc"]:
        return 0
    najwyzsza = 0
    for poddrzewo in drzewo["galęzie"].values():
        h = oblicz_wysokosc(poddrzewo)
        if h > najwyzsza:
            najwyzsza = h
    return 1 + najwyzsza


# rysujemy wezel
def rysuj_wezel(ax, drzewo, x, y, dx, dy):
    if drzewo["lisc"]:
        ax.text(x, y, drzewo["decyzja"], ha='center', va='center', fontsize=8,
                bbox=dict(boxstyle='round', facecolor='#90EE90', edgecolor='green', alpha=0.9))
        return

    ax.text(x, y, drzewo["atrybut"], ha='center', va='center', fontsize=8,
            bbox=dict(boxstyle='round', facecolor='#ADD8E6', edgecolor='steelblue', alpha=0.9))

    galęzie = list(drzewo["galęzie"].items())
    liczba = len(galęzie)
    for i, (wartosc, poddrzewo) in enumerate(galęzie):
        nx = x + (i - (liczba - 1) / 2) * dx
        ny = y - dy
        ax.plot([x, nx], [y - 0.04, ny + 0.04], color='gray', lw=1)
        ax.text((x + nx) / 2, (y + ny) / 2, str(wartosc),
                ha='center', va='center', fontsize=7, color='darkred')
        rysuj_wezel(ax, poddrzewo, nx, ny, dx / max(liczba, 1), dy)


# zarządzamy aplikacja
class Aplikacja:

    def __init__(self, root):
        self.root = root
        self.root.title("Drzewa Decyzyjne")
        self.root.geometry("1150x720")

        self.dane = list(DOMYSLNE_DANE)
        self.decyzja = DOMYSLNA_DECYZJA
        self.atrybuty = []
        for k in self.dane[0]:
            if k != self.decyzja:
                self.atrybuty.append(k)
        self.drzewo = None

        self.buduj_gui()
        self.odswiez_tabele()

    # budujemy interfejs
    def buduj_gui(self):

        pasek = tk.Frame(self.root, bg="#2c3e50", pady=5)
        pasek.pack(fill=tk.X)

        tk.Label(pasek, text="Drzewa Decyzyjne", bg="#2c3e50", fg="white",
                 font=("Arial", 13, "bold")).pack(side=tk.LEFT, padx=10)

        tk.Button(pasek, text="Wczytaj CSV", command=self.wczytaj,
                  bg="#3498db", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=3)
        tk.Button(pasek, text="Edytuj dane", command=self.edytuj,
                  bg="#9b59b6", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=3)
        tk.Button(pasek, text="Zapisz wyniki", command=self.zapisz_wyniki,
                  bg="#27ae60", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=3)
        tk.Button(pasek, text="Reset", command=self.reset,
                  bg="#e67e22", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=3)

        main = tk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        lewa = tk.Frame(main, width=360)
        lewa.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        lewa.pack_propagate(False)

        tk.Label(lewa, text="Dane wejsciowe", font=("Arial", 9, "bold")).pack(anchor=tk.W)

        ramka_tabeli = tk.Frame(lewa)
        ramka_tabeli.pack(fill=tk.BOTH, expand=True)

        self.tabela = ttk.Treeview(ramka_tabeli, show="headings", height=9)
        scroll_y = ttk.Scrollbar(ramka_tabeli, orient=tk.VERTICAL, command=self.tabela.yview)
        scroll_x = ttk.Scrollbar(ramka_tabeli, orient=tk.HORIZONTAL, command=self.tabela.xview)
        self.tabela.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        ramka_param = tk.LabelFrame(lewa, text="Parametry", pady=3)
        ramka_param.pack(fill=tk.X, pady=6)

        self.metoda = tk.StringVar(value="Information Gain")
        self.max_glab = tk.IntVar(value=10)
        self.min_prob = tk.IntVar(value=1)
        self.podzial = tk.IntVar(value=70)

        tk.Label(ramka_param, text="Metoda:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Label(ramka_param, text="Max glebokos:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Label(ramka_param, text="Min probek:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        tk.Label(ramka_param, text="Trening %:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)

        tk.OptionMenu(ramka_param, self.metoda, "Information Gain", "Gain Ratio", "Gini").grid(
            row=0, column=1, sticky=tk.W, padx=5)
        tk.Spinbox(ramka_param, from_=1, to=20, textvariable=self.max_glab, width=5).grid(
            row=1, column=1, sticky=tk.W, padx=5)
        tk.Spinbox(ramka_param, from_=1, to=20, textvariable=self.min_prob, width=5).grid(
            row=2, column=1, sticky=tk.W, padx=5)
        tk.Spinbox(ramka_param, from_=50, to=90, textvariable=self.podzial, width=5).grid(
            row=3, column=1, sticky=tk.W, padx=5)

        ramka_btn = tk.Frame(lewa)
        ramka_btn.pack(fill=tk.X, pady=3)

        tk.Button(ramka_btn, text="Buduj drzewo", command=self.buduj,
                  bg="#2ecc71", fg="white", font=("Arial", 10, "bold"),
                  relief=tk.FLAT, padx=8, pady=4).pack(side=tk.LEFT, padx=3)
        tk.Button(ramka_btn, text="Klasyfikuj obiekt", command=self.klasyfikuj_okno,
                  bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                  relief=tk.FLAT, padx=8, pady=4).pack(side=tk.LEFT, padx=3)

        ramka_wyniki = tk.LabelFrame(lewa, text="Wyniki")
        ramka_wyniki.pack(fill=tk.X, pady=3)

        self.lbl_dok = tk.Label(ramka_wyniki, text="Dokladnosc: -", font=("Arial", 10))
        self.lbl_dok.pack(anchor=tk.W, padx=5)

        self.lbl_stat = tk.Label(ramka_wyniki, text="Wezly: - | Liscie: - | Wysokosc: -", font=("Arial", 9))
        self.lbl_stat.pack(anchor=tk.W, padx=5)

        prawa = tk.Frame(main)
        prawa.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tabs = ttk.Notebook(prawa)
        tabs.pack(fill=tk.BOTH, expand=True)

        tab_drzewo = tk.Frame(tabs, bg="white")
        tabs.add(tab_drzewo, text="Drzewo")

        self.fig, self.ax = plt.subplots(figsize=(6, 4.5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=tab_drzewo)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.pusty_wykres()

        tab_kroki = tk.Frame(tabs, bg="white")
        tabs.add(tab_kroki, text="Kroki budowania")

        self.logi_txt = tk.Text(tab_kroki, font=("Courier", 9), bg="#1e1e1e", fg="#00ff00")
        scroll_logi = ttk.Scrollbar(tab_kroki, command=self.logi_txt.yview)
        self.logi_txt.configure(yscrollcommand=scroll_logi.set)
        scroll_logi.pack(side=tk.RIGHT, fill=tk.Y)
        self.logi_txt.pack(fill=tk.BOTH, expand=True)

    # odswiezamy tabele
    def odswiez_tabele(self):
        if not self.dane:
            return
        kolumny = list(self.dane[0].keys())
        self.tabela["columns"] = kolumny
        for k in kolumny:
            self.tabela.heading(k, text=k)
            self.tabela.column(k, width=90, anchor=tk.CENTER)
        for wiersz in self.tabela.get_children():
            self.tabela.delete(wiersz)
        for i, wiersz in enumerate(self.dane):
            if i % 2 == 0:
                tag = "jasny"
            else:
                tag = "ciemny"
            self.tabela.insert("", tk.END, values=list(wiersz.values()), tags=(tag,))
        self.tabela.tag_configure("jasny", background="#f5f5f5")
        self.tabela.tag_configure("ciemny", background="#ffffff")

    # budujemy drzewo
    def buduj(self):
        if not self.dane:
            messagebox.showwarning("Brak danych", "Wczytaj lub zdefiniuj dane.")
            return
        trening, test = podziel(self.dane, self.podzial.get() / 100)
        logi = []
        self.drzewo = buduj_drzewo(
            trening, self.atrybuty, self.decyzja,
            self.metoda.get(), self.max_glab.get(), self.min_prob.get(),
            logi=logi
        )
        self.logi_txt.delete("1.0", tk.END)
        self.logi_txt.insert(tk.END, "Metoda: " + self.metoda.get() + "\n")
        self.logi_txt.insert(tk.END, "Trening: " + str(len(trening)) + " | Test: " + str(len(test)) + "\n")
        self.logi_txt.insert(tk.END, "-" * 35 + "\n")
        for log in logi:
            self.logi_txt.insert(tk.END, log + "\n")
        if test:
            zbior = test
        else:
            zbior = trening
        dok = dokladnosc(zbior, self.decyzja, self.drzewo)
        pop = int(dok * len(zbior))
        self.lbl_dok.config(text="Dokladnosc: " + str(round(dok * 100, 1)) + "% (" + str(pop) + "/" + str(len(zbior)) + ")")
        self.lbl_stat.config(
            text="Wezly: " + str(policz_wezly(self.drzewo)) +
                 " | Liscie: " + str(policz_liscie(self.drzewo)) +
                 " | Wysokosc: " + str(wysokosc(self.drzewo))
        )
        self.rysuj()

    # czyscimy wykres
    def pusty_wykres(self):
        self.ax.clear()
        self.ax.text(0.5, 0.5, "Zbuduj drzewo", ha='center', va='center',
                     fontsize=12, color='gray')
        self.ax.axis('off')
        self.canvas.draw()

    # rysujemy strukture
    def rysuj(self):
        self.ax.clear()
        self.ax.axis('off')
        if self.drzewo:
            h = oblicz_wysokosc(self.drzewo)
            dy = 0.85 / max(h + 1, 2)
            rysuj_wezel(self.ax, self.drzewo, 0.5, 0.93, 0.35, dy)
            self.ax.set_xlim(-0.1, 1.1)
            self.ax.set_ylim(0.0, 1.0)
        self.fig.tight_layout()
        self.canvas.draw()

    # otwieramy formularz
    def klasyfikuj_okno(self):
        if not self.drzewo:
            messagebox.showwarning("Brak drzewa", "Najpierw zbuduj drzewo.")
            return
        okno = tk.Toplevel(self.root)
        okno.title("Klasyfikuj obiekt")
        okno.geometry("340x280")
        tk.Label(okno, text="Podaj wartosci atrybutow:", font=("Arial", 10, "bold")).pack(pady=8)
        pola = {}
        for atrybut in self.atrybuty:
            ramka = tk.Frame(okno)
            ramka.pack(fill=tk.X, padx=15, pady=2)
            tk.Label(ramka, text=atrybut + ":", width=15, anchor=tk.W).pack(side=tk.LEFT)
            wartosci = []
            for wiersz in self.dane:
                if wiersz[atrybut] not in wartosci:
                    wartosci.append(wiersz[atrybut])
            wartosci.sort()
            var = tk.StringVar(value=wartosci[0])
            tk.OptionMenu(ramka, var, *wartosci).pack(side=tk.LEFT)
            pola[atrybut] = var
        wynik = tk.StringVar(value="")
        tk.Label(okno, textvariable=wynik, font=("Arial", 11, "bold"), fg="#27ae60").pack(pady=6)
        def klasyfikuj_klik():
            obiekt = {}
            for atr in self.atrybuty:
                obiekt[atr] = pola[atr].get()
            dec = klasyfikuj(obiekt, self.drzewo)
            wynik.set("Wynik: " + self.decyzja + " = " + dec)
        tk.Button(okno, text="Klasyfikuj", command=klasyfikuj_klik,
                  bg="#2ecc71", fg="white", font=("Arial", 10, "bold"),
                  relief=tk.FLAT, padx=10).pack()

    # otwieramy edytor
    def edytuj(self):
        okno = tk.Toplevel(self.root)
        okno.title("Edytuj dane")
        okno.geometry("560x400")
        tk.Label(okno, text="Wpisz dane w formacie CSV.\nPierwsza linia = naglowki, ostatnia kolumna = decyzja.",
                 justify=tk.LEFT).pack(padx=8, pady=5)
        pole = tk.Text(okno, font=("Courier", 9), height=16)
        pole.pack(fill=tk.BOTH, expand=True, padx=8)
        naglowki = ",".join(self.dane[0].keys())
        pole.insert(tk.END, naglowki + "\n")
        for wiersz in self.dane:
            pole.insert(tk.END, ",".join(wiersz.values()) + "\n")
        def zatwierdz():
            try:
                nowe_dane, atrybuty, decyzja = z_tekstu(pole.get("1.0", tk.END))
                self.dane = nowe_dane
                self.atrybuty = atrybuty
                self.decyzja = decyzja
                self.drzewo = None
                self.odswiez_tabele()
                self.pusty_wykres()
                okno.destroy()
            except Exception as blad:
                messagebox.showerror("Blad", str(blad))
        tk.Button(okno, text="Zatwierdz", command=zatwierdz,
                  bg="#2ecc71", fg="white", relief=tk.FLAT, padx=10, pady=4).pack(pady=5)

    # wczytujemy plik
    def wczytaj(self):
        sciezka = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not sciezka:
            return
        try:
            dane, atrybuty, decyzja = wczytaj_csv(sciezka)
            self.dane = dane
            self.atrybuty = atrybuty
            self.decyzja = decyzja
            self.drzewo = None
            self.odswiez_tabele()
            self.pusty_wykres()
            messagebox.showinfo("OK", "Wczytano " + str(len(dane)) + " wierszy.")
        except Exception as blad:
            messagebox.showerror("Blad", str(blad))

    # resetujemy ustawienia
    def reset(self):
        self.dane = list(DOMYSLNE_DANE)
        self.decyzja = DOMYSLNA_DECYZJA
        self.atrybuty = []
        for k in self.dane[0]:
            if k != self.decyzja:
                self.atrybuty.append(k)
        self.drzewo = None
        self.odswiez_tabele()
        self.pusty_wykres()
        self.logi_txt.delete("1.0", tk.END)
        self.lbl_dok.config(text="Dokladnosc: -")
        self.lbl_stat.config(text="Wezly: - | Liscie: - | Wysokosc: -")

    # zapisujemy raport
    def zapisz_wyniki(self):
        if not self.drzewo:
            messagebox.showwarning("Brak drzewa", "Najpierw zbuduj drzewo.")
            return
        sciezka = filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Tekst", "*.txt")])
        if not sciezka:
            return
        _, test = podziel(self.dane, self.podzial.get() / 100)
        if test:
            zbior = test
        else:
            zbior = self.dane
        dok = dokladnosc(zbior, self.decyzja, self.drzewo)
        parametry = {
            "Metoda": self.metoda.get(),
            "Max glebokos": self.max_glab.get(),
            "Min probek": self.min_prob.get(),
            "Podzial trening/test": str(self.podzial.get()) + "%",
            "Atrybut decyzji": self.decyzja,
        }
        wyniki = {
            "dokladnosc": dok,
            "poprawne": int(dok * len(zbior)),
            "wszystkich": len(zbior),
            "wezly": policz_wezly(self.drzewo),
            "liscie": policz_liscie(self.drzewo),
            "wysokosc": wysokosc(self.drzewo),
        }
        try:
            zapisz(sciezka, parametry, self.drzewo, wyniki)
            messagebox.showinfo("OK", "Zapisano: " + sciezka)
        except Exception as blad:
            messagebox.showerror("Blad", str(blad))


if __name__ == "__main__":
    root = tk.Tk()
    Aplikacja(root)
    root.mainloop()