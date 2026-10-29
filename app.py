from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from financeiro import enriquecer_titulos, preparar_dados  # noqa: E402

st.set_page_config(page_title="Financeiro em Dia", page_icon="💸", layout="wide")

st.markdown("""
<style>
    .stApp { background: #f5f7fb; }
    [data-testid="stMetric"] { background: white; border: 1px solid #e7ebf2; padding: 16px 18px; border-radius: 14px; }
    [data-testid="stMetricLabel"] p { color: #65728a; }
    h1, h2, h3 { color: #18243b; }
    .caption-box { color: #68758c; font-size: .92rem; margin-top: -10px; }
</style>
""", unsafe_allow_html=True)

st.title("💸 Financeiro em Dia")
st.markdown('<div class="caption-box">Contas a pagar e previsão de desembolsos • dados sintéticos para demonstração</div>', unsafe_allow_html=True)

arquivo = ROOT / "data" / "contas_pagar.csv"
if not arquivo.exists():
    st.error("Base de dados não encontrada. Gere o arquivo com `python scripts/gerar_dados.py`.")
    st.stop()

dados = preparar_dados(pd.read_csv(arquivo))
if dados.empty:
    st.warning("A base não contém títulos para exibir.")
    st.stop()

hoje = pd.Timestamp.today().normalize()
ref_default = min(max(hoje, dados["data_vencimento"].min().normalize()), dados["data_vencimento"].max().normalize())

with st.sidebar:
    st.header("Filtros")
    referencia = st.date_input("Data de referência", value=ref_default.date(), help="Usada para calcular atrasos e próximos vencimentos.")
    min_data = dados["data_vencimento"].min().date()
    max_data = dados["data_vencimento"].max().date()
    intervalo = st.date_input("Período de vencimento", value=(min_data, max_data), min_value=min_data, max_value=max_data)
    fornecedores = st.multiselect("Fornecedor", sorted(dados["fornecedor"].unique()))
    centros = st.multiselect("Centro de custo", sorted(dados["centro_custo"].unique()))
    categorias = st.multiselect("Categoria", sorted(dados["categoria"].unique()))
    criticidades = st.multiselect("Criticidade", ["Alta", "Média", "Baixa"])
    st.caption("A base é fictícia e não contém dados de empresas reais.")

ref = pd.Timestamp(referencia)
if isinstance(intervalo, tuple) and len(intervalo) == 2:
    inicio, fim = map(pd.Timestamp, intervalo)
else:
    inicio = fim = pd.Timestamp(intervalo)

filtrado = dados[(dados["data_vencimento"].dt.normalize() >= inicio) & (dados["data_vencimento"].dt.normalize() <= fim)].copy()
if fornecedores:
    filtrado = filtrado[filtrado["fornecedor"].isin(fornecedores)]
if centros:
    filtrado = filtrado[filtrado["centro_custo"].isin(centros)]
if categorias:
    filtrado = filtrado[filtrado["categoria"].isin(categorias)]
if criticidades:
    filtrado = filtrado[filtrado["criticidade"].isin(criticidades)]
filtrado = enriquecer_titulos(filtrado, ref)

abertos = filtrado[filtrado["status"] == "Em aberto"]
pagos = filtrado[filtrado["status"] == "Pago"]
atrasados = abertos[abertos["data_vencimento"].dt.normalize() < ref.normalize()]

fmt_brl = lambda valor: f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Em aberto", fmt_brl(abertos["valor"].sum()), f"{len(abertos)} títulos")
col2.metric("Vencido", fmt_brl(atrasados["valor"].sum()), f"{len(atrasados)} títulos")
col3.metric("Pago no período", fmt_brl(pagos["valor"].sum()), f"{len(pagos)} títulos")
if not abertos.empty:
    media_dias = abertos["dias_para_vencer"].clip(lower=0).mean()
    col4.metric("Prazo médio até vencer", f"{media_dias:.0f} dias")
else:
    col4.metric("Prazo médio até vencer", "—")

st.divider()
if filtrado.empty:
    st.info("Nenhum título corresponde aos filtros selecionados.")
    st.stop()

