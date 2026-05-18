# =========================================================
# IMPORTS
# =========================================================

import streamlit as st
import os
import base64
import json
import io

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Lar doce Lar",
    page_icon="🏠",
    layout="centered"
)

# =========================================================
# GOOGLE DRIVE
# =========================================================

try:

    if "google_credentials" in st.secrets:

        credenciais_dict = json.loads(
            st.secrets["google_credentials"]
        )

        creds = Credentials.from_service_account_info(
            credenciais_dict,
            scopes=["https://www.googleapis.com/auth/drive"]
        )

        drive_service = build(
            'drive',
            'v3',
            credentials=creds
        )

    else:
        st.error(
            "Erro: Credenciais Google não encontradas nos Secrets."
        )
        st.stop()

except Exception as e:

    st.error(f"Erro conectando ao Google Drive: {e}")
    st.stop()

# =========================================================
# PASTA DRIVE
# =========================================================

PASTA_DRIVE_ID = "1uM5fKwOJyo418E-Te3EpyPuLMvGpVdQH"

# =========================================================
# ARQUIVOS
# =========================================================

NOME_IMAGEM = "lar_doce_lar.png"
IMAGEM_NAZARE = "Nazare.jpg"

# =========================================================
# MESES
# =========================================================

LISTA_MESES = [
    "Janeiro/2026",
    "Fevereiro/2026",
    "Março/2026",
    "Abril/2026",
    "Maio/2026",
    "Junho/2026",
    "Julho/2026",
    "Agosto/2026",
    "Setembro/2026",
    "Outubro/2026",
    "Novembro/2026",
    "Dezembro/2026"
]

MAPA_MESES = {
    "Janeiro/2026": "2026.01",
    "Fevereiro/2026": "2026.02",
    "Março/2026": "2026.03",
    "Abril/2026": "2026.04",
    "Maio/2026": "2026.05",
    "Junho/2026": "2026.06",
    "Julho/2026": "2026.07",
    "Agosto/2026": "2026.08",
    "Setembro/2026": "2026.09",
    "Outubro/2026": "2026.10",
    "Novembro/2026": "2026.11",
    "Dezembro/2026": "2026.12"
}

# =========================================================
# USUÁRIOS
# =========================================================

USUARIOS = {
    "Admin": {
        "senha": "2311",
        "perfil": "admin"
    },
    "Vicente": {
        "senha": "1103",
        "perfil": "familia"
    },
    "Amoreco": {
        "senha": "1812",
        "perfil": "marido"
    }
}

# =========================================================
# SESSION STATE
# =========================================================

if 'logado' not in st.session_state:

    st.session_state.logado = False
    st.session_state.perfil = None
    st.session_state.usuario_atual = None

# =========================================================
# BASE64 IMAGENS
# =========================================================

def obter_imagem_base64(caminho_img):

    try:

        if os.path.exists(caminho_img):

            with open(caminho_img, "rb") as f:
                data = f.read()

            return base64.b64encode(data).decode()

    except Exception as e:
        st.error(f"Erro imagem {caminho_img}: {e}")

    return None

img_familia_b64 = obter_imagem_base64(NOME_IMAGEM)
img_nazare_b64 = obter_imagem_base64(IMAGEM_NAZARE)

