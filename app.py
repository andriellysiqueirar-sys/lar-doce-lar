import streamlit as st
import os
import base64
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Lar doce Lar",
    page_icon="🏠",
    layout="centered"
)

# --- CONEXÃO COM O GOOGLE DRIVE ---
if "google_credentials" in st.secrets:
    credenciais_dict = json.loads(st.secrets["google_credentials"])
    creds = Credentials.from_service_account_info(credenciais_dict, scopes=["https://www.googleapis.com/auth/drive"])
    drive_service = build('drive', 'v3', credentials=creds)
else:
    st.error("Erro: As credenciais do Google Drive não foram encontradas nos Secrets do Streamlit.")
    st.stop()

# ID DA PASTA DO DRIVE
PASTA_DRIVE_ID = "1uM5fKwOJyo418E-Te3EpyPuLMvGpVdQH"

NOME_IMAGEM = "lar_doce_lar.png"
IMAGEM_NAZARE = "Nazare.jpg"

LISTA_MESES = [
    "Janeiro/2026", "Fevereiro/2026", "Março/2026", "Abril/2026", "Maio/2026", "Junho/2026",
    "Julho/2026", "Agosto/2026", "Setembro/2026", "Outubro/2026", "Novembro/2026", "Dezembro/2026"
]

MAPA_MESES = {
    "Janeiro/2026": "2026.01", "Fevereiro/2026": "2026.02", "Março/2026": "2026.03",
    "Abril/2026": "2026.04", "Maio/2026": "2026.05", "Junho/2026": "2026.06",
    "Julho/2026": "2026.07", "Agosto/2026": "2026.08", "Setembro/2026": "2026.09",
    "Outubro/2026": "2026.10", "Novembro/2026": "2026.11", "Dezembro/2026": "2026.12"
}

# USUÁRIOS
USUARIOS = {
    "Admin": {"senha": "2311", "perfil": "admin"},
    "Vicente": {"senha": "1103", "perfil": "familia"},
    "Amoreco": {"senha": "1812", "perfil": "marido"}
}

if 'logado' not in st.session_state:
    st.session_state.logado = False
    st.session_state.perfil = None
    st.session_state.usuario_atual = None

