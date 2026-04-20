"""
Cumprimento da Lei 12.732/2012 em câncer pediátrico
Fonte: PAINEL-Oncologia / DATASUS - 0-19 anos, diagnósticos 2019-2023
"""
import pandas as pd
import matplotlib.pyplot as plt
import re

CSV_PATH = "painel_onco_ped.csv"

# 1. Lê o arquivo bruto como texto
with open(CSV_PATH, "r", encoding="latin-1") as f:
    linhas = [l.rstrip("\r\n") for l in f.readlines()]

# 2. Detecta header: primeira linha que tem ";" E contém uma das palavras-chave
HEADER_KEYWORDS = ["residência", "residencia", "diagnóstico", "tratamento", "Município", "UF"]
header_idx = None
for i, l in enumerate(linhas):
    if ";" in l and any(k.lower() in l.lower() for k in HEADER_KEYWORDS):
        header_idx = i
        break

if header_idx is None:
    raise ValueError("Cabeçalho não encontrado.")

header = [c.strip().strip('"') for c in linhas[header_idx].split(";")]
print(f">>> Header na linha {header_idx}: {header[0]!r} + {len(header)-1} colunas\n")

# 3. Extrai linhas de dados — qualquer linha cujo primeiro campo NÃO é "Total"
#    e tem o mesmo número de colunas do header
dados = []
for l in linhas[header_idx + 1:]:
    partes = [c.strip().strip('"') for c in l.split(";")]
    if len(partes) != len(header):
        continue
    primeiro = partes[0]
    if primeiro.lower() == "total" or primeiro == "":
        continue
    dados.append(partes)

df = pd.DataFrame(dados, columns=header)
df = df.rename(columns={df.columns[0]: "local"})
df["local"] = df["local"].str.replace(r"^\d+\s*", "", regex=True).str.strip()

# 4. Converte numérico (ponto = separador de milhar em pt-BR)
for c in df.columns[1:]:
    df[c] = pd.to_numeric(
        df[c].str.replace(".", "", regex=False).replace({"-": "0", "": "0"}),
        errors="coerce",
    ).fillna(0)

# 5. Classifica colunas: dentro de 60 dias vs fora
DENTRO = ["-90", "-60", "-30", "mesmo", "1 a 10", "11 a 20",
          "21 a 30", "31 a 40", "41 a 50", "51 a 60"]
FORA = ["61 a 90", "91 a 120", "121", "301", "366", "mais de"]

dentro = [c for c in df.columns[1:] if any(k in c.lower() for k in [x.lower() for x in DENTRO])]
fora   = [c for c in df.columns[1:] if any(k in c.lower() for k in [x.lower() for x in FORA])]

df["no_prazo"] = df[dentro].sum(axis=1)
df["atrasado"] = df[fora].sum(axis=1)
df["total_com_info"] = df["no_prazo"] + df["atrasado"]
df["pct_atraso"] = 100 * df["atrasado"] / df["total_com_info"].replace(0, pd.NA)
df = df.dropna(subset=["pct_atraso"])

print("=" * 80)
print("RESULTADO")
print("=" * 80)
print(df[["local", "total_com_info", "no_prazo", "atrasado", "pct_atraso"]]
      .sort_values("pct_atraso", ascending=False)
      .to_string(index=False))

# 6. Gráfico
df_plot = df.sort_values("pct_atraso")
n_barras = len(df_plot)
altura = max(4.5, n_barras * 0.32)

fig, ax = plt.subplots(figsize=(12, altura))
# colore o pior em vermelho forte, melhor em salmão - gradiente
cores = plt.cm.Reds([0.35 + 0.6 * (i / max(n_barras - 1, 1)) for i in range(n_barras)])
bars = ax.barh(df_plot["local"], df_plot["pct_atraso"], color=cores)

ax.set_xlabel("% que esperaram MAIS de 60 dias até o 1º tratamento", fontsize=11)
ax.set_title(
    "Câncer pediátrico no Brasil — desigualdade no cumprimento da Lei 12.732/2012\n"
    f"0-19 anos · diagnósticos 2019-2023 · n = {int(df['total_com_info'].sum()):,}".replace(",", "."),
    fontsize=12, pad=15
)
ax.set_xlim(0, df_plot["pct_atraso"].max() * 1.28)

for bar, pct, n in zip(bars, df_plot["pct_atraso"], df_plot["atrasado"]):
    ax.text(bar.get_width() + 0.3,
            bar.get_y() + bar.get_height()/2,
            f"{pct:.1f}%  ({int(n):,})".replace(",", "."),
            va="center", fontsize=9)

ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", alpha=0.2)
plt.tight_layout()

out = "pct_atraso.png"
plt.savefig(out, dpi=150, bbox_inches="tight")
plt.show()
print(f"\n✓ gráfico salvo: {out}")