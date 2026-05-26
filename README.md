# Volební scraper 2017

Třetí (závěrečný) projekt Engeto Online Python Akademie. Skript stahuje výsledky
voleb do Poslanecké sněmovny PČR z roku 2017 pro libovolný okres z webu
[volby.cz](https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ) a uloží je do
CSV souboru.

## Instalace knihoven

Doporučuji použít vlastní virtuální prostředí. Knihovny potřebné pro běh
programu jsou v souboru `requirements.txt`.

```
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

## Spuštění projektu

Skript spouštějte z příkazové řádky se dvěma argumenty:

1. **odkaz** na stránku okresu (typ `ps32`) z volby.cz
2. **jméno výstupního CSV** souboru

```
python projekt_3.py <odkaz_uzemniho_celku> <vystupni_soubor>
```

Pokud chybí některý z argumentů, případně odkaz neukazuje na stránku
`ps32` na volby.cz, program vypíše chybu a skončí.

## Ukázka

Stažení výsledků pro okres **Praha-západ**:

```
python projekt_3.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2110" vysledky_praha_zapad.csv
```

Průběh:

```
STAHUJI DATA Z URL: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2110
NALEZENO OBCI: 79
  zpracovavam 539104 Bojanovice
  zpracovavam 571199 Bratřínov
  zpracovavam 599735 Březová-Oleško
  ...
UKLADAM DATA DO SOUBORU: vysledky_praha_zapad.csv
DOKONCUJI: projekt_3.py
```

Výřez z výstupu (`vysledky_praha_zapad.csv`):

```
code,location,registered,envelopes,valid,Občanská demokratická strana,Řád národa - Vlastenecká unie,...
539104,Bojanovice,372,268,267,36,0,0,24,0,19,15,1,3,6,0,0,36,0,0,13,78,...
571199,Bratřínov,202,150,150,11,0,0,9,1,18,4,1,1,5,0,0,16,0,0,3,52,...
```

Každý řádek odpovídá jedné obci. Sloupce:

| sloupec | význam |
| --- | --- |
| `code` | kód obce |
| `location` | název obce |
| `registered` | voliči v seznamu |
| `envelopes` | vydané obálky |
| `valid` | platné hlasy |
| ostatní | počet hlasů pro každou kandidující stranu |
