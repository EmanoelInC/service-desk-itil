"""
Service Desk ITIL — Simulador de Chamados
==========================================
Autor: Emanoel Cavalcante

Simulação de um sistema de gestão de chamados baseado
nos princípios ITIL® 4, aplicando os conceitos de:
 - Gestão de Incidentes
 - Gestão de Problemas
 - Service Level Management (SLM)
 - Análise de Causa Raiz
 - Relatório de Desempenho (Service Reporting)

A lógica reflete a gestão de SLAs e ocorrências
praticada na operação CDDNPA (ID Logistics) —
transposta para o contexto de TI.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from datetime import datetime, timedelta
import random

np.random.seed(2025)
random.seed(2025)

print("=" * 62)
print("  SERVICE DESK ITIL — SIMULADOR DE CHAMADOS")
print("  Emanoel Cavalcante · emanoelinc.github.io")
print("=" * 62)

# ──────────────────────────────────────────────
# 1. CONFIGURAÇÃO DO SERVICE DESK
# ──────────────────────────────────────────────

# SLAs por prioridade (horas para resolução)
SLA = {
    'P1 — Crítico':  1,
    'P2 — Alto':     4,
    'P3 — Médio':    8,
    'P4 — Baixo':   24,
}

CATEGORIAS = [
    'Infraestrutura', 'Acesso / Permissão', 'Sistema ERP',
    'Rede / Conectividade', 'Hardware', 'BI / Relatórios', 'Outros'
]

STATUS = ['Resolvido', 'Resolvido', 'Resolvido', 'Fechado', 'Em andamento', 'Pendente']

# ──────────────────────────────────────────────
# 2. GERAÇÃO DE CHAMADOS (90 dias simulados)
# ──────────────────────────────────────────────

print("\n[1/5] Gerando base de chamados...")

n_chamados = 350
inicio = datetime(2025, 3, 1)

prioridades = np.random.choice(
    list(SLA.keys()), n_chamados,
    p=[0.05, 0.15, 0.50, 0.30]
)

datas_abertura = [
    inicio + timedelta(
        days=random.randint(0, 89),
        hours=random.randint(7, 19),
        minutes=random.randint(0, 59)
    )
    for _ in range(n_chamados)
]

# Tempo de resolução: a maioria dentro do SLA, alguns fora
tempos_resolucao = []
for p in prioridades:
    sla_h = SLA[p]
    # 88% dentro do SLA
    if random.random() < 0.88:
        t = random.uniform(0.2 * sla_h, 0.95 * sla_h)
    else:
        t = random.uniform(1.1 * sla_h, 3.5 * sla_h)
    tempos_resolucao.append(round(t, 2))

df = pd.DataFrame({
    'id':               [f'INC-{2025000 + i}' for i in range(n_chamados)],
    'data_abertura':    datas_abertura,
    'prioridade':       prioridades,
    'categoria':        np.random.choice(CATEGORIAS, n_chamados),
    'status':           np.random.choice(STATUS, n_chamados, p=[0.55, 0.20, 0.10, 0.08, 0.05, 0.02]),
    'tempo_resolucao_h': tempos_resolucao,
    'satisfacao':       np.random.choice([1,2,3,4,5], n_chamados, p=[0.03,0.07,0.15,0.40,0.35]),
    'reincidente':      np.random.choice([True, False], n_chamados, p=[0.12, 0.88]),
})

df['data_abertura'] = pd.to_datetime(df['data_abertura'])
df['mes']           = df['data_abertura'].dt.to_period('M')
df['sla_limite_h']  = df['prioridade'].map(SLA)
df['sla_ok']        = df['tempo_resolucao_h'] <= df['sla_limite_h']
df['data_resolucao']= df['data_abertura'] + pd.to_timedelta(df['tempo_resolucao_h'], unit='h')

print(f"   → {len(df)} chamados gerados")
print(f"   → Período: {df['data_abertura'].min().date()} a {df['data_abertura'].max().date()}")

# ──────────────────────────────────────────────
# 3. KPIs ITIL
# ──────────────────────────────────────────────

print("\n[2/5] Calculando KPIs ITIL...")

sla_geral      = df['sla_ok'].mean() * 100
mttr           = df['tempo_resolucao_h'].mean()
satisfacao_m   = df['satisfacao'].mean()
reincidencia   = df['reincidente'].mean() * 100
p1_sla         = df[df['prioridade'] == 'P1 — Crítico']['sla_ok'].mean() * 100
volume_mes     = df.groupby('mes').size()

print(f"\n   ┌─ SLA Geral          : {sla_geral:.1f}%  (meta: ≥ 90%)")
print(f"   ├─ SLA P1 Críticos   : {p1_sla:.1f}%  (meta: ≥ 95%)")
print(f"   ├─ MTTR (horas)      : {mttr:.2f}h")
print(f"   ├─ Satisfação média  : {satisfacao_m:.2f}/5.0")
print(f"   ├─ Taxa reincidência : {reincidencia:.1f}%")
print(f"   └─ Chamados/mês      : {volume_mes.mean():.0f} (média)")

# Por prioridade
print("\n   SLA por Prioridade:")
sla_prio = df.groupby('prioridade').agg(
    total=('id','count'),
    dentro_sla=('sla_ok','sum'),
    tempo_medio=('tempo_resolucao_h','mean')
).reset_index()
sla_prio['sla_pct'] = (sla_prio['dentro_sla'] / sla_prio['total'] * 100).round(1)
for _, row in sla_prio.iterrows():
    status = '✓' if row['sla_pct'] >= 90 else '✗'
    print(f"   {status} {row['prioridade']:<20} {row['sla_pct']}% | MTTR {row['tempo_medio']:.1f}h | {row['total']} chamados")

# ──────────────────────────────────────────────
# 4. GESTÃO DE PROBLEMAS (Causa Raiz)
# ──────────────────────────────────────────────

print("\n[3/5] Análise de Problemas (Reincidentes)...")

reincidentes = df[df['reincidente']].groupby('categoria').agg(
    ocorrencias=('id','count'),
    mttr_medio=('tempo_resolucao_h','mean'),
    sla_pct=('sla_ok','mean')
).reset_index().sort_values('ocorrencias', ascending=False)
reincidentes['sla_pct'] = (reincidentes['sla_pct'] * 100).round(1)
reincidentes['mttr_medio'] = reincidentes['mttr_medio'].round(2)
reincidentes['acao'] = reincidentes['ocorrencias'].apply(
    lambda x: '🔴 Abrir Problema' if x > 6 else '🟡 Monitorar' if x > 3 else '🟢 OK'
)

print("\n   Categorias com reincidência:")
for _, row in reincidentes.iterrows():
    print(f"   {row['acao']} {row['categoria']:<25} {row['ocorrencias']} ocorr. | SLA {row['sla_pct']}%")

# ──────────────────────────────────────────────
# 5. VISUALIZAÇÃO
# ──────────────────────────────────────────────

print("\n[4/5] Gerando dashboard...")

BG    = '#0a0d14'; SURF = '#111520'; VERDE = '#00d4a4'
AZUL  = '#4f7fff'; AMAR = '#fbbf24'; VERM  = '#ff6b6b'
TEXTO = '#e8ecf5'; MUT  = '#8290aa'

fig = plt.figure(figsize=(20, 14), facecolor=BG)
gs  = gridspec.GridSpec(3, 3, figure=fig,
                        hspace=0.55, wspace=0.38,
                        left=0.05, right=0.97,
                        top=0.92, bottom=0.05)

fig.text(0.5, 0.96, 'SERVICE DESK ITIL — DASHBOARD DE DESEMPENHO',
         fontsize=16, color=TEXTO, ha='center', fontweight='bold')
fig.text(0.5, 0.93,
         f'Mar–Mai 2025  |  {len(df)} chamados  |  SLA Geral: {sla_geral:.1f}%  |  Emanoel Cavalcante',
         fontsize=9, color=MUT, ha='center')

# KPI Cards
kpis = [
    (f'{sla_geral:.1f}%', 'SLA Geral\n(meta ≥ 90%)', VERDE if sla_geral >= 90 else VERM),
    (f'{mttr:.1f}h', 'MTTR Médio', AZUL),
    (f'{satisfacao_m:.2f}/5', 'Satisfação\nMédia', VERDE),
    (f'{reincidencia:.1f}%', 'Taxa\nReincidência', AMAR),
    (f'{p1_sla:.1f}%', 'SLA P1\n(meta ≥ 95%)', VERDE if p1_sla >= 95 else VERM),
    (f'{len(df)}', 'Chamados\nno Período', AZUL),
]
ax_kpi = fig.add_subplot(gs[0, :])
ax_kpi.set_facecolor(SURF); ax_kpi.axis('off')
for i, (val, lbl, cor) in enumerate(kpis):
    x = 0.08 + i * 0.165
    ax_kpi.text(x, 0.70, val, transform=ax_kpi.transAxes,
                fontsize=20, color=cor, ha='center', fontweight='bold', fontfamily='monospace')
    ax_kpi.text(x, 0.18, lbl, transform=ax_kpi.transAxes,
                fontsize=8, color=MUT, ha='center', fontfamily='monospace')
    if i < 5:
        ax_kpi.axvline(x=0.165*(i+1)+0.003, color='#1e2740', lw=0.8, alpha=0.5)
ax_kpi.set_title('KPIs DO SERVICE DESK', color=TEXTO, fontsize=10,
                 fontfamily='monospace', pad=10, loc='left')

# Volume por mês
ax1 = fig.add_subplot(gs[1, 0])
ax1.set_facecolor(SURF)
ax1.bar([str(m) for m in volume_mes.index], volume_mes.values, color=AZUL, alpha=0.8)
ax1.tick_params(colors=MUT, labelsize=8)
[s.set_color('#1e2740') for s in ax1.spines.values()]
ax1.set_title('Volume de Chamados / Mês', color=TEXTO, fontsize=9,
              fontfamily='monospace', pad=6)

# SLA por prioridade
ax2 = fig.add_subplot(gs[1, 1])
ax2.set_facecolor(SURF)
cores_p = [VERDE if v >= 90 else VERM for v in sla_prio['sla_pct']]
labels_p = [p.split('—')[0].strip() for p in sla_prio['prioridade']]
ax2.barh(labels_p, sla_prio['sla_pct'], color=cores_p, height=0.5)
ax2.axvline(90, color=AMAR, linewidth=1.5, linestyle='--', label='Meta 90%')
ax2.set_xlim(70, 105)
ax2.tick_params(colors=MUT, labelsize=8)
[s.set_color('#1e2740') for s in ax2.spines.values()]
ax2.set_title('SLA % por Prioridade', color=TEXTO, fontsize=9,
              fontfamily='monospace', pad=6)
ax2.legend(fontsize=7, facecolor=SURF, edgecolor='#1e2740', labelcolor=MUT)

# Chamados por categoria
cat_count = df.groupby('categoria').size().sort_values()
ax3 = fig.add_subplot(gs[1, 2])
ax3.set_facecolor(SURF)
ax3.barh(cat_count.index, cat_count.values, color=AZUL, alpha=0.7, height=0.5)
ax3.tick_params(colors=MUT, labelsize=7)
[s.set_color('#1e2740') for s in ax3.spines.values()]
ax3.set_title('Chamados por Categoria', color=TEXTO, fontsize=9,
              fontfamily='monospace', pad=6)

# Satisfação
ax4 = fig.add_subplot(gs[2, 0])
ax4.set_facecolor(SURF)
sat_counts = df['satisfacao'].value_counts().sort_index()
cores_sat = [VERM, VERM, AMAR, VERDE, VERDE]
ax4.bar(sat_counts.index, sat_counts.values, color=cores_sat, width=0.5)
ax4.tick_params(colors=MUT, labelsize=9)
[s.set_color('#1e2740') for s in ax4.spines.values()]
ax4.set_title('Satisfação dos Usuários (1–5)', color=TEXTO, fontsize=9,
              fontfamily='monospace', pad=6)
ax4.set_xlabel('Nota', color=MUT, fontsize=8)

# Reincidência por categoria
ax5 = fig.add_subplot(gs[2, 1])
ax5.set_facecolor(SURF)
cores_r = [VERM if v > 6 else AMAR if v > 3 else VERDE for v in reincidentes['ocorrencias']]
ax5.barh(reincidentes['categoria'], reincidentes['ocorrencias'], color=cores_r, height=0.5)
ax5.axvline(6, color=VERM, linewidth=1.2, linestyle='--', label='Abrir Problema')
ax5.tick_params(colors=MUT, labelsize=7)
[s.set_color('#1e2740') for s in ax5.spines.values()]
ax5.set_title('Problemas Reincidentes por Categoria', color=TEXTO,
              fontsize=9, fontfamily='monospace', pad=6)
ax5.legend(fontsize=7, facecolor=SURF, edgecolor='#1e2740', labelcolor=MUT)

# MTTR por prioridade
ax6 = fig.add_subplot(gs[2, 2])
ax6.set_facecolor(SURF)
cores_m = [VERDE if t <= s else VERM
           for t, s in zip(sla_prio['tempo_medio'], sla_prio['sla_limite_h']
                           if hasattr(sla_prio, 'sla_limite_h')
                           else [SLA[p] for p in sla_prio['prioridade']])]
# recalc
sla_prio['sla_h'] = sla_prio['prioridade'].map(SLA)
cores_m2 = [VERDE if r['tempo_medio'] <= r['sla_h'] else VERM
            for _, r in sla_prio.iterrows()]
ax6.bar(labels_p, sla_prio['tempo_medio'], color=cores_m2, width=0.5, label='MTTR real')
ax6.plot(labels_p, sla_prio['sla_h'], color=AMAR, marker='D',
         linewidth=0, markersize=10, label='SLA limite', zorder=5)
ax6.tick_params(colors=MUT, labelsize=8)
[s.set_color('#1e2740') for s in ax6.spines.values()]
ax6.set_title('MTTR × SLA Limite (horas)', color=TEXTO, fontsize=9,
              fontfamily='monospace', pad=6)
ax6.legend(fontsize=7, facecolor=SURF, edgecolor='#1e2740', labelcolor=MUT)

plt.savefig('service_desk_itil_dashboard.png', dpi=150, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
print("   → service_desk_itil_dashboard.png gerado ✓")

print("\n[5/5] Resumo de Gestão de Problemas:")
print("   Categorias candidatas a registro formal de Problema ITIL:")
for _, row in reincidentes[reincidentes['ocorrencias'] > 6].iterrows():
    print(f"   → {row['categoria']}: {row['ocorrencias']} reincidências | MTTR {row['mttr_medio']:.1f}h")

print("\n✅ Service Desk ITIL concluído!")
