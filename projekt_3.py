"""
projekt_3.py: treti projekt - Elections Scraper

author: hatcyk
email: 133507370+hatcyk@users.noreply.github.com
"""

import sys
from urllib.parse import urlparse, parse_qs


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


def main() -> None:
    url, output = parse_args(sys.argv)
    print(f"STAHUJI DATA Z URL: {url}")
    print(f"UKLADAM DATA DO SOUBORU: {output}")
    print("DOKONCUJI: projekt_3.py")


if __name__ == "__main__":
    main()
