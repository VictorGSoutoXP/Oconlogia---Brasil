"""
Completude do registro de tratamento por UF
Pergunta: a desigualdade que vemos é real ou artefato de subnotificação?
"""
import pandas as pd
import matplotlib.pyplot as plt
import re

CSV_PATH = "painel_onco_ped.csv"

# 1. Lê o CSV (mesma lógica robusta de antes)
with open(CSV_PATH, "r", encoding="latin-1") as f:
    linhas = [l.rstrip("\r\n") for l in f.readlines()]

HEADER_KEYWORDS = ["residência", "residencia", "diagnóstico", "tratamento", "Município", "UF"]
header_idx = next(i for i, l in enumerate(linhas)
                  if ";" in l and any(k.lower() in l.lower() for k in HEADER_KEYWORDS))

header = [c.strip().strip('"') for c in linhas[header_idx].split(";")]
dados = []
for l in linhas[header_idx + 1:]:
    partes = [c.strip().strip('"') for c in l.split(";")]
    if len(partes) != len(header) or partes[0].lower() == "total" or partes[0] == "":
        continue
    dados.append(partes)

df = pd.DataFrame(dados, columns=header)
df = df.rename(columns={df.columns[0]: "uf"})
df["uf"] = df["uf"].str.replace(r"^\d+\s*", "", regex=True).str.strip()

for c in df.columns[1:]:
    df[c] = pd.to_numeric(
        df[c].str.replace(".", "", regex=False).replace({"-": "0", "": "0"}),
        errors="coerce",
    ).fillna(0)

# 2. Completude = % de casos COM informação de tratamento (qualquer faixa)
sem_info_col = [c for c in df.columns if "sem informação" in c.lower()][0]
total_col = [c for c in df.columns if c.lower().strip() == "total"][0]

df["sem_info"] = df[sem_info_col]
df["total_geral"] = df[total_col]
df["com_info"] = df["total_geral"] - df["sem_info"]
df["pct_completude"] = 100 * df["com_info"] / df["total_geral"]
df["pct_sem_info"] = 100 - df["pct_completude"]

print("=" * 80)
print("COMPLETUDE DE REGISTRO POR UF (% com info de tratamento)")
print("=" * 80)
print(df[["uf", "total_geral", "com_info", "sem_info", "pct_completude"]]
      .sort_values("pct_completude")
      .to_string(index=False))

print(f"\nMédia nacional: {100 * df['com_info'].sum() / df['total_geral'].sum():.1f}%")
print(f"Pior UF: {df.loc[df['pct_completude'].idxmin(), 'uf']} "
      f"({df['pct_completude'].min():.1f}%)")
print(f"Melhor UF: {df.loc[df['pct_completude'].idxmax(), 'uf']} "
      f"({df['pct_completude'].max():.1f}%)")

# 3. Gráfico de completude
df_plot = df.sort_values("pct_completude")
fig, ax = plt.subplots(figsize=(12, 9))

# vermelho pra baixa completude (ruim), verde pra alta (bom) — gradiente RdYlGn
n = len(df_plot)
cores = plt.cm.RdYlGn([df_plot["pct_completude"].iloc[i] / 100 for i in range(n)])
bars = ax.barh(df_plot["uf"], df_plot["pct_completude"], color=cores)

ax.axvline(50, color="gray", linestyle="--", alpha=0.5, linewidth=1)
ax.text(50, n - 0.3, " 50%", color="gray", fontsize=9, va="top")

ax.set_xlabel("% de casos COM registro de tratamento (qualquer tempo)", fontsize=11)
ax.set_title(
    "Quão completo é o registro de tratamento oncológico pediátrico por UF?\n"
    f"PAINEL-Oncologia · 0-19 anos · 2019-2023 · n total = "
    f"{int(df['total_geral'].sum()):,}".replace(",", "."),
    fontsize=12, pad=15
)
ax.set_xlim(0, 105)

for bar, pct, n_com, n_total in zip(bars, df_plot["pct_completude"],
                                      df_plot["com_info"], df_plot["total_geral"]):
    ax.text(bar.get_width() + 1,
            bar.get_y() + bar.get_height()/2,
            f"{pct:.0f}%  ({int(n_com):,} de {int(n_total):,})".replace(",", "."),
            va="center", fontsize=9)

ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", alpha=0.2)
plt.tight_layout()
plt.savefig("completude_por_uf.png", dpi=150, bbox_inches="tight")
plt.show()

# 4. ANÁLISE CRUCIAL: completude correlaciona com % de atraso?
# Se sim -> nosso ranking de atraso está enviesado pela completude
df["no_prazo"] = df.filter(regex=r"-90|-60|-30|mesmo|1 a 10|11 a 20|21 a 30|31 a 40|41 a 50|51 a 60").sum(axis=1)
df["atrasado"] = df.filter(regex=r"61 a 90|91 a 120|121|301|366|mais de").sum(axis=1)
df["pct_atraso"] = 100 * df["atrasado"] / (df["no_prazo"] + df["atrasado"])

corr = df[["pct_completude", "pct_atraso"]].corr().iloc[0, 1]
print(f"\nCORRELAÇÃO completude × % atraso: {corr:.3f}")
print("Interpretação:")
if abs(corr) < 0.3:
    print("  → Correlação fraca. Ranking de atraso provavelmente NÃO é artefato de completude. ✓")
elif corr < -0.3:
    print("  → Correlação NEGATIVA. UFs com pior registro mostram MENOS atraso aparente.")
    print("    Isso sugere que estamos SUBESTIMANDO o atraso em UFs com registro ruim.")
elif corr > 0.3:
    print("  → Correlação POSITIVA. UFs com melhor registro mostram MAIS atraso.")
    print("    Possível artefato: registro melhor capta atrasos que outros perdem.")

# Scatter pra visualizar
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(df["pct_completude"], df["pct_atraso"], s=df["total_geral"]/30,
           alpha=0.6, color="#8B1A1A", edgecolors="black", linewidth=0.5)
for _, row in df.iterrows():
    ax.annotate(row["uf"], (row["pct_completude"], row["pct_atraso"]),
                fontsize=8, xytext=(5, 5), textcoords="offset points")
ax.set_xlabel("% completude do registro")
ax.set_ylabel("% de atraso (>60 dias) entre os com registro")
ax.set_title(f"O atraso aparente é artefato da completude? (r = {corr:.2f})\n"
             "Tamanho do círculo = nº de casos")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("completude_vs_atraso.png", dpi=150, bbox_inches="tight")
plt.show()

print("\n✓ Salvos: completude_por_uf.png + completude_vs_atraso.png")