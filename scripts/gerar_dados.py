"""Gera uma base fictícia e reproduzível de contas a pagar."""
from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

SEMENTE = 20261028
QUANTIDADE = 500
ROOT = Path(__file__).resolve().parents[1]
DESTINO = ROOT / "data" / "contas_pagar.csv"

FORNECEDORES = [
    "Nuvem Clara Tecnologia", "Papelaria Horizonte", "Logística Rota Sul",
    "Energia do Vale", "Café das Palmeiras", "Consultoria Prisma",
    "Limpeza Brilho Novo", "Telefonia Conecta", "Alimentos Campo Bom",
    "Manutenção Ponto Certo", "Gráfica Estação", "Segurança Guardião",
    "Hotel Vila Serena", "Transporte Via Norte", "Software Ponto Azul",
    "Água Serra Verde", "Móveis Traço", "Serviços Alfa",
]
CATEGORIAS = ["Tecnologia", "Aluguel", "Serviços", "Logística", "Utilidades", "Materiais", "Viagens", "Marketing"]
CENTROS = ["Administrativo", "Comercial", "Operações", "Tecnologia", "Financeiro", "Pessoas"]
DESCRICOES = {
    "Tecnologia": ["Licença de software", "Hospedagem em nuvem", "Suporte técnico"],
    "Aluguel": ["Locação de escritório", "Condomínio", "Locação de equipamento"],
    "Serviços": ["Consultoria mensal", "Serviço de limpeza", "Manutenção preventiva"],
    "Logística": ["Frete de mercadorias", "Entrega expressa", "Armazenagem"],
    "Utilidades": ["Conta de energia", "Conta de água", "Telefonia e internet"],
    "Materiais": ["Material de escritório", "Insumos operacionais", "Compra de equipamentos"],
    "Viagens": ["Hospedagem corporativa", "Passagens", "Transporte terrestre"],
    "Marketing": ["Campanha digital", "Produção de conteúdo", "Material promocional"],
}


def gerar() -> None:
    rng = random.Random(SEMENTE)
    hoje = date.today()
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    campos = [
        "id_titulo", "fornecedor", "categoria", "centro_custo", "data_emissao",
        "data_vencimento", "valor", "status", "data_pagamento", "criticidade", "descricao",
    ]
    with DESTINO.open("w", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=campos)
        writer.writeheader()
        for n in range(1, QUANTIDADE + 1):
            emissao = hoje + timedelta(days=rng.randint(-390, 0))
            vencimento = emissao + timedelta(days=rng.choice([7, 14, 21, 28, 30, 35, 45, 60]))
            valor = round(rng.uniform(180, 28500) * rng.choice([0.7, 1, 1, 1, 1.35]), 2)
            probabilidade_pago = 0.65 if vencimento <= hoje else 0.10
            status = "Pago" if rng.random() < probabilidade_pago else "Em aberto"
            pagamento = ""
            if status == "Pago":
                pagamento_data = min(hoje, vencimento + timedelta(days=rng.randint(-5, 18)))
                pagamento_data = max(emissao, pagamento_data)
                pagamento = pagamento_data.isoformat()
            criticidade = rng.choices(["Alta", "Média", "Baixa"], weights=[18, 47, 35])[0]
            categoria = rng.choice(CATEGORIAS)
            writer.writerow({
                "id_titulo": f"CP-{n:04d}",
                "fornecedor": rng.choice(FORNECEDORES),
                "categoria": categoria,
                "centro_custo": rng.choice(CENTROS),
                "data_emissao": emissao.isoformat(),
                "data_vencimento": vencimento.isoformat(),
                "valor": f"{valor:.2f}",
                "status": status,
                "data_pagamento": pagamento,
                "criticidade": criticidade,
                "descricao": rng.choice(DESCRICOES[categoria]),
            })
    print(f"Base criada: {DESTINO} ({QUANTIDADE} títulos; referência de geração: {hoje:%d/%m/%Y})")


if __name__ == "__main__":
    gerar()

