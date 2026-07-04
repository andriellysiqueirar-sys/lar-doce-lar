import streamlit as st
import os
import base64
import json
import qrcode
import io as io_module
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io

st.set_page_config(page_title="Lar doce Lar", page_icon="🏠", layout="centered")

SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]

if "google_credentials" in st.secrets:
    credenciais_dict = json.loads(st.secrets["google_credentials"])
    creds = Credentials.from_service_account_info(credenciais_dict, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
else:
    st.error("Credenciais não encontradas.")
    st.stop()

PASTA_DRIVE_ID = "1uM5fKwOJyo418E-Te3EpyPuLMvGpVdQH"
PLANILHA_ID    = "1la4BUnm9du32LDk0m1FcQay1HxFaYjJfCYbrDLH9rg4"
ABA_DADOS      = "Planilha"
NOME_IMAGEM    = "lar_doce_lar.png"
IMAGEM_NAZARE  = "Nazare.jpg"

LISTA_MESES = [
    "Janeiro/2026","Fevereiro/2026","Março/2026","Abril/2026","Maio/2026","Junho/2026",
    "Julho/2026","Agosto/2026","Setembro/2026","Outubro/2026","Novembro/2026","Dezembro/2026"
]
MAPA_MESES = {
    "Janeiro/2026":"2026.01","Fevereiro/2026":"2026.02","Março/2026":"2026.03",
    "Abril/2026":"2026.04","Maio/2026":"2026.05","Junho/2026":"2026.06",
    "Julho/2026":"2026.07","Agosto/2026":"2026.08","Setembro/2026":"2026.09",
    "Outubro/2026":"2026.10","Novembro/2026":"2026.11","Dezembro/2026":"2026.12"
}

INTERNET_FIXO = 55.00
PIX_CHAVE     = "08974285959"
PIX_NOME      = "Andrielly Cristina"
PIX_CIDADE    = "Araucaria"
PIX_DESCRICAO = "Lar doce Lar"

USUARIOS = {
    "Admin":   {"senha": "2311", "perfil": "admin"},
    "Vicente": {"senha": "1103", "perfil": "familia"},
    "Amoreco": {"senha": "1812", "perfil": "marido"}
}

for k, v in {"logado": False, "perfil": None, "usuario_atual": None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Índice do mês atual (0-based)
MES_ATUAL_IDX = datetime.now().month - 1

def obter_imagem_base64(caminho):
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

img_familia_b64 = obter_imagem_base64(NOME_IMAGEM)
img_nazare_b64  = obter_imagem_base64(IMAGEM_NAZARE)

background_style = f"""
    background: linear-gradient(rgba(232,138,122,0.83),rgba(232,138,122,0.83)),
                url("data:image/png;base64,{img_familia_b64}");
    background-size:100% auto;background-position:top center;
    background-repeat:no-repeat;background-attachment:fixed;
""" if img_familia_b64 else "background-color:#E88A7A;"

nazare_style = f"""
    background-image:url("data:image/jpeg;base64,{img_nazare_b64}");
    background-size:cover;background-position:center;
    background-blend-mode:overlay;background-color:rgba(255,255,255,0.55);
""" if img_nazare_b64 else "background-color:#FDF5F3;"

st.markdown(f"""
<style>
.stApp {{ {background_style} color:#2F1F1D; }}
.stTextInput>div>div>input,.stSelectbox>div>div,.stNumberInput>div>div>input {{
    background-color:#FCEBE8!important;color:#2F1F1D!important;
    border:1px solid #D16B5B!important;border-radius:8px!important; }}
label,.stMarkdown,p {{ color:#3E2723!important;font-weight:500; }}
.botao-sair button {{
    background-color:#3E2723!important;color:#FCEBE8!important;
    border-radius:8px!important;border:2px solid #FCEBE8!important;font-weight:bold!important;width:100%; }}
div.stDownloadButton>button {{
    background-color:#2E7D32!important;color:#FFFFFF!important;
    border-radius:8px!important;border:none!important;width:100%;font-weight:bold; }}
div.stButton>button {{
    background-color:#3E2723!important;color:#FCEBE8!important;
    border-radius:8px!important;border:none!important;font-weight:bold;width:100%; }}
.destaque-box {{
    background-color:#FDF5F3;padding:22px;border-radius:12px;
    box-shadow:0px 4px 15px rgba(0,0,0,0.1);border:2px solid #D16B5B;margin-bottom:20px; }}
.caixa-nazare-container {{
    {nazare_style} padding:22px;border-radius:12px;
    box-shadow:0px 4px 15px rgba(0,0,0,0.1);border:2px solid #D16B5B;margin-bottom:20px; }}
.grid-nazare {{ display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-top:15px; }}
.item-nazare {{ flex:1;min-width:120px;text-align:center; }}
.label-nazare {{ color:#21100B!important;font-size:14px;font-weight:bold;margin-bottom:5px;text-shadow:0px 0px 4px rgba(255,255,255,0.8); }}
.val-nazare {{ color:#000000!important;font-size:22px;font-weight:bold;text-shadow:0px 0px 5px rgba(255,255,255,0.9); }}
.erro-grande {{ text-align:center;color:#C62828;font-size:14px;font-weight:bold;padding:10px;
    background-color:#FFEBEE;border-radius:8px;border:1px solid #FFCDD2;margin-top:5px; }}
.erro-grande span {{ font-size:32px;display:block;margin-bottom:2px; }}
[data-testid="stToolbar"] {{ display:none!important; }}
#MainMenu {{ visibility:hidden; }}
header {{ visibility:hidden; }}
footer {{ visibility:hidden; }}
[data-testid="stDecoration"] {{ display:none; }}
[data-testid="stStatusWidget"] {{ display:none!important; }}
.stAppDeployButton {{ display:none!important; }}
[data-testid="stExpander"] {{
    background-color:#FDF5F3!important;border:2px solid #D16B5B!important;border-radius:12px!important; }}
[data-testid="stExpander"] summary {{
    background-color:#FDF5F3!important;border-radius:12px!important;font-weight:bold;color:#3E2723!important; }}
[data-testid="stExpander"]>div>div {{
    background-color:#FDF5F3!important;border-radius:0 0 12px 12px!important;padding:10px!important; }}
[data-testid="stMetric"] {{
    background-color:#FCEBE8!important;border-radius:10px!important;
    padding:10px 14px!important;border:1px solid #D16B5B!important; }}
[data-testid="stMetricLabel"] p {{ color:#3E2723!important;font-weight:bold; }}
[data-testid="stMetricValue"] {{ color:#2F1F1D!important; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# PIX
# ==========================================
def _crc16(data):
    crc = 0xFFFF
    for char in data:
        crc ^= ord(char) << 8
        for _ in range(8):
            crc = (crc << 1) ^ 0x1021 if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return format(crc, '04X')

def _emv(id_, value):
    return f"{id_}{len(value):02d}{value}"

def gerar_payload_pix(chave, nome, cidade, valor, descricao):
    valor_str = f"{valor:.2f}"
    gui = _emv("00", "br.gov.bcb.pix")
    chave_field = _emv("01", chave)
    desc_field = _emv("02", descricao[:72])
    merchant_account = _emv("26", gui + chave_field + desc_field)
    payload = (
        _emv("00", "01") + merchant_account + _emv("52", "0000")
        + _emv("53", "986") + _emv("54", valor_str) + _emv("58", "BR")
        + _emv("59", nome[:25]) + _emv("60", cidade[:15])
        + _emv("62", _emv("05", "***")) + "6304"
    )
    return payload + _crc16(payload)

def gerar_qrcode_imagem(valor):
    payload = gerar_payload_pix(PIX_CHAVE, PIX_NOME, PIX_CIDADE, valor, PIX_DESCRICAO)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=6, border=2)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#3E2723", back_color="white")
    buf = io_module.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ==========================================
# SHEETS
# ==========================================
CABECALHO = [
    "Mes_Ano","Valor_Luz","Total_kWh","Leitura_Ant","Leitura_At",
    "Valor_Agua","Internet_Fixo","Parte_Amoreco_Luz","Parte_Vicente_Luz",
    "Parte_Amoreco_Agua","Parte_Vicente_Agua","Parte_Amoreco_Internet",
    "Parte_Vicente_Internet","Total_Amoreco","Total_Vicente"
]

def garantir_cabecalho_sheets():
    res = sheets_service.spreadsheets().values().get(
        spreadsheetId=PLANILHA_ID, range=f"{ABA_DADOS}!A1:O1").execute()
    vals = res.get('values', [])
    if not vals or vals[0][0] != "Mes_Ano":
        sheets_service.spreadsheets().values().update(
            spreadsheetId=PLANILHA_ID, range=f"{ABA_DADOS}!A1",
            valueInputOption="RAW", body={"values": [CABECALHO]}).execute()

def buscar_linha_mes(prefixo):
    res = sheets_service.spreadsheets().values().get(
        spreadsheetId=PLANILHA_ID, range=f"{ABA_DADOS}!A:A").execute()
    for i, linha in enumerate(res.get('values', [])):
        if linha and linha[0] == prefixo:
            return i + 1
    return None

def salvar_dados_sheets(prefixo, val_luz, total_kwh, leitura_ant, leitura_at, val_agua):
    garantir_cabecalho_sheets()
    if total_kwh > 0:
        preco_kwh = val_luz / total_kwh
        parte_amoreco_luz = round(preco_kwh * (leitura_at - leitura_ant), 2)
    else:
        parte_amoreco_luz = 0.0
    parte_vicente_luz = round(val_luz - parte_amoreco_luz, 2)
    parte_agua_cada   = round(val_agua / 2, 2)
    total_amoreco     = round(parte_amoreco_luz + parte_agua_cada + INTERNET_FIXO, 2)
    total_vicente     = round(parte_vicente_luz + parte_agua_cada + INTERNET_FIXO, 2)
    nova_linha = [[
        prefixo, val_luz, total_kwh, leitura_ant, leitura_at, val_agua, INTERNET_FIXO,
        parte_amoreco_luz, parte_vicente_luz, parte_agua_cada, parte_agua_cada,
        INTERNET_FIXO, INTERNET_FIXO, total_amoreco, total_vicente
    ]]
    linha = buscar_linha_mes(prefixo)
    if linha:
        sheets_service.spreadsheets().values().update(
            spreadsheetId=PLANILHA_ID,
            range=f"{ABA_DADOS}!A{linha}:O{linha}",
            valueInputOption="RAW", body={"values": nova_linha}).execute()
    else:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=PLANILHA_ID, range=f"{ABA_DADOS}!A:O",
            valueInputOption="RAW", insertDataOption="INSERT_ROWS",
            body={"values": nova_linha}).execute()

def carregar_dados_sheets(prefixo):
    try:
        res = sheets_service.spreadsheets().values().get(
            spreadsheetId=PLANILHA_ID, range=f"{ABA_DADOS}!A:O").execute()
        for linha in res.get('values', []):
            if linha and linha[0] == prefixo:
                def sf(v):
                    try: return float(str(v).replace(',','.'))
                    except: return 0.0
                return {
                    "val_luz":                sf(linha[1])  if len(linha)>1  else 0.0,
                    "total_kwh":              sf(linha[2])  if len(linha)>2  else 0.0,
                    "leitura_ant":            sf(linha[3])  if len(linha)>3  else 0.0,
                    "leitura_at":             sf(linha[4])  if len(linha)>4  else 0.0,
                    "val_agua":               sf(linha[5])  if len(linha)>5  else 0.0,
                    "internet_fixo":          sf(linha[6])  if len(linha)>6  else INTERNET_FIXO,
                    "parte_amoreco_luz":      sf(linha[7])  if len(linha)>7  else 0.0,
                    "parte_vicente_luz":      sf(linha[8])  if len(linha)>8  else 0.0,
                    "parte_amoreco_agua":     sf(linha[9])  if len(linha)>9  else 0.0,
                    "parte_vicente_agua":     sf(linha[10]) if len(linha)>10 else 0.0,
                    "parte_amoreco_internet": sf(linha[11]) if len(linha)>11 else INTERNET_FIXO,
                    "parte_vicente_internet": sf(linha[12]) if len(linha)>12 else INTERNET_FIXO,
                    "total_amoreco":          sf(linha[13]) if len(linha)>13 else 0.0,
                    "total_vicente":          sf(linha[14]) if len(linha)>14 else 0.0,
                }
    except Exception as e:
        st.warning(f"Erro ao carregar planilha: {e}")
    return None

def buscar_leitura_anterior_sheets(mes):
    try:
        idx = LISTA_MESES.index(mes)
        if idx > 0:
            d = carregar_dados_sheets(MAPA_MESES[LISTA_MESES[idx-1]])
            if d: return d["leitura_at"]
    except: pass
    return 0.0

# ==========================================
# DRIVE
# ==========================================
def buscar_arquivo_no_drive(nome):
    res = drive_service.files().list(
        q=f"'{PASTA_DRIVE_ID}' in parents and name='{nome}' and trashed=false",
        fields="files(id)").execute()
    arqs = res.get('files', [])
    return arqs[0]['id'] if arqs else None

def upload_documento_drive(arquivo_st, nome_final):
    file_id = buscar_arquivo_no_drive(nome_final)
    mem = io.BytesIO(arquivo_st.getvalue())
    media = MediaIoBaseUpload(mem, mimetype=arquivo_st.type, resumable=False)
    if file_id:
        drive_service.files().update(fileId=file_id, media_body=media).execute()
    else:
        drive_service.files().create(
            body={'name': nome_final, 'parents': [PASTA_DRIVE_ID]},
            media_body=media).execute()

def baixar_arquivo_do_drive(file_id):
    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, drive_service.files().get_media(fileId=file_id))
    done = False
    while not done: _, done = dl.next_chunk()
    buf.seek(0)
    return buf.read()

def listar_todos_arquivos_drive():
    try:
        res = drive_service.files().list(
            q=f"'{PASTA_DRIVE_ID}' in parents and trashed=false",
            fields="files(name)").execute()
        return [a['name'] for a in res.get('files', [])]
    except: return []

# ==========================================
# EXPLICATIVO DA LUZ
# ==========================================
def exibir_explicativo_luz(dados, eh_marido):
    val_luz = dados["val_luz"]; total_kwh = dados["total_kwh"]
    leitura_ant = dados["leitura_ant"]; leitura_at = dados["leitura_at"]
    if total_kwh == 0:
        st.info("Dados insuficientes."); return
    preco_kwh = val_luz / total_kwh
    consumo_amoreco = leitura_at - leitura_ant
    consumo_vicente = total_kwh - consumo_amoreco
    if eh_marido:
        meu_consumo = consumo_amoreco
        minha_parte = dados["parte_amoreco_luz"]
        quem_sou = "Dry / Rafa"
    else:
        meu_consumo = consumo_vicente
        minha_parte = dados["parte_vicente_luz"]
        quem_sou = "Gaby / Mandy"

    st.markdown("**⚡ Dados Gerais da Fatura COPEL**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Valor total", f"R$ {val_luz:.2f}")
        st.metric("📊 Consumo total da casa", f"{total_kwh:.1f} kWh")
    with col2:
        st.metric("💡 Preço por kWh", f"R$ {preco_kwh:.4f}")
    st.markdown("---")

    st.markdown("**📊 Divisão do Consumo (kWh)**")
    col3, col4 = st.columns(2)
    with col3:
        st.metric("⚡ Consumo Dry/Rafa", f"{consumo_amoreco:.1f} kWh",
                  help=f"Leitura: {leitura_ant:.1f} → {leitura_at:.1f}")
    with col4:
        st.metric("⚡ Consumo Gaby/Mandy", f"{consumo_vicente:.1f} kWh",
                  help="Restante da casa (total − Dry/Rafa)")
    st.markdown("---")

    st.markdown(f"**🧮 Seu Cálculo ({quem_sou})**")
    st.markdown(f"📐 **Conta:** {meu_consumo:.1f} kWh × R$ {preco_kwh:.4f}/kWh")
    st.success(f"💰 Sua parte da luz: **R$ {minha_parte:.2f}**")

# ==========================================
# LOGIN
# ==========================================
if not st.session_state.logado:
    st.markdown("<div style='margin-top:130px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;margin-top:15px;'>🏠 Lar doce Lar</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#3E2723;'>Insira suas credenciais para acessar o portal</p>", unsafe_allow_html=True)
    usuario_input = st.text_input("Usuário")
    senha_input   = st.text_input("Senha", type="password")
    if st.button("Entrar", use_container_width=True):
        if usuario_input in USUARIOS and USUARIOS[usuario_input]["senha"] == senha_input:
            st.session_state.logado        = True
            st.session_state.perfil        = USUARIOS[usuario_input]["perfil"]
            st.session_state.usuario_atual = usuario_input
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

# ==========================================
# SISTEMA
# ==========================================
else:
    col_topo_1, col_topo_2 = st.columns([8, 2])
    with col_topo_2:
        st.markdown('<div class="botao-sair">', unsafe_allow_html=True)
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.session_state.perfil = None
            st.session_state.usuario_atual = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center;margin-top:15px;'>🏠 Lar doce Lar</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #D16B5B;'>", unsafe_allow_html=True)

    # ADMIN
    if st.session_state.perfil == "admin":
        st.subheader("⚙️ Painel de Administração")
        aba_subir, aba_historico = st.tabs(["🚀 Lançar Valores e Contas", "📊 Arquivos no Drive"])

        with aba_subir:
            mes_ano      = st.selectbox("Selecione o Mês/Ano de referência:", LISTA_MESES, index=MES_ATUAL_IDX)
            prefixo_data = MAPA_MESES[mes_ano]

            with st.spinner("Carregando dados do mês..."):
                dados_mes = carregar_dados_sheets(prefixo_data)

            if dados_mes:
                luz_fatura  = dados_mes["val_luz"]
                kwh_fatura  = dados_mes["total_kwh"]
                medidor_ant = dados_mes["leitura_ant"]
                leitura_at  = dados_mes["leitura_at"]
                agua_fatura = dados_mes["val_agua"]
            else:
                luz_fatura = kwh_fatura = leitura_at = agua_fatura = 0.0
                medidor_ant = buscar_leitura_anterior_sheets(mes_ano)

            st.markdown("#### ⚡ Fatura de Energia - COPEL")
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                val_luz   = st.number_input("Valor Total da Fatura Copel (R$)", min_value=0.0, step=0.01, value=luz_fatura, key=f"adm_luz_{prefixo_data}")
            with col_l2:
                total_kwh = st.number_input("Consumo Total de kW/h", min_value=0.0, step=0.1, value=kwh_fatura, key=f"adm_kwh_{prefixo_data}")

            st.markdown("#### 🔍 Medidor Interno (Dry / Rafa)")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                leitura_ant_input = st.number_input("Leitura Anterior", min_value=0.0, step=0.1, value=medidor_ant, key=f"adm_lant_{prefixo_data}")
            with col_m2:
                leitura_at_input  = st.number_input("Leitura Atual", min_value=0.0, step=0.1, value=leitura_at, key=f"adm_lat_{prefixo_data}")

            st.markdown("#### 💧 Fatura de Água SANEPAR")
            val_agua = st.number_input("Valor Total da Conta de Água (R$)", min_value=0.0, step=0.01, value=agua_fatura, key=f"adm_agua_{prefixo_data}")
            st.markdown(f"#### 🌐 Internet — Valor fixo: **R$ {INTERNET_FIXO:.2f}** por família")

            st.markdown("---")
            st.markdown("#### 📂 Upload das Faturas Originais")
            col_up1, col_up2 = st.columns(2)
            with col_up1:
                arquivo_luz  = st.file_uploader("📄 Fatura da Luz (Copel)",    type=["pdf","jpg","jpeg","png"], key="up_fatura_luz")
            with col_up2:
                arquivo_agua = st.file_uploader("📄 Fatura da Água (Sanepar)", type=["pdf","jpg","jpeg","png"], key="up_fatura_agua")

            st.markdown("---")
            st.markdown("#### 🧾 Upload dos Comprovantes de Pagamento")
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                comp_luz  = st.file_uploader("✅ Comprovante da Luz",      type=["pdf","jpg","jpeg","png","txt"], key="up_comp_luz")
            with col_c2:
                comp_agua = st.file_uploader("✅ Comprovante da Água",     type=["pdf","jpg","jpeg","png","txt"], key="up_comp_agua")
            with col_c3:
                comp_net  = st.file_uploader("✅ Comprovante da Internet", type=["pdf","jpg","jpeg","png","txt"], key="up_comp_net")

            st.markdown("---")
            if st.button("💾 Salvar e Publicar no Sistema", use_container_width=True):
                with st.spinner("Salvando dados..."):
                    try:
                        salvar_dados_sheets(prefixo_data, val_luz, total_kwh, leitura_ant_input, leitura_at_input, val_agua)
                        for arq, sufixo in [(arquivo_luz,"luz"),(arquivo_agua,"água"),(comp_luz,"comp_luz"),(comp_agua,"comp_água"),(comp_net,"comp_internet")]:
                            if arq is not None:
                                upload_documento_drive(arq, f"{prefixo_data} - {sufixo}{os.path.splitext(arq.name)[1].lower()}")
                        st.success(f"✅ Dados de {mes_ano} salvos com sucesso!")
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar: {e}")

        with aba_historico:
            with st.spinner("Buscando arquivos no Drive..."):
                arquivos = listar_todos_arquivos_drive()
                if arquivos:
                    for arq in sorted(arquivos): st.write(f"📁 {arq}")
                else:
                    st.info("Nenhum arquivo encontrado.")

    # FAMÍLIA
    elif st.session_state.perfil in ["familia", "marido"]:
        eh_marido = st.session_state.perfil == "marido"
        if eh_marido:
            st.markdown(f"<h3 style='text-align:center;color:#3E2723;'>👋 Bem-vindo ao seu Espaço, {st.session_state.usuario_atual}!</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align:center;color:#3E2723;'>👋 Bem-vindo ao Espaço da Família!</h3>", unsafe_allow_html=True)

        mes_selecionado = st.selectbox("Selecione o Mês/Ano:", LISTA_MESES, index=MES_ATUAL_IDX)
        codigo_mes      = MAPA_MESES[mes_selecionado]

        with st.spinner("Carregando valores..."):
            dados = carregar_dados_sheets(codigo_mes)

        if dados:
            if eh_marido:
                parte_luz      = dados["parte_amoreco_luz"]
                parte_agua     = dados["parte_amoreco_agua"]
                parte_internet = dados["parte_amoreco_internet"]
                total_a_pagar  = dados["total_amoreco"]
                titulo_detalhe = "📝 Detalhamento dos Gastos (Dry / Rafa)"
            else:
                parte_luz      = dados["parte_vicente_luz"]
                parte_agua     = dados["parte_vicente_agua"]
                parte_internet = dados["parte_vicente_internet"]
                total_a_pagar  = dados["total_vicente"]
                titulo_detalhe = "📝 Detalhamento dos Gastos (Gaby / Mandy)"
        else:
            parte_luz = parte_agua = parte_internet = total_a_pagar = 0.0
            titulo_detalhe = "📝 Detalhamento dos Gastos"

        # RESUMO
        st.markdown(f"""
            <div class='destaque-box'>
                <h3 style='margin-top:0;color:#3E2723;'>💰 Resumo do Mês: {mes_selecionado}</h3>
                <p style='font-size:19px;'><b>Total a Pagar:</b>
                <span style='color:#2E7D32;font-size:24px;font-weight:bold;'>R$ {total_a_pagar:.2f}</span></p>
                <hr style='border:0.5px solid #D16B5B;'>
                <p style='font-size:16px;margin-bottom:0;'>🔑 <b>Chave PIX:</b>
                <code style='font-size:15px;background-color:#EEA296;color:#3E2723;padding:4px 8px;border-radius:4px;'>{PIX_CHAVE}</code></p>
            </div>
        """, unsafe_allow_html=True)

        # QR CODE + PIX COPIA E COLA
        if total_a_pagar > 0:
            st.markdown("<h4 style='text-align:center;'>📱 QR Code PIX — Escaneie para Pagar</h4>", unsafe_allow_html=True)
            qr_bytes    = gerar_qrcode_imagem(total_a_pagar)
            payload_pix = gerar_payload_pix(PIX_CHAVE, PIX_NOME, PIX_CIDADE, total_a_pagar, PIX_DESCRICAO)

            col_qr1, col_qr2, col_qr3 = st.columns([1, 2, 1])
            with col_qr2:
                st.image(qr_bytes, caption=f"R$ {total_a_pagar:.2f} → {PIX_CHAVE}", use_container_width=True)

            st.markdown("<p style='text-align:center;font-size:14px;color:#3E2723;margin-bottom:4px;'>📋 <b>PIX Copia e Cola</b> — selecione e copie o código abaixo:</p>", unsafe_allow_html=True)
            st.text_area("", value=payload_pix, height=90, key=f"pix_payload_{codigo_mes}", label_visibility="collapsed")
            st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
        else:
            st.info("QR Code disponível após o Admin lançar os valores do mês.")

        # DETALHAMENTO
        st.markdown(f"""
            <div class="caixa-nazare-container">
                <h4 style="margin-top:0;color:#21100B;text-shadow:0px 0px 4px rgba(255,255,255,0.8);">{titulo_detalhe}</h4>
                <div class="grid-nazare">
                    <div class="item-nazare">
                        <div class="label-nazare">⚡ Energia Copel</div>
                        <div class="val-nazare">R$ {parte_luz:.2f}</div>
                    </div>
                    <div class="item-nazare">
                        <div class="label-nazare">💧 Água Sanepar</div>
                        <div class="val-nazare">R$ {parte_agua:.2f}</div>
                    </div>
                    <div class="item-nazare">
                        <div class="label-nazare">🌐 Internet</div>
                        <div class="val-nazare">R$ {parte_internet:.2f}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # EXPLICATIVO
        if dados and dados["total_kwh"] > 0:
            with st.expander("💡 Como foi calculado o valor da luz? Clique para ver"):
                exibir_explicativo_luz(dados, eh_marido)

        # FATURAS
        st.markdown("<h4 style='text-align:center;margin-top:25px;'>📂 Baixar Faturas Oficiais</h4>", unsafe_allow_html=True)
        col_down_1, col_down_2 = st.columns(2)
        id_luz=None; nome_luz=None
        for ext in ['.pdf','.jpg','.jpeg','.png']:
            id_luz = buscar_arquivo_no_drive(f"{codigo_mes} - luz{ext}")
            if id_luz: nome_luz=f"{codigo_mes} - luz{ext}"; break
        with col_down_1:
            if id_luz:
                st.download_button("📥 Fatura Luz", data=baixar_arquivo_do_drive(id_luz), file_name=nome_luz, mime="application/octet-stream")
            else:
                st.markdown('<div class="erro-grande"><span>❌</span>Fatura de Luz<br>não disponível</div>', unsafe_allow_html=True)

        id_agua=None; nome_agua=None
        for ext in ['.pdf','.jpg','.jpeg','.png']:
            id_agua = buscar_arquivo_no_drive(f"{codigo_mes} - água{ext}")
            if id_agua: nome_agua=f"{codigo_mes} - água{ext}"; break
        with col_down_2:
            if id_agua:
                st.download_button("📥 Fatura Água", data=baixar_arquivo_do_drive(id_agua), file_name=nome_agua, mime="application/octet-stream")
            else:
                st.markdown('<div class="erro-grande"><span>❌</span>Fatura de Água<br>não disponível</div>', unsafe_allow_html=True)

        # COMPROVANTES
        st.markdown("<hr style='border:0.5px dashed #D16B5B;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align:center;'>🧾 Comprovantes de Quitação</h4>", unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)

        id_cl=None; nome_cl=None
        for ext in ['.pdf','.jpg','.jpeg','.png','.txt']:
            id_cl = buscar_arquivo_no_drive(f"{codigo_mes} - comp_luz{ext}")
            if id_cl: nome_cl=f"{codigo_mes} - comp_luz{ext}"; break
        with col_c1:
            if id_cl:
                st.download_button("🧾 Comp. Luz", data=baixar_arquivo_do_drive(id_cl), file_name=nome_cl)
            else:
                st.markdown('<div class="erro-grande"><span>❌</span>Comp. Luz<br>ausente</div>', unsafe_allow_html=True)

        id_ca=None; nome_ca=None
        for ext in ['.pdf','.jpg','.jpeg','.png','.txt']:
            id_ca = buscar_arquivo_no_drive(f"{codigo_mes} - comp_água{ext}")
            if id_ca: nome_ca=f"{codigo_mes} - comp_água{ext}"; break
        with col_c2:
            if id_ca:
                st.download_button("🧾 Comp. Água", data=baixar_arquivo_do_drive(id_ca), file_name=nome_ca)
            else:
                st.markdown('<div class="erro-grande"><span>❌</span>Comp. Água<br>ausente</div>', unsafe_allow_html=True)

        id_cn=None; nome_cn=None
        for ext in ['.pdf','.jpg','.jpeg','.png','.txt']:
            id_cn = buscar_arquivo_no_drive(f"{codigo_mes} - comp_internet{ext}")
            if id_cn: nome_cn=f"{codigo_mes} - comp_internet{ext}"; break
        with col_c3:
            if id_cn:
                st.download_button("🧾 Comp. Net", data=baixar_arquivo_do_drive(id_cn), file_name=nome_cn)
            else:
                st.markdown('<div class="erro-grande"><span>❌</span>Comp. Internet<br>ausente</div>', unsafe_allow_html=True)