esq, dir = st.columns([1.65, 1])
with esq:
    st.subheader("Previsão de pagamentos · próximas 8 semanas")
    inicio_semana = ref.normalize() - pd.Timedelta(days=ref.weekday())
    semanas = pd.date_range(inicio_semana, periods=8, freq="W-MON")
    futuros = abertos[abertos["data_vencimento"].dt.normalize() >= ref.normalize()].copy()
    futuros["semana"] = futuros["data_vencimento"].dt.normalize() - pd.to_timedelta(futuros["data_vencimento"].dt.weekday, unit="D")
    resumo = futuros.groupby("semana")["valor"].sum().reindex(semanas, fill_value=0).rename_axis("Semana").reset_index(name="Valor previsto")
    fig = px.bar(resumo, x="Semana", y="Valor previsto", labels={"Semana": "Semana de vencimento", "Valor previsto": "Valor (R$)"}, color_discrete_sequence=["#3878f6"])
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), plot_bgcolor="white", paper_bgcolor="white", yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f", xaxis=dict(tickformat="%d/%m"), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
with dir:
    st.subheader("Em aberto por categoria")
    por_categoria = abertos.groupby("categoria", as_index=False)["valor"].sum().sort_values("valor", ascending=False)
    if por_categoria.empty:
        st.info("Sem contas em aberto nos filtros selecionados.")
    else:
        fig_cat = px.pie(por_categoria, names="categoria", values="valor", hole=0.62, color_discrete_sequence=px.colors.qualitative.Safe)
        fig_cat.update_traces(textposition="inside", textinfo="percent")
        fig_cat.update_layout(margin=dict(l=0, r=0, t=0, b=0), legend_title_text="", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_cat, use_container_width=True)
    st.subheader("Maiores fornecedores em aberto")
    por_fornecedor = abertos.groupby("fornecedor", as_index=False)["valor"].sum().nlargest(8, "valor").sort_values("valor")
    if por_fornecedor.empty:
        st.info("Sem contas em aberto nos filtros selecionados.")
    else:
        fig_for = px.bar(por_fornecedor, x="valor", y="fornecedor", orientation="h", labels={"fornecedor": "Fornecedor", "valor": "Valor (R$)"}, color_discrete_sequence=["#19a58a"])
        fig_for.update_layout(margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor="white", paper_bgcolor="white", xaxis_tickprefix="R$ ", xaxis_tickformat=",.0f", yaxis_title="")
        st.plotly_chart(fig_for, use_container_width=True)

st.subheader("Títulos que precisam de atenção")
if abertos.empty:
    st.info("Não há títulos em aberto para os filtros selecionados.")
else:
    atencao = abertos.sort_values(["ordem_prioridade", "data_vencimento", "valor"], ascending=[True, True, False]).copy()
    atencao["valor"] = atencao["valor"].map(fmt_brl)
    atencao["data_vencimento"] = atencao["data_vencimento"].dt.strftime("%d/%m/%Y")
    atencao["dias_para_vencer"] = atencao["dias_para_vencer"].map(lambda n: f"{abs(n)} dias atrasado" if n < 0 else ("vence hoje" if n == 0 else f"em {n} dias"))
    atencao = atencao.rename(columns={"id_titulo": "Título", "fornecedor": "Fornecedor", "categoria": "Categoria", "centro_custo": "Centro de custo", "data_vencimento": "Vencimento", "valor": "Valor", "criticidade": "Criticidade", "prioridade": "Prioridade", "dias_para_vencer": "Prazo"})
    st.dataframe(atencao[["Título", "Fornecedor", "Categoria", "Centro de custo", "Vencimento", "Prazo", "Valor", "Criticidade", "Prioridade"]], use_container_width=True, hide_index=True)

with st.expander("Ver todos os títulos do período"):
    geral = filtrado.copy()
    geral["valor"] = geral["valor"].map(fmt_brl)
    geral["data_vencimento"] = geral["data_vencimento"].dt.strftime("%d/%m/%Y")
    st.dataframe(geral[["id_titulo", "fornecedor", "categoria", "centro_custo", "data_vencimento", "valor", "status", "criticidade"]].rename(columns={"id_titulo": "Título", "fornecedor": "Fornecedor", "categoria": "Categoria", "centro_custo": "Centro de custo", "data_vencimento": "Vencimento", "valor": "Valor", "status": "Status", "criticidade": "Criticidade"}), use_container_width=True, hide_index=True)

st.caption("Prioridade é uma sugestão baseada em atraso, criticidade e proximidade do vencimento. Confirme os pagamentos nos sistemas oficiais da empresa.")
