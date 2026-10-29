"""Funções de negócio do painel Financeiro em Dia."""
from __future__ import annotations

import pandas as pd

COLUNAS_DATA = ["data_emissao", "data_vencimento", "data_pagamento"]


def preparar_dados(df: pd.DataFrame) -> pd.DataFrame:
    dados = df.copy()
    for coluna in COLUNAS_DATA:
        dados[coluna] = pd.to_datetime(dados[coluna], errors="coerce")
    dados["valor"] = pd.to_numeric(dados["valor"], errors="coerce").fillna(0.0)
    dados["status"] = dados["status"].fillna("Em aberto")
    return dados


def classificar_titulo(linha: pd.Series, referencia: pd.Timestamp) -> str:
    if linha["status"] == "Pago":
        return "Pago"
    dias = (linha["data_vencimento"].normalize() - referencia.normalize()).days
    if dias < 0:
        return "Atrasado"
    if linha["criticidade"] == "Alta" or dias <= 3:
        return "Alta"
    if dias <= 7 or linha["criticidade"] == "Média":
        return "Média"
    return "Normal"


def enriquecer_titulos(df: pd.DataFrame, referencia: pd.Timestamp) -> pd.DataFrame:
    dados = df.copy()
    dados["dias_para_vencer"] = (dados["data_vencimento"].dt.normalize() - referencia.normalize()).dt.days
    dados["prioridade"] = dados.apply(classificar_titulo, axis=1, referencia=referencia)
    ordem = {"Atrasado": 0, "Alta": 1, "Média": 2, "Normal": 3, "Pago": 4}
    dados["ordem_prioridade"] = dados["prioridade"].map(ordem)
    return dados
