# 🔄 Service Desk ITIL — Simulador de Chamados

> Simulação completa de um sistema de gestão de chamados baseado nos princípios ITIL® 4 — aplicando Gestão de Incidentes, Problemas, SLM e Service Reporting.

## KPIs calculados
- SLA Geral e por Prioridade (P1/P2/P3/P4)
- MTTR — Mean Time to Resolve
- Taxa de reincidência por categoria
- Satisfação dos usuários (CSAT)
- Volume de chamados MoM

## Gestão de Problemas
Identifica automaticamente categorias candidatas a registro formal de Problema ITIL com base na frequência de reincidência — mesma lógica aplicada na gestão de ocorrências da operação CDDNPA.

## Como executar
```bash
pip install pandas matplotlib numpy
python service_desk_itil.py
```

*Autor: Emanoel Cavalcante · [emanoelinc.github.io](https://emanoelinc.github.io)*
