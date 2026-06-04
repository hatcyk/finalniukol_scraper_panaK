import csv, requests
from bs4 import BeautifulSoup as BS
from urllib.parse import urljoin

URL = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2110"
OUT = "vysledky.csv"
cislo = lambda t: t.replace("\xa0", "").replace(" ", "").strip()
soup = lambda u: BS(requests.get(u).content, "html.parser")

obce = [(td[0].get_text(strip=True), td[1].get_text(strip=True), urljoin(URL, td[0].a["href"]))
        for tr in soup(URL).select("tr")
        if (td := tr.find_all("td")) and len(td) >= 3 and td[0].get_text(strip=True).isdigit() and td[0].a]

rows, hlavicka = [], None
for kod, nazev, u in obce:
    t = soup(u).find_all("table")
    s = t[0].find_all("tr")[2].find_all("td")
    strany = {td[1].get_text(strip=True): cislo(td[2].get_text())
              for tab in t[1:] for tr in tab.find_all("tr")[2:]
              if (td := tr.find_all("td")) and len(td) >= 3 and td[0].get_text(strip=True) != "-"}
    hlavicka = hlavicka or list(strany)
    rows.append([kod, nazev, cislo(s[3].get_text()), cislo(s[4].get_text()), cislo(s[7].get_text()),
                 *[strany.get(p, "0") for p in hlavicka]])
    print(kod, nazev)

with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["code", "location", "registered", "envelopes", "valid", *hlavicka])
    w.writerows(rows)
