import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from torch import imag
from utils.utils import graphics_generator, match_title_finder, summuarize_fan_voice, insert_data
from utils.config import config
import os


st.set_page_config(
    page_title="Análise de Sentimento dos Torcedores",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_image(image_path):
    return Image.open(image_path)


st.sidebar.title("Configurações")
time_selecionado = st.sidebar.selectbox("Selecione o Time", config['teams_reddit'].keys())
rodada_selecionada = st.sidebar.selectbox("Selecione a Rodada", range(1, 39))
confirm_button = st.sidebar.button("Confirmar")
st.sidebar.text("Desenvolvido por Antonny e Felipe")
st.title("Análise de Emoção dos Torcedores de Futebol")

if confirm_button:
    confronto_selecionado = match_title_finder(time_selecionado, rodada_selecionada)
    st.subheader(f"Confronto: {confronto_selecionado} pela {rodada_selecionada}ª Rodada")
    image_path1, image_path2 = graphics_generator(time_selecionado, rodada_selecionada)
    confronto_selecionado = match_title_finder(time_selecionado, rodada_selecionada)
    image1 = load_image(image_path1)
    image2 = load_image(image_path2)
    fig, ax = plt.subplots(1, 2, figsize=(24, 12))
    ax[0].imshow(image1)
    ax[0].axis('off')
    ax[0].autoscale(enable=True, tight=True)  # Add this line to zoom in the image
    ax[1].imshow(image2)
    ax[1].axis('off')
    ax[1].autoscale(enable=True, tight=True)  # Add this line to zoom in the image
    os.remove(image_path1)
    os.remove(image_path2)
    st.pyplot(fig, clear_figure=True)

    fan_voice = summuarize_fan_voice(time_selecionado, rodada_selecionada)
    st.subheader("Voz do Torcedor")
    st.write(fan_voice['fan_voice_output'][0])