# =========================================================
# CSS ORIGINAL
# =========================================================

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

    .stApp {{
        {background_style}
        color: #2F1F1D;
    }}

    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {{
        background-color: #FCEBE8 !important;
        color: #2F1F1D !important;
        border: 1px solid #D16B5B !important;
        border-radius: 8px !important;
    }}

    label,
    .stMarkdown,
    p {{
        color: #3E2723 !important;
        font-weight: 500;
    }}

    [data-testid="stForm"] {{
        background-color: #FDF5F3 !important;
        border: 2px solid #D16B5B !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        max-width: 200px !important;
        margin: 0 auto !important;
    }}

    [data-testid="stForm"] div.stButton > button {{
        background-color: #3E2723 !important;
        color: #FCEBE8 !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold;
        width: 100%;
    }}

    .botao-sair button {{
        background-color: #3E2723 !important;
        color: #FCEBE8 !important;
        border-radius: 8px !important;
        border: 2px solid #FCEBE8 !important;
        font-weight: bold !important;
        width: 100%;
    }}

    div.stDownloadButton > button {{
        background-color: #3E2723 !important;
        color: #FCEBE8 !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100%;
        font-weight: bold;
    }}

    .destaque-box {{
        background-color: #FDF5F3;
        padding: 22px;
        border-radius: 12px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        border: 2px solid #D16B5B;
        margin-bottom: 20px;
    }}

    .caixa-nazare-container {{
        {nazare_style}
        padding: 22px;
        border-radius: 12px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        border: 2px solid #D16B5B;
        margin-bottom: 20px;
    }}

    .gif-coadjuvante {{
        margin: 0 auto !important;
        text-align: center;
    }}

    .gif-coadjuvante img {{
        max-width: 200px !important;
        height: auto !important;
    }}

    .grid-nazare {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        margin-top: 15px;
    }}

    .item-nazare {{
        flex: 1;
        min-width: 120px;
        text-align: center;
    }}

    .label-nazare {{
        color: #21100B !important;
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 5px;
        text-shadow: 0px 0px 4px rgba(255,255,255,0.8);
    }}

    .val-nazare {{
        color: #000000 !important;
        font-size: 22px;
        font-weight: bold;
        text-shadow: 0px 0px 5px rgba(255,255,255,0.9);
    }}

    </style>
""", unsafe_allow_html=True)

# =========================================================
# GOOGLE DRIVE FUNÇÕES
# =========================================================

def buscar_arquivo_no_drive(nome_arquivo):

    try:

        query = (
            f"'{PASTA_DRIVE_ID}' in parents "
            f"and name = '{nome_arquivo}' "
            f"and trashed = false"
        )

        resultados = drive_service.files().list(
            q=query,
            fields="files(id, name)"
        ).execute()

        arquivos = resultados.get('files', [])

        if arquivos:
            return arquivos[0]['id']

    except Exception as e:
        st.error(f"Erro buscando arquivo: {e}")

    return None


def salvar_historico_completo_drive(
    prefixo,
    val_luz,
    total_kwh,
    leitura_ant,
    leitura_at,
    val_agua
):

    try:

        nome_txt = f"{prefixo} - valores.txt"

        conteudo = (
            f"{val_luz}\n"
            f"{total_kwh}\n"
            f"{leitura_ant}\n"
            f"{leitura_at}\n"
            f"{val_agua}\n"
        )

        arquivo_memoria = io.BytesIO(
            conteudo.encode("utf-8")
        )

        media = MediaIoBaseUpload(
            arquivo_memoria,
            mimetype='text/plain',
            resumable=True
        )

        file_id = buscar_arquivo_no_drive(nome_txt)

        if file_id:

            drive_service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()

        else:

            metadados = {
                'name': nome_txt,
                'parents': [PASTA_DRIVE_ID]
            }

            drive_service.files().create(
                body=metadados,
                media_body=media
            ).execute()

    except Exception as e:
        st.error(f"Erro salvando histórico: {e}")


def carregar_historico_completo_drive(prefixo):

    try:

        nome_txt = f"{prefixo} - valores.txt"

        file_id = buscar_arquivo_no_drive(nome_txt)

        if file_id:

            conteudo = drive_service.files().get_media(
                fileId=file_id
            ).execute()

            linhas = [
                linha.strip()
                for linha in conteudo.decode('utf-8').split('\n')
                if linha.strip()
            ]

            if len(linhas) >= 5:

                return (
                    float(linhas[0]),
                    float(linhas[1]),
                    float(linhas[2]),
                    float(linhas[3]),
                    float(linhas[4])
                )

    except Exception as e:
        st.error(f"Erro carregando histórico: {e}")

    return 0, 0, 0, 0, 0


def upload_documento_drive(arquivo_st, nome_final):

    try:

        arquivo_memoria = io.BytesIO(
            arquivo_st.getvalue()
        )

        media = MediaIoBaseUpload(
            arquivo_memoria,
            mimetype=arquivo_st.type,
            resumable=True
        )

        file_id = buscar_arquivo_no_drive(nome_final)

        if file_id:

            drive_service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()

        else:

            metadados = {
                'name': nome_final,
                'parents': [PASTA_DRIVE_ID]
            }

            drive_service.files().create(
                body=metadados,
                media_body=media
            ).execute()

    except Exception as e:
        st.error(f"Erro upload arquivo: {e}")
