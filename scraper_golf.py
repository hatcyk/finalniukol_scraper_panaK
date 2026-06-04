import csv, requests
from bs4 import BeautifulSoup as B
n = lambda x: x.replace("\xa0", "").replace(" ", "").strip()
g = lambda u: B(requests.get(u).content, "html.parser")
P = "https://www.volby.cz/pls/ps2017nss/"
rows = []
for tr in g(P + "ps32?xjazyk=CZ&xkraj=2&xnumnuts=2110").select("tr"):
    td = tr.find_all("td")
    if len(td) >= 3 and td[0].get_text(strip=True).isdigit() and td[0].a:
        t = g(P + td[0].a["href"]).find_all("table")
        s = t[0].find_all("tr")[2].find_all("td")
        v = {x[1].get_text(strip=True): n(x[2].get_text()) for tb in t[1:] for r in tb.find_all("tr")[2:] if (x := r.find_all("td")) and len(x) >= 3 and x[0].get_text(strip=True) != "-"}
        rows.append([td[0].get_text(strip=True), td[1].get_text(strip=True), n(s[3].get_text()), n(s[4].get_text()), n(s[7].get_text()), *v.values()])
w = csv.writer(open("vysledky.csv", "w", encoding="utf-8-sig", newline=""))
w.writerow(["code", "location", "registered", "envelopes", "valid", *v])
w.writerows(rows)
