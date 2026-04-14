import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date, datetime
import gspread
from google.oauth2.service_account import Credentials

# ── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CampanhaOS · Gestão",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

COLUNAS = [
    "id", "tipo", "filiais", "nome_acao", "laboratorio", "ponto_focal",
    "data_inicio", "data_fim", "duracao_dias", "reposicao_por",
    "margem_AL", "margem_PE", "margem_SE", "observacoes", "criado_em",
]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── Tema escuro ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0D0F14 !important;
    color: #E2E8F0 !important;
    font-family: 'Syne', sans-serif !important;
}
[data-testid="stHeader"] { background: transparent !important; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; letter-spacing: -0.03em; }
h1 { font-weight: 800; font-size: 2rem !important; color: #F8FAFC !important; }
h2 { font-weight: 700; font-size: 1.25rem !important; color: #CBD5E1 !important; }
h3 { font-weight: 600; color: #94A3B8 !important; font-size: 0.85rem !important;
     text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stTextInput"] input,
[data-testid="stTextAreaRootElement"] textarea,
[data-testid="stDateInput"] input,
[data-testid="stNumberInput"] input {
    background-color: #161B27 !important;
    border: 1px solid #1E2A3A !important;
    border-radius: 6px !important;
    color: #E2E8F0 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.9rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextAreaRootElement"] textarea:focus {
    border-color: #09A49B !important;
    box-shadow: 0 0 0 2px rgba(9,164,155,0.15) !important;
}
[data-testid="stSelectbox"] > div > div {
    background-color: #161B27 !important;
    border: 1px solid #1E2A3A !important;
    border-radius: 6px !important;
    color: #E2E8F0 !important;
}
label, [data-testid="stWidgetLabel"] p {
    color: #94A3B8 !important; font-size: 0.8rem !important;
    font-weight: 600 !important; text-transform: uppercase !important;
    letter-spacing: 0.06em !important; font-family: 'Syne', sans-serif !important;
}
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #09A49B, #0D7A73) !important;
    color: #fff !important; border: none !important; border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    font-size: 0.9rem !important; padding: 0.6rem 2rem !important;
    transition: opacity 0.2s !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover { opacity: 0.85 !important; }
[data-testid="stButton"] > button[kind="secondary"] {
    background: #161B27 !important; color: #94A3B8 !important;
    border: 1px solid #1E2A3A !important; border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
}
[data-testid="stTabs"] [role="tablist"] { border-bottom: 1px solid #1E2A3A !important; gap: 0 !important; }
[data-testid="stTabs"] button[role="tab"] {
    background: transparent !important; color: #64748B !important;
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    font-size: 0.85rem !important; border: none !important;
    padding: 0.6rem 1.2rem !important; border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #09A49B !important; border-bottom: 2px solid #09A49B !important;
}
[data-testid="stDataFrame"] { border: 1px solid #1E2A3A !important; border-radius: 8px !important; overflow: hidden; }
hr { border-color: #1E2A3A !important; }
[data-testid="stRadio"] label { text-transform: none !important; font-size: 0.88rem !important; color: #CBD5E1 !important; }
[data-testid="stMetric"] {
    background: #161B27 !important; border: 1px solid #1E2A3A !important;
    border-radius: 8px !important; padding: 1rem !important;
}
[data-testid="stMetricLabel"] { color: #64748B !important; font-size: 0.75rem !important; }
[data-testid="stMetricValue"] { color: #F8FAFC !important; font-size: 1.6rem !important; font-weight: 800 !important; }
[data-testid="stCheckbox"] label { text-transform: none !important; font-size: 0.9rem !important; color: #CBD5E1 !important; }
[data-testid="stDownloadButton"] > button {
    background: #161B27 !important; border: 1px solid #1E2A3A !important;
    border-radius: 6px !important; color: #94A3B8 !important;
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    font-size: 0.82rem !important; padding: 0.45rem 1rem !important;
    transition: border-color 0.2s, color 0.2s !important;
}
[data-testid="stDownloadButton"] > button:hover {
    border-color: #09A49B !important; color: #09A49B !important;
}
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0D0F14; }
::-webkit-scrollbar-thumb { background: #1E2A3A; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Google Sheets ─────────────────────────────────────────────────────────────
@st.cache_resource
def conectar_sheets():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def get_worksheet():
    client = conectar_sheets()
    spreadsheet_id = st.secrets["SPREADSHEET_ID"]
    sh = client.open_by_key(spreadsheet_id)
    try:
        ws = sh.worksheet("Campanhas")
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title="Campanhas", rows=1000, cols=len(COLUNAS))
        ws.append_row(COLUNAS)  # cabeçalho
    return ws


@st.cache_data(ttl=30)  # cache de 30s para não bater a API em todo rerender
def carregar_dados() -> pd.DataFrame:
    try:
        ws = get_worksheet()
        dados = ws.get_all_records()
        if not dados:
            return pd.DataFrame(columns=COLUNAS)
        df = pd.DataFrame(dados, dtype=str)
        for col in COLUNAS:
            if col not in df.columns:
                df[col] = ""
        return df[COLUNAS]
    except Exception as e:
        st.error(f"Erro ao carregar dados do Sheets: {e}")
        return pd.DataFrame(columns=COLUNAS)


def salvar_linha(nova: dict):
    ws = get_worksheet()
    ws.append_row([nova.get(col, "") for col in COLUNAS])
    st.cache_data.clear()  # limpa cache para próxima leitura buscar dados frescos


def proximo_id(df: pd.DataFrame) -> str:
    if df.empty:
        return "CAM-001"
    nums = []
    for i in df["id"].dropna().tolist():
        try:
            nums.append(int(str(i).replace("CAM-", "")))
        except Exception:
            pass
    return f"CAM-{(max(nums) + 1):03d}" if nums else "CAM-001"


# ── Exportador Excel ──────────────────────────────────────────────────────────
def gerar_excel(df: pd.DataFrame) -> bytes:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Campanhas & Ações"

    thin  = Side(style="thin",   color="D1FAF8")
    thick = Side(style="medium", color="09A49B")
    borda     = Border(left=thin,  right=thin,  top=thin,  bottom=thin)
    borda_hdr = Border(left=thick, right=thick, top=thick, bottom=thick)

    ws.merge_cells("A1:N1")
    ws["A1"] = "CampanhaOS  —  Relatório de Campanhas & Ações"
    ws["A1"].font      = Font(name="Arial", bold=True, size=15, color="FFFFFF")
    ws["A1"].fill      = PatternFill("solid", fgColor="0D7A73")
    ws["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[1].height = 34

    ws.merge_cells("A2:N2")
    ws["A2"] = (
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        f"   |   Total: {len(df)}"
        f"   |   Campanhas: {len(df[df['tipo']=='Campanha'])}"
        f"   |   Ações: {len(df[df['tipo']=='Ação'])}"
    )
    ws["A2"].font      = Font(name="Arial", size=9, color="FFFFFF", italic=True)
    ws["A2"].fill      = PatternFill("solid", fgColor="09A49B")
    ws["A2"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[2].height = 18
    ws.row_dimensions[3].height = 6

    colunas = [
        ("ID",             "id",            10),
        ("Tipo",           "tipo",          13),
        ("Filiais",        "filiais",       14),
        ("Nome",           "nome_acao",     32),
        ("Laboratório",    "laboratorio",   24),
        ("Ponto Focal",    "ponto_focal",   22),
        ("Início",         "data_inicio",   13),
        ("Fim",            "data_fim",      13),
        ("Duração (dias)", "duracao_dias",  14),
        ("Reposição",      "reposicao_por", 14),
        ("Margem AL (%)",  "margem_AL",     14),
        ("Margem PE (%)",  "margem_PE",     14),
        ("Margem SE (%)",  "margem_SE",     14),
        ("Cadastrado em",  "criado_em",     20),
    ]

    for ci, (lbl, _, w) in enumerate(colunas, 1):
        cell = ws.cell(row=4, column=ci, value=lbl)
        cell.font      = Font(name="Arial", bold=True, size=9, color="FFFFFF")
        cell.fill      = PatternFill("solid", fgColor="1C4058")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border    = borda_hdr
        ws.column_dimensions[get_column_letter(ci)].width = w
    ws.row_dimensions[4].height = 26

    tipo_bg = {"Campanha": "1E3A5F", "Ação": "1A3A2A"}
    tipo_fg = {"Campanha": "60A5FA", "Ação": "34D399"}

    for ri, (_, row) in enumerate(df.iterrows(), 5):
        fill_bg = "F0FAFA" if ri % 2 == 0 else "FFFFFF"
        tipo_v  = str(row.get("tipo", ""))
        for ci, (_, campo, _) in enumerate(colunas, 1):
            val  = str(row.get(campo, "")) if pd.notna(row.get(campo, "")) else ""
            cell = ws.cell(row=ri, column=ci, value=val)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border    = borda
            if campo == "tipo" and tipo_v in tipo_bg:
                cell.fill = PatternFill("solid", fgColor=tipo_bg[tipo_v])
                cell.font = Font(name="Arial", size=9, bold=True, color=tipo_fg[tipo_v])
            else:
                cell.fill = PatternFill("solid", fgColor=fill_bg)
                cell.font = Font(name="Arial", size=9, color="1C2333")
        ws.row_dimensions[ri].height = 18

    tot = 5 + len(df)
    ws.merge_cells(f"A{tot}:C{tot}")
    ws[f"A{tot}"] = f"Total: {len(df)} registro(s)"
    ws[f"A{tot}"].font      = Font(name="Arial", bold=True, size=9, color="FFFFFF")
    ws[f"A{tot}"].fill      = PatternFill("solid", fgColor="09A49B")
    ws[f"A{tot}"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[tot].height = 18
    ws.freeze_panes = "A5"

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


# ── Exportador PDF ────────────────────────────────────────────────────────────
def gerar_pdf(df: pd.DataFrame) -> bytes:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                    Paragraph, Spacer, HRFlowable)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

    def hc(h):
        h = h.lstrip("#")
        return colors.Color(int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255)

    TEAL_C  = hc("09A49B"); DARK_C  = hc("0D7A73"); HEAD_C = hc("1C4058")
    EVEN_C  = hc("EEF9F8"); GRAY_C  = hc("64748B"); TEXT_C = hc("1C2333")
    CAMP_BG = hc("EFF6FF"); ACAO_BG = hc("F0FDF4")
    CAMP_FG = hc("1E40AF"); ACAO_FG = hc("166534")

    sWH  = ParagraphStyle("wh",  fontSize=7, fontName="Helvetica-Bold",    textColor=colors.white, alignment=TA_CENTER)
    sCEL = ParagraphStyle("cel", fontSize=7, fontName="Helvetica",         textColor=TEXT_C,       alignment=TA_CENTER, leading=9)
    sCMP = ParagraphStyle("cmp", fontSize=7, fontName="Helvetica-Bold",    textColor=CAMP_FG,      alignment=TA_CENTER)
    sACO = ParagraphStyle("aco", fontSize=7, fontName="Helvetica-Bold",    textColor=ACAO_FG,      alignment=TA_CENTER)
    sTIT = ParagraphStyle("tit", fontSize=16,fontName="Helvetica-Bold",    textColor=colors.white, alignment=TA_LEFT)
    sSUB = ParagraphStyle("sub", fontSize=8, fontName="Helvetica",         textColor=colors.white, alignment=TA_LEFT)
    sROD = ParagraphStyle("rod", fontSize=7, fontName="Helvetica-Oblique", textColor=GRAY_C,       alignment=TA_RIGHT)

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
                            leftMargin=12*mm, rightMargin=12*mm,
                            topMargin=12*mm,  bottomMargin=12*mm)
    story = []

    hdr = Table([[
        Paragraph("CampanhaOS", sTIT),
        Paragraph(
            f"Relatório de Campanhas &amp; Ações &nbsp;|&nbsp; "
            f"Gerado em: <b>{datetime.now().strftime('%d/%m/%Y %H:%M')}</b> &nbsp;|&nbsp; "
            f"Total: <b>{len(df)}</b> &nbsp;|&nbsp; "
            f"Campanhas: <b>{len(df[df['tipo']=='Campanha'])}</b> &nbsp;|&nbsp; "
            f"Ações: <b>{len(df[df['tipo']=='Ação'])}</b>", sSUB),
    ]], colWidths=[55*mm, None])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), DARK_C),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
        ("RIGHTPADDING", (0,0),(-1,-1), 8),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 4*mm))

    labels = ["ID","Tipo","Filiais","Nome","Laboratório","Ponto Focal",
              "Início","Fim","Dias","Reposição","Mg AL","Mg PE","Mg SE","Cadastrado em"]
    keys   = ["id","tipo","filiais","nome_acao","laboratorio","ponto_focal",
              "data_inicio","data_fim","duracao_dias","reposicao_por",
              "margem_AL","margem_PE","margem_SE","criado_em"]
    widths = [15,16,18,50,36,30,18,18,11,22,13,13,13,26]

    tdata = [[Paragraph(l, sWH) for l in labels]]
    for _, row in df.iterrows():
        linha = []
        for k in keys:
            v = str(row.get(k,"")) if pd.notna(row.get(k,"")) else ""
            if k == "tipo":
                linha.append(Paragraph(v, sCMP if v == "Campanha" else sACO))
            else:
                linha.append(Paragraph(v, sCEL))
        tdata.append(linha)

    tbl = Table(tdata, colWidths=[w*mm for w in widths], repeatRows=1)
    ts  = [
        ("BACKGROUND",    (0,0),(-1,0),  HEAD_C),
        ("TOPPADDING",    (0,0),(-1,0),  5),
        ("BOTTOMPADDING", (0,0),(-1,0),  5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, EVEN_C]),
        ("TOPPADDING",    (0,1),(-1,-1), 3),
        ("BOTTOMPADDING", (0,1),(-1,-1), 3),
        ("GRID",          (0,0),(-1,-1), 0.4, hc("D1FAF8")),
        ("LINEBELOW",     (0,0),(-1,0),  1.5, TEAL_C),
        ("BOX",           (0,0),(-1,-1), 1.5, DARK_C),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]
    for ri, (_, row) in enumerate(df.iterrows(), 1):
        bg = CAMP_BG if row.get("tipo") == "Campanha" else ACAO_BG
        ts.append(("BACKGROUND", (1,ri),(1,ri), bg))
    tbl.setStyle(TableStyle(ts))
    story.append(tbl)

    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=0.8, color=TEAL_C))
    story.append(Spacer(1, 1.5*mm))
    story.append(Paragraph("CampanhaOS · Gestão de Campanhas & Ações", sROD))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:0.5rem">
  <div style="width:36px;height:36px;background:linear-gradient(135deg,#09A49B,#0D7A73);
              border-radius:8px;display:flex;align-items:center;justify-content:center;
              font-size:1.1rem">⚡</div>
  <div>
    <div style="font-size:1.4rem;font-weight:800;color:#F8FAFC;line-height:1">CampanhaOS</div>
    <div style="font-size:0.72rem;color:#475569;font-weight:600;letter-spacing:0.08em;text-transform:uppercase">
      Gestão de Campanhas & Ações
    </div>
  </div>
</div>
<hr style="margin:0.8rem 0 1.5rem"/>
""", unsafe_allow_html=True)

tab_novo, tab_lista = st.tabs(["＋  Nova Campanha / Ação", "📋  Registros"])


# ══ TAB 1 — CADASTRO ══════════════════════════════════════════════════════════
with tab_novo:

    st.markdown("### Filiais participantes")
    st.markdown('<div style="font-size:0.78rem;color:#475569;margin-bottom:0.6rem">Selecione uma ou mais filiais</div>', unsafe_allow_html=True)
    col_al, col_pe, col_se, _ = st.columns([1,1,1,4])
    with col_al: filial_al = st.checkbox("AL — Alagoas",    value=True)
    with col_pe: filial_pe = st.checkbox("PE — Pernambuco")
    with col_se: filial_se = st.checkbox("SE — Sergipe")
    filiais_selecionadas = [f for f,v in [("AL",filial_al),("PE",filial_pe),("SE",filial_se)] if v]

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### Tipo de registro")
    tipo = st.radio("Tipo", options=["Campanha","Ação"], horizontal=True,
                    label_visibility="collapsed", key="tipo_radio")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Configurações")

    if tipo == "Ação":
        reposicao_por = st.selectbox("Reposição paga por", options=["Fornecedor","Empresa"], key="reposicao_sel")
    else:
        reposicao_por = ""
        st.markdown('<div style="padding:0.6rem 1rem;background:#0D0F14;border:1px solid #1E2A3A;border-radius:6px;color:#334155;font-size:0.82rem;display:inline-block">Reposição e margem não se aplicam para Campanha</div>', unsafe_allow_html=True)

    exibir_margem = (tipo == "Ação") and (reposicao_por == "Fornecedor")
    margem_vals   = {}

    if exibir_margem:
        if not filiais_selecionadas:
            st.markdown('<div style="padding:0.75rem;background:#1A1010;border:1px solid #3A1E1E;border-radius:6px;color:#EF4444;font-size:0.82rem;margin-top:0.5rem">⚠ Selecione ao menos uma filial acima para preencher as margens.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:0.78rem;color:#475569;margin:0.6rem 0 0.6rem">Margem média por filial participante</div>', unsafe_allow_html=True)
            mc = st.columns(len(filiais_selecionadas))
            for idx, filial in enumerate(filiais_selecionadas):
                with mc[idx]:
                    margem_vals[filial] = st.text_input(f"Margem {filial} (%)", placeholder="Ex: 18,5", key=f"margem_{filial}")
    elif tipo == "Ação" and reposicao_por == "Empresa":
        st.markdown('<div style="padding:0.6rem 1rem;background:#0D0F14;border:1px solid #1E2A3A;border-radius:6px;color:#334155;font-size:0.82rem;display:inline-block;margin-top:0.5rem">Margem não aplicável quando reposição é pela Empresa</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("form_campanha", clear_on_submit=True):
        st.markdown("### Identificação")
        c1, c2 = st.columns(2)
        with c1: nome_acao   = st.text_input("Nome da ação / campanha", placeholder="Ex: Verão 2025 — Linha Infantil")
        with c2: laboratorio = st.text_input("Laboratório / Fornecedor", placeholder="Ex: Grupo Hypermarcas")
        ponto_focal = st.text_input("Ponto focal (fornecedor)", placeholder="Ex: João Silva")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Período")
        d1, d2 = st.columns(2)
        with d1: data_inicio = st.date_input("Data de início", value=date.today(), format="DD/MM/YYYY")
        with d2: data_fim    = st.date_input("Data de fim",    value=date.today(), format="DD/MM/YYYY")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Observações")
        observacoes = st.text_area("Observações", placeholder="Descreva detalhes adicionais, condicionais, metas...", height=100, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✓  Cadastrar registro", type="primary", use_container_width=True)

    if submitted:
        if not filiais_selecionadas:
            st.error("Selecione ao menos uma filial participante.")
        elif not nome_acao.strip():
            st.error("Preencha o nome da ação / campanha.")
        elif not laboratorio.strip():
            st.error("Preencha o laboratório / fornecedor.")
        else:
            df_atual = carregar_dados()
            nova = {
                "id":            proximo_id(df_atual),
                "tipo":          tipo,
                "filiais":       ", ".join(filiais_selecionadas),
                "nome_acao":     nome_acao.strip(),
                "laboratorio":   laboratorio.strip(),
                "ponto_focal":   ponto_focal.strip(),
                "data_inicio":   data_inicio.strftime("%d/%m/%Y"),
                "data_fim":      data_fim.strftime("%d/%m/%Y"),
                "duracao_dias":  str((data_fim - data_inicio).days + 1),
                "reposicao_por": reposicao_por,
                "margem_AL":     margem_vals.get("AL","").strip(),
                "margem_PE":     margem_vals.get("PE","").strip(),
                "margem_SE":     margem_vals.get("SE","").strip(),
                "observacoes":   observacoes.strip(),
                "criado_em":     datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            salvar_linha(nova)
            st.success(f"✓ Registro **{nova['id']}** cadastrado com sucesso!")


# ══ TAB 2 — LISTAGEM ══════════════════════════════════════════════════════════
with tab_lista:

    df = carregar_dados()

    if df.empty:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#334155">
          <div style="font-size:2rem;margin-bottom:0.5rem">📭</div>
          <div style="font-weight:700">Nenhum registro ainda</div>
          <div style="font-size:0.85rem;margin-top:0.25rem">Cadastre a primeira campanha na aba ao lado</div>
        </div>""", unsafe_allow_html=True)
    else:
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Total de registros",  len(df))
        m2.metric("Campanhas",           len(df[df["tipo"]=="Campanha"]))
        m3.metric("Ações",               len(df[df["tipo"]=="Ação"]))
        m4.metric("Fornecedores únicos", df["laboratorio"].nunique())

        st.markdown("<br>", unsafe_allow_html=True)

        cf1,cf2,cf3 = st.columns(3)
        with cf1: filtro_tipo   = st.selectbox("Filtrar por tipo",        ["Todos","Campanha","Ação"])
        with cf2:
            labs = ["Todos"] + sorted(df["laboratorio"].dropna().unique().tolist())
            filtro_lab = st.selectbox("Filtrar por laboratório", labs)
        with cf3: filtro_filial = st.selectbox("Filtrar por filial",      ["Todas","AL","PE","SE"])

        cf4,cf5,_ = st.columns(3)
        with cf4:
            focais = ["Todos"] + sorted(df["ponto_focal"].dropna().replace("",pd.NA).dropna().unique().tolist())
            filtro_focal = st.selectbox("Filtrar por ponto focal", focais)
        with cf5: filtro_busca = st.text_input("Buscar por nome", placeholder="Digite parte do nome...")

        df_view = df.copy()
        if filtro_tipo   != "Todos":  df_view = df_view[df_view["tipo"] == filtro_tipo]
        if filtro_lab    != "Todos":  df_view = df_view[df_view["laboratorio"] == filtro_lab]
        if filtro_filial != "Todas":  df_view = df_view[df_view["filiais"].str.contains(filtro_filial, na=False)]
        if filtro_focal  != "Todos":  df_view = df_view[df_view["ponto_focal"] == filtro_focal]
        if filtro_busca:              df_view = df_view[df_view["nome_acao"].str.contains(filtro_busca, case=False, na=False)]

        st.markdown(f"<div style='color:#475569;font-size:0.8rem;margin-bottom:0.5rem'>{len(df_view)} registro(s) encontrado(s)</div>", unsafe_allow_html=True)

        cols_exib = {
            "id":"ID","tipo":"Tipo","filiais":"Filiais","nome_acao":"Nome",
            "laboratorio":"Laboratório","ponto_focal":"Ponto Focal",
            "data_inicio":"Início","data_fim":"Fim","duracao_dias":"Duração (dias)",
            "reposicao_por":"Reposição","margem_AL":"Margem AL (%)","margem_PE":"Margem PE (%)",
            "margem_SE":"Margem SE (%)","criado_em":"Cadastrado em",
        }
        st.dataframe(df_view[list(cols_exib.keys())].rename(columns=cols_exib),
                     use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Exportar registros filtrados")
        st.markdown('<div style="font-size:0.78rem;color:#475569;margin-bottom:0.8rem">Escolha o formato de exportação</div>', unsafe_allow_html=True)

        exp1, exp2, exp3 = st.columns(3)
        ts = datetime.now().strftime("%d%m%Y_%H%M")

        with exp1:
            st.markdown("""<div style="background:#161B27;border:1px solid #1E2A3A;border-radius:8px;padding:1rem 1.25rem;margin-bottom:0.5rem">
              <div style="font-size:0.75rem;font-weight:700;color:#34D399;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.3rem">📄 CSV</div>
              <div style="font-size:0.8rem;color:#64748B">Formato simples, compatível com qualquer planilha</div>
            </div>""", unsafe_allow_html=True)
            st.download_button("⬇  Baixar CSV", data=df_view.to_csv(index=False).encode("utf-8"),
                               file_name=f"campanhas_{ts}.csv", mime="text/csv", use_container_width=True)

        with exp2:
            st.markdown("""<div style="background:#161B27;border:1px solid #1E2A3A;border-radius:8px;padding:1rem 1.25rem;margin-bottom:0.5rem">
              <div style="font-size:0.75rem;font-weight:700;color:#60A5FA;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.3rem">📊 Excel (.xlsx)</div>
              <div style="font-size:0.8rem;color:#64748B">Relatório formatado com cores, cabeçalho e totais</div>
            </div>""", unsafe_allow_html=True)
            st.download_button("⬇  Baixar Excel", data=gerar_excel(df_view),
                               file_name=f"campanhas_{ts}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)

        with exp3:
            st.markdown("""<div style="background:#161B27;border:1px solid #1E2A3A;border-radius:8px;padding:1rem 1.25rem;margin-bottom:0.5rem">
              <div style="font-size:0.75rem;font-weight:700;color:#F472B6;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.3rem">📑 PDF</div>
              <div style="font-size:0.8rem;color:#64748B">Relatório pronto para impressão e compartilhamento</div>
            </div>""", unsafe_allow_html=True)
            st.download_button("⬇  Baixar PDF", data=gerar_pdf(df_view),
                               file_name=f"campanhas_{ts}.pdf", mime="application/pdf",
                               use_container_width=True)