"""
scrape_painel_onco.py
Raspador do PAINEL-Oncologia para câncer pediátrico (0-19 anos).
Roda em 2 fases: inspect_form() -> scrape().
"""
import requests, re, pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from urllib.parse import urljoin

BASE = "https://tabnet.datasus.gov.br"
CGI  = "/cgi/tabcgi.exe?PAINEL_ONCO/PAINEL_ONCOLOGIABR.def"
FORM = "/cgi/dhdat.exe?PAINEL_ONCO/PAINEL_ONCOLOGIABR.def"

def inspect_form():
    """
    FASE 1 - Rode isso primeiro.
    Descobre os nomes/valores exatos dos campos do form (eles vêm
    URL-encoded em ISO-8859-1 e variam por .def).
    Copie os valores que interessam pra montar o payload da fase 2.
    """
    r = requests.get(BASE + FORM)
    r.encoding = "iso-8859-1"
    soup = BeautifulSoup(r.text, "html.parser")

    for sel in soup.find_all("select"):
        print(f"\n<SELECT name={sel.get('name')!r}>")
        for opt in sel.find_all("option")[:10]:
            print(f"   value={opt.get('value')!r:40s}  label={opt.text.strip()!r}")

    # Checkboxes de filtro começam com 'S' (SFaixa_Etária, SRegião, etc)
    seen = set()
    for inp in soup.find_all("input", {"type": "checkbox"}):
        name = inp.get("name", "")
        if name.startswith("S") and name not in seen:
            seen.add(name)
            print(f"\n<CHECKBOX group={name!r}>  (exemplo de value: {inp.get('value')!r})")

def scrape(linha, coluna, anos, filtros, out="painel_onco_ped.csv"):
    """
    FASE 2 - Monta o POST e baixa o CSV gerado.
    
    linha/coluna: valores do select (copia da inspect_form)
    anos:  ['2023','2022','2021','2020','2019']
    filtros: dict tipo {'SFaixa_Et%E1ria': ['0_a_9_anos', '10_a_14_anos', '15_a_19_anos']}
    """
    payload = [("Linha", linha), ("Coluna", coluna), ("Incremento", "Casos")]
    for ano in anos:
        payload.append(("Arquivos", f"pauonbr{ano[-2:]}.dbf"))
    for campo, valores in filtros.items():
        for v in valores:
            payload.append((campo, v))
    payload += [("formato", "table"), ("mostre", "Mostra")]

    r = requests.post(BASE + CGI, data=payload)
    r.encoding = "iso-8859-1"

    # O TabNet devolve HTML com link pra um CSV temporário em /csv/
    m = re.search(r'href="(/?csv/[^"]+\.csv)"', r.text, re.I)
    if m:
        csv = requests.get(urljoin(BASE, m.group(1)))
        csv.encoding = "iso-8859-1"
        with open(out, "w", encoding="utf-8") as f:
            f.write(csv.text)
        print(f"[ok] salvo: {out}")
        return pd.read_csv(StringIO(csv.text), sep=";",
                           skiprows=3, skipfooter=8, engine="python")

    # Fallback: parse direto da tabela HTML
    tables = pd.read_html(r.text, decimal=",", thousands=".")
    df = tables[0] if tables else None
    if df is not None:
        df.to_csv(out, index=False, sep=";")
        print(f"[ok, fallback HTML] salvo: {out}")
    else:
        print("[erro] nenhuma tabela nem CSV encontrados. Veja r.text")
    return df


if __name__ == "__main__":
    # Fase 1: descobre nomes
    inspect_form()

    # Fase 2: depois de copiar os nomes corretos, comenta inspect_form() 
    # e descomenta isso:
    # df = scrape(
    #     linha="Regi%E3o_-_resid%EAncia",
    #     coluna="Tempo_at%E9_o_tratamento",
    #     anos=["2023","2022","2021","2020","2019"],
    #     filtros={"SFaixa_Et%E1ria": ["0_a_9_anos","10_a_14_anos","15_a_19_anos"]},
    # )
    # print(df)