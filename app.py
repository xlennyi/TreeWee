import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from data_handler import DOMYSLNE_DANE, DOMYSLNA_DECYZJA


# zarzadzamy cala aplikacja tworzac okno i obslugujac podstawowa logike danych w gui
class Aplikacja:

    def __init__(self, root):
        self.root = root
        self.root.title("Drzewa Decyzyjne")
        self.root.geometry("1150x720")

        # poczatkowe dane i zmienne
        self.dane = list(DOMYSLNE_DANE)
        self.decyzja = DOMYSLNA_DECYZJA
        self.atrybuty = []
        for k in self.dane[0]:
            if k != self.decyzja:
                self.atrybuty.append(k)
        self.drzewo = None

        self.buduj_gui()
        self.odswiez_tabele()

    # budujemy caly graficzny interfejs uzytkownika dla okna glownego
    def buduj_gui(self):

        # gorny pasek z nazwa i przyciskami
        pasek = tk.Frame(self.root, bg="#2c3e50", pady=5)
        pasek.pack(fill=tk.X)

        tk.Label(pasek, text="Drzewa Decyzyjne", bg="#2c3e50", fg="white",
                 font=("Arial", 13, "bold")).pack(side=tk.LEFT, padx=10)

        tk.Button(pasek, text="Wczytaj CSV",
                  bg="#3498db", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=3)
        tk.Button(pasek, text="Edytuj dane",
                  bg="#9b59b6", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=3)
        tk.Button(pasek, text="Zapisz wyniki",
                  bg="#27ae60", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=3)
        tk.Button(pasek, text="Reset",
                  bg="#e67e22", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=3)

        # glowny obszar tj lewa i prawa kolumna
        main = tk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # lewa kolumna tj tabela i parametry
        lewa = tk.Frame(main, width=360)
        lewa.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        lewa.pack_propagate(False)

        tk.Label(lewa, text="Dane wejsciowe", font=("Arial", 9, "bold")).pack(anchor=tk.W)

        # tabela z danymi
        ramka_tabeli = tk.Frame(lewa)
        ramka_tabeli.pack(fill=tk.BOTH, expand=True)

        self.tabela = ttk.Treeview(ramka_tabeli, show="headings", height=9)
        scroll_y = ttk.Scrollbar(ramka_tabeli, orient=tk.VERTICAL, command=self.tabela.yview)
        scroll_x = ttk.Scrollbar(ramka_tabeli, orient=tk.HORIZONTAL, command=self.tabela.xview)
        self.tabela.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # parametry algorytmu
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

        # przyciski akcji (na razie nic nie robia)
        ramka_btn = tk.Frame(lewa)
        ramka_btn.pack(fill=tk.X, pady=3)

        tk.Button(ramka_btn, text="Buduj drzewo",
                  bg="#2ecc71", fg="white", font=("Arial", 10, "bold"),
                  relief=tk.FLAT, padx=8, pady=4).pack(side=tk.LEFT, padx=3)
        tk.Button(ramka_btn, text="Klasyfikuj obiekt",
                  bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                  relief=tk.FLAT, padx=8, pady=4).pack(side=tk.LEFT, padx=3)

        # wyniki klasyfikacji
        ramka_wyniki = tk.LabelFrame(lewa, text="Wyniki")
        ramka_wyniki.pack(fill=tk.X, pady=3)

        self.lbl_dok = tk.Label(ramka_wyniki, text="Dokladnosc: -", font=("Arial", 10))
        self.lbl_dok.pack(anchor=tk.W, padx=5)

        self.lbl_stat = tk.Label(ramka_wyniki, text="Wezly: - | Liscie: - | Wysokosc: -", font=("Arial", 9))
        self.lbl_stat.pack(anchor=tk.W, padx=5)

        # prawa kolumna z zakladka drzewa
        prawa = tk.Frame(main)
        prawa.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tabs = ttk.Notebook(prawa)
        tabs.pack(fill=tk.BOTH, expand=True)

        # zakladka z wizualizacja drzewa
        tab_drzewo = tk.Frame(tabs, bg="white")
        tabs.add(tab_drzewo, text="Drzewo")

        self.fig, self.ax = plt.subplots(figsize=(6, 4.5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=tab_drzewo)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # pusty wykres na start
        self.ax.text(0.5, 0.5, "Zbuduj drzewo", ha='center', va='center',
                     fontsize=12, color='gray')
        self.ax.axis('off')
        self.canvas.draw()

    # odswiezamy widok tabeli danych po lewej stronie po zmianie zbioru wejsciowego
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


# uruchamiamy caly proces aplikacji w glównej petli okna tkinter
if __name__ == "__main__":
    root = tk.Tk()
    Aplikacja(root)
    root.mainloop()