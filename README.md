# Câncer pediátrico no Brasil: análise de tempo até tratamento e completude de registro

> *"Quanto tempo uma criança com câncer espera no Brasil?"* — análise de dados públicos sobre cumprimento da Lei 12.732/2012 em pacientes pediátricos do SUS, baseada no PAINEL-Oncologia (DATASUS) e na Taxa de Cobertura ANS, para o período 2019-2023.

**Autor:** Victor Gonçalves Souto · [Souto Consultoria](https://soutoconsultoria.com.br) · victor@soutoconsultoria.com.br
**Versão atual:** 1.0 — abril de 2026
**Licença:** Código sob [MIT](LICENSE) · Texto sob [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.pt-br)

---

## 📖 Sobre o projeto

Este repositório contém todo o material — texto, dados, código e gráficos — de uma análise de divulgação técnica sobre o cumprimento da **Lei dos 60 Dias** (Lei 12.732/2012) em câncer pediátrico no Brasil.

A análise foi construída a partir de **dados 100% públicos** do Ministério da Saúde e da ANS, sem necessidade de acesso a microdados restritos. O objetivo é tornar a desigualdade visível e o método replicável.

### Os três achados principais

1. **Desigualdade no cumprimento da Lei dos 60 Dias.** Entre as crianças com registro completo de tratamento, **5.129 esperaram mais de 60 dias** entre o diagnóstico e o início do tratamento (1 em cada 7). A variação entre estados vai de 8,5% (Mato Grosso do Sul) a 28,9% (Sergipe).

2. **Cratera de informação no PAINEL-Oncologia pediátrico.** Para **54,5% das crianças diagnosticadas com câncer no SUS** entre 2019-2023 (44.199 casos), não há registro de tratamento no sistema. A completude varia de 26% (Tocantins) a 81% (Acre).

3. **A hipótese do tratamento privado não explica a cratera.** A correlação entre cobertura de planos de saúde por UF e a porcentagem "sem informação" no PAINEL é de **r = 0,02** — estatisticamente nula. O problema é interno ao SUS.

---

## 📑 Leia o artigo completo

→ **[Quanto tempo uma criança com câncer espera no Brasil?](artigo/quanto-tempo-crianca-com-cancer-espera.md)**

---

## 📊 Os gráficos

| Gráfico | Descrição |
|---|---|
| ![](graficos/pct_atraso_por_uf.png) | **Desigualdade por UF.** % de crianças que esperaram mais de 60 dias até o tratamento, por estado. |
| ![](graficos/completude_por_uf.png) | **Completude do registro.** % de casos com informação de tratamento, por estado. |
| ![](graficos/ans_vs_completude.png) | **Plano de saúde × falta de info.** Teste da hipótese "as crianças foram tratadas no privado". |

---

## 🔬 Como reproduzir

### Pré-requisitos

- Python 3.10+
- pandas, matplotlib, numpy

```bash
pip install pandas matplotlib numpy
```

### Passo a passo

1. **Clone este repositório:**
```bash
   git clone https://github.com/VictorGSoutoXP/oncologia-pediatrica-brasil.git
   cd oncologia-pediatrica-brasil
```

2. **Os dados brutos já estão na pasta `dados/`.** Eles foram extraídos manualmente do TabNet (DataSUS e ANS) seguindo os filtros descritos abaixo.

3. **Rode os scripts em ordem:**
```bash
   python scripts/01_analise_painel_onco.py
   python scripts/02_analise_completude.py
   python scripts/03_analise_ans_completude.py
```

   Os gráficos serão gerados na pasta atual.

### Como obter os dados brutos novamente

**PAINEL-Oncologia (DATASUS):**
- Acessar: https://datasus.saude.gov.br/informacoes-de-saude-tabnet/ → Epidemiológicas e Morbidade → Tempo até o início do tratamento oncológico
- Filtros: Faixa etária = 0 a 19 anos · Período = 2019-2023
- Linha = UF da residência (ou Região para o gráfico nacional)
- Coluna = Tempo Tratamento (detalhado)
- Conteúdo = Casos
- Salvar como CSV

**Cobertura ANS:**
- Acessar: https://www.ans.gov.br/anstabnet/ → Beneficiários → Taxa de Cobertura
- Filtros: Período = Dezembro/2021 · Faixa Etária = 1-4, 5-9, 10-14, 15-19 anos
- Linha = UF · Conteúdo = Assistência Médica
- Salvar como CSV

---

## 📂 Estrutura do repositório

```
oncologia-pediatrica-brasil/
├── artigo/          → Texto principal (Markdown)
├── dados/           → CSVs brutos do TabNet
├── scripts/         → Análises em Python
├── graficos/        → Visualizações geradas
├── README.md        → Este arquivo
└── LICENSE          → MIT (código)
```

---

## 🗺️ Roadmap

Este é um projeto vivo. As próximas versões já estão planejadas.

### v1.0 (atual) — abril de 2026
- ✅ Análise descritiva de tempo até tratamento por UF
- ✅ Análise de completude do registro
- ✅ Teste da hipótese de tratamento privado (ANS)

### v2.0 — em desenvolvimento
- ⏳ Cruzamento com o Cadastro Nacional de Estabelecimentos de Saúde (CNES)
- ⏳ Análise de distância até centros UNACON/CACON com habilitação em oncologia pediátrica
- ⏳ Intervalos de confiança para todas as estimativas estaduais

### v3.0 — futuro
- 🔜 Cruzamento com o Sistema de Informação sobre Mortalidade (SIM) para estimar quantas das 44.199 crianças "sem informação" faleceram antes do tratamento
- 🔜 Requer aprovação em Comitê de Ética em Pesquisa, dependendo de parceria acadêmica

---

## 🔍 Limitações conhecidas

Esta versão tem limitações que estão descritas em detalhe na seção "Limitações e próximos passos" do [artigo](artigo/quanto-tempo-crianca-com-cancer-espera.md). As principais:

- A Lei 12.732 permite atrasos clinicamente justificados; os dados não distinguem motivos
- Estados pequenos (Acre, Amapá, Roraima) têm intervalos de confiança largos por baixo n
- Distinguir "subnotificação" de "abandono" de "óbito antes do tratamento" exige cruzamento com SIM (planejado para v3.0)

---

## 🤝 Contribuição

**Encontrou um erro?** Tem uma análise adicional para sugerir? Trabalha com oncologia pediátrica e discorda de alguma conclusão?

Abra uma [issue](https://github.com/VictorGSoutoXP/oncologia-pediatrica-brasil/issues) ou escreva direto: **victor@soutoconsultoria.com.br**

Críticas técnicas legítimas serão incorporadas nas próximas versões com crédito.

---

## 📚 Fontes

- **PAINEL-Oncologia** (DATASUS / Ministério da Saúde) — https://datasus.saude.gov.br
- **ANS TABNET** (Agência Nacional de Saúde Suplementar) — https://www.ans.gov.br/anstabnet
- **Lei 12.732/2012** — http://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12732.htm

---

## ⚖️ Citação

Se você usar este trabalho em pesquisa, divulgação ou política pública, cite:

```
Victor Gonçalves Souto (2026). Quanto tempo uma criança com câncer espera no Brasil?
Souto Consultoria, abril de 2026.
Disponível em: https://github.com/VictorGSoutoXP/oncologia-pediatrica-brasil
```