# --- FUNÇÕES PARA CONVERSÃO DE IMAGENS EM BASE64 ---
def obter_imagem_base64(caminho_img):
    if os.path.exists(caminho_img):
        with open(caminho_img, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

img_familia_b64 = obter_imagem_base64(NOME_IMAGEM)
img_nazare_b64 = obter_imagem_base64(IMAGEM_NAZARE)

# --- INJEÇÃO UNIVERSAL DE CSS SEGURO ---
if img_familia_b64:
    background_style = f"""
        background: linear-gradient(rgba(232, 138, 122, 0.83), rgba(232, 138, 122, 0.83)), 
                    url("data:image/png;base64,{img_familia_b64}");
        background-size: 100% auto;
        background-position: top center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    """
else:
    background_style = "background-color: #E88A7A;"

if img_nazare_b64:
    nazare_style = f"""
        background-image: url("data:image/jpeg;base64,{img_nazare_b64}");
        background-size: cover;
        background-position: center;
        background-blend-mode: overlay;
        background-color: rgba(255, 255, 255, 0.55);
    """
else:
    nazare_style = "background-color: #FDF5F3;"

st.markdown(f"""
    <style>
    .stApp {{ {background_style} color: #2F1F1D; }}
    .stTextInput > div > div > input, .stSelectbox > div > div, .stNumberInput > div > div > input {{
        background-color: #FCEBE8 !important; color: #2F1F1D !important; border: 1px solid #D16B5B !important; border-radius: 8px !important;
    }}
    label, .stMarkdown, p {{ color: #3E2723 !important; font-weight: 500; }}
    [data-testid="stForm"] {{
        background-color: #FDF5F3 !important; border: 2px solid #D16B5B !important; border-radius: 12px !important; padding: 20px !important; box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1); max-width: 200px !important; margin: 0 auto !important;
    }}
    [data-testid="stForm"] div.stButton > button {{ background-color: #3E2723 !important; color: #FCEBE8 !important; border-radius: 8px !important; border: none !important; font-weight: bold; width: 100%; }}
    .botao-sair button {{ background-color: #3E2723 !important; color: #FCEBE8 !important; border-radius: 8px !important; border: 2px solid #FCEBE8 !important; font-weight: bold !important; width: 100%; }}
    div.stDownloadButton > button {{ background-color: #2E7D32 !important; color: #FFFFFF !important; border-radius: 8px !important; border: none !important; width: 100%; font-weight: bold; }}
    .destaque-box {{ background-color: #FDF5F3; padding: 22px; border-radius: 12px; box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1); border: 2px solid #D16B5B; margin-bottom: 20px; }}
    .caixa-nazare-container {{ {nazare_style} padding: 22px; border-radius: 12px; box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1); border: 2px solid #D16B5B; margin-bottom: 20px; }}
    .grid-nazare {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-top: 15px; }}
    .item-nazare {{ flex: 1; min-width: 120px; text-align: center; }}
    .label-nazare {{ color: #21100B !important; font-size: 14px; font-weight: bold; margin-bottom: 5px; text-shadow: 0px 0px 4px rgba(255, 255, 255, 0.8); }}
    .val-nazare {{ color: #000000 !important; font-size: 22px; font-weight: bold; text-shadow: 0px 0px 5px rgba(255, 255, 255, 0.9); }}
    .erro-grande {{ text-align: center; color: #C62828; font-size: 14px; font-weight: bold; padding: 10px; background-color: #FFEBEE; border-radius: 8px; border: 1px solid #FFCDD2; margin-top: 5px; }}
    .erro-grande span {{ font-size: 32px; display: block; margin-bottom: 2px; }}

    /* REMOVE ELEMENTOS E COMPONENTES ESTRUTURAIS SEM AFETAR IFRAMES DO GOOGLE */
    [data-testid="stToolbar"] {{ display: none !important; }}
    [data-testid="stDecoration"] {{ display: none !important; }}
    [data-testid="stStatusWidget"] {{ display: none !important; }}
    #MainMenu {{ visibility: hidden !important; }}
    header {{ visibility: hidden !important; }}
    footer {{ visibility: hidden !important; }}
    
    /* REMOVE BOTÕES DE DEPLOY, VIEWERS E DE COMPARTILHAMENTO DO CLOUD */
    .stAppDeployButton {{ display: none !important; }}
    [data-testid="stCloudViewerConnectionStatus"] {{ display: none !important; }}
    button[kind="header"] {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES CONECTADAS AO GOOGLE DRIVE ---

def buscar_arquivo_no_drive(nome_arquivo):
    """Procura um arquivo pelo nome dentro da pasta específica do Drive e retorna o ID"""
    query = f"'{PASTA_DRIVE_ID}' in parents and name = '{nome_arquivo}' and trashed = false"
    resultados = drive_service.files().list(q=query, fields="files(id, name)").execute()
    arquivos = resultados.get('files', [])
    if arquivos:
        return arquivos[0]['id']
    return None

def salvar_historico_completo_drive(prefixo, val_luz, total_kwh, leitura_ant, leitura_at, val_agua):
    nome_txt = f"{prefixo} - valores.txt"
    conteudo = f"{val_luz}\n{total_kwh}\n{leitura_ant}\n{leitura_at}\n{val_agua}\n"
    
    file_id = buscar_arquivo_no_drive(nome_txt)
    arquivo_memoria = io.BytesIO(conteudo.encode('utf-8'))
    media = MediaIoBaseUpload(arquivo_memoria, mimetype='text/plain', resumable=False)
    
    if file_id:
        drive_service.files().update(fileId=file_id, media_body=media).execute()
    else:
        metadados = {'name': nome_txt, 'parents': [PASTA_DRIVE_ID]}
        drive_service.files().create(body=metadados, media_body=media).execute()

def carregar_historico_completo_drive(prefixo):
    nome_txt = f"{prefixo} - valores.txt"
    file_id = buscar_arquivo_no_drive(nome_txt)
    
    if file_id:
        try:
            buffer = io.BytesIO()
            requisicao = drive_service.files().get_media(fileId=file_id)
            downloader = MediaIoBaseDownload(buffer, requisicao)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            buffer.seek(0)
            linhas = [l.strip() for l in buffer.read().decode('utf-8').split('\n') if l.strip()]
            if len(linhas) >= 5:
                return float(linhas[0]), float(linhas[1]), float(linhas[2]), float(linhas[3]), float(linhas[4])
        except Exception as e:
            st.warning(f"Erro ao carregar dados: {e}")
            return 0.0, 0.0, 0.0, 0.0, 0.0
    return 0.0, 0.0, 0.0, 0.0, 0.0

def upload_documento_drive(arquivo_st, nome_final):
    """Faz o upload de qualquer documento para o Drive limpando duplicatas antigas"""
    file_id = buscar_arquivo_no_drive(nome_final)
    arquivo_memoria = io.BytesIO(arquivo_st.getvalue())
    media = MediaIoBaseUpload(arquivo_memoria, mimetype=arquivo_st.type, resumable=False)
    
    if file_id:
        drive_service.files().update(fileId=file_id, media_body=media).execute()
    else:
        metadados = {'name': nome_final, 'parents': [PASTA_DRIVE_ID]}
        drive_service.files().create(body=metadados, media_body=media).execute()

def baixar_arquivo_do_drive_para_download(file_id):
    buffer = io.BytesIO()
    requisicao = drive_service.files().get_media(fileId=file_id)
    downloader = MediaIoBaseDownload(buffer, requisicao)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buffer.seek(0)
    return buffer.read()

def buscar_leitura_atual_anterior(mes_selecionado):
    try:
        idx = LISTA_MESES.index(mes_selecionado)
        if idx > 0:
            mes_anterior = LISTA_MESES[idx - 1]
            prefixo_ant = MAPA_MESES[mes_anterior]
            dados = carregar_historico_completo_drive(prefixo_ant)
            return dados[3]
    except Exception:
        pass
    return 0.0

def listar_todos_arquivos_drive():
    try:
        query = f"'{PASTA_DRIVE_ID}' in parents and trashed = false"
        resultados = drive_service.files().list(q=query, fields="files(name)").execute()
        arquivos = resultados.get('files', [])
        return [arq['name'] for arq in arquivos]
    except Exception:
        pass
    return []

# ==========================================
# 1. TELA DE LOGIN
# ==========================================
if not st.session_state.logado:
    st.markdown("<div style='margin-top: 130px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-top: 15px;'>🏠 Lar doce Lar</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #3E2723;'>Insira suas credenciais para acessar o portal</p>", unsafe_allow_html=True)
    
    with st.form(key="login_form"):
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")
        botao_entrar = st.form_submit_button("Entrar")
        
        if botao_entrar:
            if usuario_input in USUARIOS and USUARIOS[usuario_input]["senha"] == senha_input:
                st.session_state.logado = True
                st.session_state.perfil = USUARIOS[usuario_input]["perfil"]
                st.session_state.usuario_atual = usuario_input
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

# ==========================================
# 2. TELAS DO SISTEMA (PÓS-LOGIN)
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

    st.markdown("<h1 style='text-align: center; margin-top: 15px;'>🏠 Lar doce Lar</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #D16B5B;'>", unsafe_allow_html=True)

    # ------------------------------------------
    # 2.1. PAINEL ADMIN
    # ------------------------------------------
    if st.session_state.perfil == "admin":
        st.subheader("⚙️ Painel de Administração")
        aba_subir, aba_historio = st.tabs(["🚀 Lançar Valores e Contas", "📊 Arquivos no Drive"])
        
        with aba_subir:
            mes_ano = st.selectbox("Selecione o Mês/Ano de referência:", LISTA_MESES, index=4)
            prefixo_data = MAPA_MESES[mes_ano]
            
            luz_fatura, kwh_fatura, medidor_ant, leitura_at, agua_fatura = carregar_historico_completo_drive(prefixo_data)
            
            if medidor_ant == 0.0:
                medidor_ant = buscar_leitura_atual_anterior(mes_ano)
            
            st.markdown("#### ⚡ Fatura de Energia - COPEL")
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                val_luz = st.number_input("Valor Total da Fatura Copel (R$)", min_value=0.0, step=0.01, value=luz_fatura, key="adm_luz_tot")
            with col_l2:
                total_kwh = st.number_input("Consumo Total de kW/h", min_value=0.0, step=0.1, value=kwh_fatura, key="adm_kwh_tot")
            
            st.markdown("#### 🔍 Medidor Interno (Dry / Rafa)")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                leitura_ant_input = st.number_input("Leitura Anterior do Medidor Interno", min_value=0.0, step=0.1, value=medidor_ant)
            with col_m2:
                leitura_at_input = st.number_input("Leitura Atual do Medidor Interno", min_value=0.0, step=0.1, value=leitura_at)
            
            st.markdown("#### 💧 Fatura de Água SANEPAR")
            val_agua = st.number_input("Valor Total da Conta de Água (R$)", min_value=0.0, step=0.01, value=agua_fatura, key="adm_agua_tot")
            
            st.markdown("---")
            st.markdown("#### 📂 Upload das Faturas Originais")
            col_up1, col_up2 = st.columns(2)
            with col_up1:
                arquivo_luz = st.file_uploader("📄 Fatura da Luz (Copel)", type=["pdf", "jpg", "jpeg", "png"], key="up_fatura_luz")
            with col_up2:
                arquivo_agua = st.file_uploader("📄 Fatura da Água (Sanepar)", type=["pdf", "jpg", "jpeg", "png"], key="up_fatura_agua")
            
            st.markdown("---")
            st.markdown("#### 🧾 Upload dos Comprovantes de Pagamento")
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                comp_luz = st.file_uploader("✅ Comprovante da Luz", type=["pdf", "jpg", "jpeg", "png", "txt"], key="up_comp_luz")
            with col_c2:
                comp_agua = st.file_uploader("✅ Comprovante da Água", type=["pdf", "jpg", "jpeg", "png", "txt"], key="up_comp_agua")
            with col_c3:
                comp_net = st.file_uploader("✅ Comprovante da Internet", type=["pdf", "jpg", "jpeg", "png", "txt"], key="up_comp_net")

            st.markdown("---")

            if st.button("💾 Salvar e Publicar no Sistema", use_container_width=True):
                with st.spinner("Atualizando base de dados no Drive..."):
                    try:
                        salvar_historico_completo_drive(prefixo_data, val_luz, total_kwh, leitura_ant_input, leitura_at_input, val_agua)
                        
                        if arquivo_luz is not None:
                            upload_documento_drive(arquivo_luz, f"{prefixo_data} - luz{os.path.splitext(arquivo_luz.name)[1].lower()}")
                        if arquivo_agua is not None:
                            upload_documento_drive(arquivo_agua, f"{prefixo_data} - água{os.path.splitext(arquivo_agua.name)[1].lower()}")
                        if comp_luz is not None:
                            upload_documento_drive(comp_luz, f"{prefixo_data} - comp_luz{os.path.splitext(comp_luz.name)[1].lower()}")
                        if comp_agua is not None:
                            upload_documento_drive(comp_agua, f"{prefixo_data} - comp_água{os.path.splitext(comp_agua.name)[1].lower()}")
                        if comp_net is not None:
                            upload_documento_drive(comp_net, f"{prefixo_data} - comp_internet{os.path.splitext(comp_net.name)[1].lower()}")
                        
                        st.success(f"✅ Dados e mídias de {mes_ano} publicados com sucesso no Drive!")
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar: {e}")

        with aba_historio:
            with st.spinner("Buscando lista de arquivos no Drive..."):
                arquivos_na_pasta = listar_todos_arquivos_drive()
                if arquivos_na_pasta:
                    for arq in sorted(arquivos_na_pasta):
                        st.write(f"📁 {arq}")
                else:
                    st.info("Nenhum arquivo encontrado na pasta do Drive.")

    # ------------------------------------------
    # 2.2. ESPAÇO DA FAMÍLIA (Vicente OU Marido)
    # ------------------------------------------
    elif st.session_state.perfil in ["familia", "marido"]:
        if st.session_state.perfil == "marido":
            st.markdown(f"<h3 style='text-align: center; color: #3E2723;'>👋 Bem-vindo ao seu Espaço, {st.session_state.usuario_atual}!</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center; color: #3E2723;'>👋 Bem-vindo ao Espaço da Família!</h3>", unsafe_allow_html=True)
        
        mes_selecionado = st.selectbox("Selecione o Mês/Ano:", LISTA_MESES, index=4)
        codigo_mes = MAPA_MESES[mes_selecionado]
        
        with st.spinner("Carregando valores do Drive..."):
            val_luz, total_kwh, leitura_ant, leitura_at, val_agua = carregar_historico_completo_drive(codigo_mes)
        
        if total_kwh > 0 and leitura_at >= leitura_ant:
            valor_por_kwh = val_luz / total_kwh
            consumo_dry_rafa = leitura_at - leitura_ant
            custo_dry_rafa = consumo_dry_rafa * valor_por_kwh
            
            if st.session_state.perfil == "marido":
                parte_luz_exibida = custo_dry_rafa
                titulo_detalhe = "📝 Detalhamento dos Gastos (Dry / Rafa)"
            else:
                parte_luz_exibida = val_luz - custo_dry_rafa
                titulo_detalhe = "📝 Detalhamento dos Gastos (Gaby / Mandy)"
        else:
            parte_luz_exibida = 0.0
            titulo_detalhe = "📝 Detalhamento dos Gastos"
            
        parte_agua_exibida = val_agua / 2
        internet_fixo = 55.00
        
        total_a_pagar = parte_luz_exibida + parte_agua_exibida + internet_fixo
        
        st.markdown(f"""
            <div class='destaque-box'>
                <h3 style='margin-top:0; color:#3E2723;'>💰 Resumo do Mês: {mes_selecionado}</h3>
                <p style='font-size: 19px;'><b>Total a Pagar:</b> <span style='color: #2E7D32; font-size: 24px; font-weight: bold;'>R$ {total_a_pagar:.2f}</span></p>
                <hr style='border: 0.5px solid #D16B5B;'>
                <p style='font-size: 16px; margin-bottom: 0;'>🔑 <b>Chave PIX:</b> <code style='font-size: 15px; background-color: #EEA296; color: #3E2723; padding: 4px 8px; border-radius: 4px;'>08974285959</code></p>
            </div>
        """, unsafe_allow_html=True)
        
        # SESSÃO QR CODE DINÂMICO
        st.markdown("<h4 style='text-align: center;'>📱 Escaneie para Pagar (Pix Copia e Cola / QR Code)</h4>", unsafe_allow_html=True)
        st.info("Área reservada para a imagem do QR Code correspondente ao valor.")
        
        st.markdown(f"""
            <div class="caixa-nazare-container">
                <h4 style="margin-top: 0; color: #21100B; text-shadow: 0px 0px 4px rgba(255,255,255,0.8);">{titulo_detalhe}</h4>
                <div class="grid-nazare">
                    <div class="item-nazare">
                        <div class="label-nazare">⚡ Energia Copel</div>
                        <div class="val-nazare">R$ {parte_luz_exibida:.2f}</div>
                    </div>
                    <div class="item-nazare">
                        <div class="label-nazare">💧 Água Sanepar</div>
                        <div class="val-nazare">R$ {parte_agua_exibida:.2f}</div>
                    </div>
                    <div class="item-nazare">
                        <div class="label-nazare">🌐 Internet (Fixo)</div>
                        <div class="val-nazare">R$ {internet_fixo:.2f}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # SEÇÃO 1: BAIXAR FATURAS
        st.markdown("<h4 style='text-align: center; margin-top: 25px;'>📂 Baixar Faturas Oficiais</h4>", unsafe_allow_html=True)
        col_down_1, col_down_2 = st.columns(2)
        
        id_luz_drive = None
        nome_luz_final = None
        for ext in ['.pdf', '.jpg', '.jpeg', '.png']:
            id_luz_drive = buscar_arquivo_no_drive(f"{codigo_mes} - luz{ext}")
            if id_luz_drive:
                nome_luz_final = f"{codigo_mes} - luz{ext}"
                break
        
        with col_down_1:
            if id_luz_drive:
                conteudo_luz = baixar_arquivo_do_drive_para_download(id_luz_drive)
                st.download_button(label="📥 Fatura Luz", data=conteudo_luz, file_name=nome_luz_final, mime="application/octet-stream")
            else:
                st.markdown('<div class="erro-grande"><span>❌</span>Fatura de Luz<br>não disponível</div>', unsafe_allow_html=True)
                
        id_agua_drive = None
        nome_agua_final = None
        for ext in ['.pdf', '.jpg', '.jpeg', '.png']:
            id_agua_drive = buscar_arquivo_no_drive(f"{codigo_mes} - água{ext}")
            if id_agua_drive:
                nome_agua_final = f"{codigo_mes} - água{ext}"
                break
                
        with col_down_2:
            if id_agua_drive:
                conteudo_agua = baixar_arquivo_do_drive_para_download(id_agua_drive)
                st.download_button(label="📥 Fatura Água", data=conteudo_agua, file_name=nome_agua_final, mime="application/octet-stream")
            else:
                st.markdown('<div class="erro-grande"><span>❌</span>Fatura de Água<br>não disponível</div>', unsafe_allow_html=True)

        # SEÇÃO 2: COMPROVANTES
        st.markdown("<hr style='border: 0.5px dashed #D16B5B;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center;'>🧾 Comprovantes de Quitação</h4>", unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)

        # Checar Comprovante Luz
        id_c_luz = None
        nome_c_luz = None
        for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.txt']:
            id_c_luz = buscar_arquivo_no_drive(f"{codigo_mes} - comp_luz{ext}")
            if id_c_luz:
                nome_c_luz = f"{codigo_mes} - comp_luz{ext}"
                break
        with col_c1:
            if id_c_luz:
                st.download_button(label="🧾 Comp. Luz", data=baixar_arquivo_do_drive_para_download(id_c_luz), file_name=nome_c_luz)
            else:
                st.markdown('<div class="erro-grande"><span>❌</span>Comp. Luz<br>ausente</div>', unsafe_allow_html=True)

        # Checar Comprovante Água
        id_c_agua = None
        nome_c_agua = None
        for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.txt']:
            id_c_agua = buscar_arquivo_no_drive(f"{codigo_mes} - comp_água{ext}")
            if id_c_agua:
                nome_c_agua = f"{codigo_mes} - comp_água{ext}"
                break
        with col_c2:
            if id_c_agua:
                st.download_button(label="🧾 Comp. Água", data=baixar_arquivo_do_drive_para_download(id_c_agua), file_name=nome_c_agua)
            else:
                st.markdown('<div class="erro-grande"><span>❌</span>Comp. Água<br>ausente</div>', unsafe_allow_html=True)

        # Checar Comprovante Internet
        id_c_net = None
        nome_c_net = None
        for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.txt']:
            id_c_net = buscar_arquivo_no_drive(f"{codigo_mes} - comp_internet{ext}")
            if id_c_net:
                nome_c_net = f"{codigo_mes} - comp_internet{ext}"
                break
        with col_c3:
            if id_c_net:
                st.download_button(label="🧾 Comp. Net", data=baixar_arquivo_do_drive_para_download(id_c_net), file_name=nome_c_net)
            else:
                st.markdown('<div class="erro-grande"><span>❌</span>Comp. Internet<br>ausente</div>', unsafe_allow_html=True)