"""
projekt_3.py: treti projekt - Elections Scraper

author: hatcyk
email: 133507370+hatcyk@users.noreply.github.com
"""

import sys
from urllib.parse import urlparse, parse_qs, urljoin

import requests
from bs4 import BeautifulSoup


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


def stahni_stranku(url: str) -> BeautifulSoup:
    """Stahne HTML danou URL a vrati objekt BeautifulSoup."""
    odpoved = requests.get(url, timeout=30)
    odpoved.raise_for_status()
    odpoved.encoding = odpoved.apparent_encoding
    return BeautifulSoup(odpoved.text, "html.parser")


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


def main() -> None:
    url, output = parse_args(sys.argv)
    print(f"STAHUJI DATA Z URL: {url}")
    obce = ziskej_seznam_obci(url)
    print(f"NALEZENO OBCI: {len(obce)}")
    for kod, nazev, _ in obce[:3]:
        print(f"  {kod} - {nazev}")
    print(f"UKLADAM DATA DO SOUBORU: {output}")
    print("DOKONCUJI: projekt_3.py")


if __name__ == "__main__":
    main()
