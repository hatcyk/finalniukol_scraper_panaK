"""
projekt_3.py: treti projekt - Elections Scraper

author: hatcyk
email: 133507370+hatcyk@users.noreply.github.com
"""

import csv
import sys
import time
from urllib.parse import urlparse, parse_qs, urljoin

import requests
from bs4 import BeautifulSoup

HLAVICKY = {"User-Agent": "Mozilla/5.0 (volby-scraper; projekt_3.py)"}


def parse_args(argv: list[str]) -> tuple[str, str]:
    """Overi spravnost vstupnich argumentu a vrati (url, vystupni_soubor)."""
    if len(argv) != 3:
        sys.exit(
            "CHYBA: program ocekava prave 2 argumenty:\n"
            "  1) URL uzemniho celku (stranka typu ps32 na volby.cz)\n"
            "  2) jmeno vystupniho CSV souboru\n"
            f'priklad: python {argv[0]} '
            '"https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" '
            'vysledky_prostejov.csv'
        )

    url, output = argv[1], argv[2]

    parsed = urlparse(url)
    if "volby.cz" not in parsed.netloc or "ps32" not in parsed.path:
        sys.exit(
            "CHYBA: prvni argument musi byt odkaz na stranku ps32 webu volby.cz\n"
            f"  zadano: {url}"
        )

    query = parse_qs(parsed.query)
    if "xkraj" not in query or "xnumnuts" not in query:
        sys.exit(
            "CHYBA: odkaz musi obsahovat parametry xkraj a xnumnuts (vyber okresu)."
        )

    if not output.lower().endswith(".csv"):
        sys.exit("CHYBA: vystupni soubor musi mit priponu .csv")

    return url, output


def stahni_stranku(url: str, pokusy: int = 3) -> BeautifulSoup:
    """Stahne HTML danou URL a vrati objekt BeautifulSoup. Pri chybe to zkusi znovu."""
    posledni_chyba: Exception | None = None
    for pokus in range(1, pokusy + 1):
        try:
            odpoved = requests.get(url, headers=HLAVICKY, timeout=30)
            odpoved.raise_for_status()
            odpoved.encoding = odpoved.apparent_encoding
            return BeautifulSoup(odpoved.text, "html.parser")
        except requests.RequestException as chyba:
            posledni_chyba = chyba
            time.sleep(pokus)
    sys.exit(f"CHYBA: nepodarilo se stahnout {url}: {posledni_chyba}")


def ziskej_seznam_obci(url: str) -> list[tuple[str, str, str]]:
    """Vrati seznam (kod, nazev, url_detailu) pro vsechny obce v okrese."""
    soup = stahni_stranku(url)
    obce: list[tuple[str, str, str]] = []
    videno: set[str] = set()

    for tabulka in soup.find_all("table"):
        for radek in tabulka.find_all("tr"):
            bunky = radek.find_all("td")
            if len(bunky) < 3:
                continue
            kod = bunky[0].get_text(strip=True)
            nazev = bunky[1].get_text(strip=True)
            if not kod.isdigit() or kod in videno:
                continue
            odkaz_tag = bunky[0].find("a")
            if odkaz_tag is None:
                continue
            url_detailu = urljoin(url, odkaz_tag["href"])
            obce.append((kod, nazev, url_detailu))
            videno.add(kod)

    if not obce:
        sys.exit("CHYBA: na zadane strance se nepodarilo najit zadne obce.")
    return obce


def _ocisti_cislo(text: str) -> str:
    """Z volby.cz textu jako '1\xa0234' udela '1234'."""
    return text.replace("\xa0", "").replace(" ", "").strip()


def ziskej_vysledky_obce(url: str) -> dict[str, object]:
    """Z detailu obce vrati souhrn (volici, obalky, platne hlasy + slovnik hlasu po stranach)."""
    soup = stahni_stranku(url)
    tabulky = soup.find_all("table")
    if not tabulky:
        sys.exit(f"CHYBA: na strance {url} nejsou ocekavane tabulky.")

    # Souhrnna tabulka - 3. radek (index 2) je radek s hodnotami
    souhrn = tabulky[0].find_all("tr")[2].find_all("td")
    volici = _ocisti_cislo(souhrn[3].get_text())
    obalky = _ocisti_cislo(souhrn[4].get_text())
    platne = _ocisti_cislo(souhrn[7].get_text())

    # Tabulky stran (vsechny dalsi)
    strany: dict[str, str] = {}
    for tabulka in tabulky[1:]:
        radky = tabulka.find_all("tr")
        for radek in radky[2:]:
            bunky = radek.find_all("td")
            if len(bunky) < 3:
                continue
            cislo = bunky[0].get_text(strip=True)
            nazev = bunky[1].get_text(strip=True)
            hlasy = _ocisti_cislo(bunky[2].get_text())
            if cislo == "-" or not nazev:
                continue
            strany[nazev] = hlasy

    return {
        "volici": volici,
        "obalky": obalky,
        "platne": platne,
        "strany": strany,
    }


def main() -> None:
    url, output = parse_args(sys.argv)
    print(f"STAHUJI DATA Z URL: {url}")
    obce = ziskej_seznam_obci(url)
    print(f"NALEZENO OBCI: {len(obce)}")

    vysledky: list[dict[str, object]] = []
    nazvy_stran: list[str] = []

    for kod, nazev, url_detailu in obce:
        print(f"  zpracovavam {kod} {nazev}")
        data = ziskej_vysledky_obce(url_detailu)
        if not nazvy_stran:
            nazvy_stran = list(data["strany"].keys())
        vysledky.append({
            "kod": kod,
            "nazev": nazev,
            **data,
        })

    print(f"UKLADAM DATA DO SOUBORU: {output}")
    # utf-8-sig => Excel na Macu/Windows spravne pozna Ceske znaky
    with open(output, "w", encoding="utf-8-sig", newline="") as f:
        zapisovac = csv.writer(f)
        zapisovac.writerow(
            ["code", "location", "registered", "envelopes", "valid", *nazvy_stran]
        )
        for r in vysledky:
            zapisovac.writerow([
                r["kod"], r["nazev"], r["volici"], r["obalky"], r["platne"],
                *[r["strany"].get(s, "0") for s in nazvy_stran],
            ])
    print("DOKONCUJI: projekt_3.py")


if __name__ == "__main__":
    main()
