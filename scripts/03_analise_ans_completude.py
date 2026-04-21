"""
Hipótese: a baixa completude do PAINEL-Oncologia é explicada por
cobertura de planos de saúde (crianças tratadas fora do SUS).
Teste: correlação entre taxa de cobertura ANS pediátrica (Dez/2021)
       e % "sem informação" no PAINEL-Oncologia (0-19a, 2019-2023).
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import unicodedata


def normaliza(s):
    """Remove acentos e padroniza pra fazer merge robusto."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()


# ---------- 1. Cobertura ANS ----------
# Tenta múltiplos encodings - o save do navegador bagunçou os acentos
ans = None
for enc in ["latin-1", "utf-8", "cp1252"]:
    try:
        ans = pd.read_csv("cobertura_ans.csv", sep=";", encoding=enc, decimal=",")
        break
    except Exception:
        continue

if ans is None:
    raise RuntimeError("Não consegui ler cobertura_ans.csv com nenhum encoding")

ans.columns = [c.strip() for c in ans.columns]
ans = ans.rename(columns={ans.columns[0]: "uf", ans.columns[1]: "cobertura_pct"})

# Como os acentos vieram corrompidos, remapeamos pelos nomes corretos na ordem
# em que a ANS lista as UFs (Norte → Nordeste → Sudeste → Sul → Centro-Oeste)
ufs_ordem_ans = [
    "Rondônia", "Acre", "Amazonas", "Roraima", "Pará", "Amapá", "Tocantins",
    "Maranhão", "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba",
    "Pernambuco", "Alagoas", "Sergipe", "Bahia", "Minas Gerais",
    "Espírito Santo", "Rio de Janeiro", "São Paulo", "Paraná",
    "Santa Catarina", "Rio Grande do Sul", "Mato Grosso do Sul",
    "Mato Grosso", "Goiás", "Distrito Federal"
]

if len(ans) == len(ufs_ordem_ans):
    ans["uf"] = ufs_ordem_ans
    print(f"✓ Nomes corrigidos: {len(ans)} UFs\n")
else:
    print(f"⚠ Esperava 27 UFs no CSV ANS, encontrei {len(ans)}.")
    print("   Verifica se o cobertura_ans.csv tem exatamente 27 linhas de dados.")
    print("   Vou tentar continuar usando os nomes do CSV mesmo assim.\n")

print("ANS (cobertura pediátrica de planos, Dez/2021):")
print(ans.to_string(index=False))
print()

# ---------- 2. PAINEL-Oncologia ----------
with open("painel_onco_ped.csv", "r", encoding="latin-1") as f:
    plinhas = [l.rstrip("\r\n") for l in f.readlines()]

KW = ["residência", "residencia", "diagnóstico", "tratamento", "Município", "UF"]
ph_idx = next(i for i, l in enumerate(plinhas)
              if ";" in l and any(k.lower() in l.lower() for k in KW))
pheader = [c.strip().strip('"') for c in plinhas[ph_idx].split(";")]
pdados = []
for l in plinhas[ph_idx + 1:]:
    partes = [c.strip().strip('"') for c in l.split(";")]
    if len(partes) != len(pheader) or partes[0].lower() in ("total", ""):
        continue
    pdados.append(partes)

painel = pd.DataFrame(pdados, columns=pheader)
painel = painel.rename(columns={painel.columns[0]: "uf"})
painel["uf"] = painel["uf"].str.replace(r"^\d+\s*", "", regex=True).str.strip()

for c in painel.columns[1:]:
    painel[c] = pd.to_numeric(
        painel[c].str.replace(".", "", regex=False).replace({"-": "0", "": "0"}),
        errors="coerce",
    ).fillna(0)

sem_info_col = [c for c in painel.columns if "sem informação" in c.lower()][0]
total_col = [c for c in painel.columns if c.lower().strip() == "total"][0]
painel["pct_sem_info"] = 100 * painel[sem_info_col] / painel[total_col]
painel["casos_painel"] = painel[total_col]

# ---------- 3. Merge usando chave normalizada (à prova de acento) ----------
ans["_key"] = ans["uf"].apply(normaliza)
painel["_key"] = painel["uf"].apply(normaliza)

df = ans.merge(
    painel[["_key", "pct_sem_info", "casos_painel"]],
    on="_key", how="inner"
).drop(columns="_key")

print(f"Merge: {len(df)} UFs casadas (esperado: 27)\n")

if len(df) < 27:
    nao_casaram = set(ans["uf"]) - set(df["uf"])
    print(f"⚠ Não casaram: {nao_casaram}\n")

# ---------- 4. Resultado ----------
print("=" * 80)
print("COBERTURA ANS PEDIÁTRICA × FALTA DE INFO NO PAINEL")
print("=" * 80)
print(df.sort_values("cobertura_pct", ascending=False).to_string(index=False))

corr = df[["cobertura_pct", "pct_sem_info"]].corr().iloc[0, 1]
print(f"\nCORRELAÇÃO: r = {corr:.3f}  (n = {len(df)})")
print()
if corr > 0.5:
    print("→ FORTE positiva. Cobertura privada EXPLICA boa parte da falta de info.")
elif corr > 0.3:
    print("→ Moderada positiva. Tratamento privado explica PARTE.")
elif abs(corr) <= 0.3:
    print("→ FRACA. Cobertura privada NÃO explica os 55% sem info.")
    print("  → A análise 2 vira manchete: subnotificação/abandono é a história real.")
else:
    print("→ NEGATIVA. UFs com mais plano têm MELHOR registro. Investigar.")

# ---------- 5. Scatter ----------
fig, ax = plt.subplots(figsize=(11, 7))
ax.scatter(df["cobertura_pct"], df["pct_sem_info"],
           s=df["casos_painel"] / 30, alpha=0.6,
           color="#2C5F8D", edgecolors="black", linewidth=0.5)

for _, row in df.iterrows():
    ax.annotate(row["uf"], (row["cobertura_pct"], row["pct_sem_info"]),
                fontsize=8, xytext=(5, 5), textcoords="offset points")

z = np.polyfit(df["cobertura_pct"], df["pct_sem_info"], 1)
xs = np.linspace(df["cobertura_pct"].min(), df["cobertura_pct"].max(), 100)
ax.plot(xs, np.polyval(z, xs), "--", color="gray", alpha=0.6,
        label=f"tendência (r = {corr:.2f}, n = {len(df)})")

ax.set_xlabel("Taxa de cobertura de planos de saúde — 0-19 anos (ANS, Dez/2021)")
ax.set_ylabel('% de casos "sem informação de tratamento" no PAINEL-Oncologia')
ax.set_title(
    'Tratamento privado explica a "falta de info" do SUS?\n'
    "PAINEL-Oncologia (0-19a, 2019-2023) × cobertura ANS pediátrica · "
    "círculo = nº de casos"
)
ax.legend(loc="upper left")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("ans_vs_completude.png", dpi=150, bbox_inches="tight")
plt.show()
print("\n✓ Salvo: ans_vs_completude.png")