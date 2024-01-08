from pathlib import Path
from datetime import datetime
import time
import queue

from streamlit_webrtc import WebRtcMode, webrtc_streamer
import streamlit as st

import pydub
import openai
from dotenv import load_dotenv,find_dotenv

PASTA_ARQUIVOS = Path(__file__).parent / 'arquivos'
PASTA_ARQUIVOS.mkdir(exist_ok=True)

_ = load_dotenv(find_dotenv())

## OPEN AI ===========================
client = openai.OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

def transcreve_audio(caminho_audio,language='pt',response_format='text'):
    with open(caminho_audio, 'rb') as arquivo_audio:  
        transcricao = client.audio.transcriptions.create(
        model='whisper-1',
        language=language,
        response_format=response_format,
        file=arquivo_audio
        )
    return transcricao

def chat_openai(
        mensagem,
        modelo='gpt-3.5-turbo-0613',
    ):
    mensagens = [{'role': 'user', 'content': mensagem}]
    resposta = client.chat.completions.create(
        model=modelo,
        messages=mensagens,
        )
    return resposta.choices[0].message.content

## TAB GRAVA REUNIAO ===========================
def tab_gravar_reuniao():
    webrtc_ctx = webrtc_streamer(
        key="recebe-audio",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        media_stream_constraints={"audio": True, "video": False},
        )
    
    if not webrtc_ctx.state.playing:
        return
    
    container = st.empty()
    container.markdown('Gravando...')
    pasta_reuniao = PASTA_ARQUIVOS / datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    pasta_reuniao.mkdir()
    
    audio_chunk = pydub.AudioSegment.empty()
    
    while True:
        if webrtc_ctx.audio_receiver:
            
            container.markdown('Recebendo audio...')
            try:
                frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                time.sleep(0.1)
                continue
            for frame in frames:
                sound = pydub.AudioSegment(
                    data=frame.to_ndarray().tobytes(),
                    sample_width=frame.format.bytes,
                    frame_rate=frame.sample_rate,
                    channels=len(frame.layout.channels),
                )
                audio_chunk += sound
            if len(audio_chunk) > 0 :
                audio_chunk.export(pasta_reuniao / 'audio_temp.mp3')
            
        else:
            break
    

## TAB SELECAO REUNIAO ===========================
def tab_selecao_reuniao():
    st.markdown('Tab seleciona')

def main():
    st.header("Bem-vindo ao transcriptor da Bubup 🎙️",divider=True)
    tab_gravar,tab_Selecao = st.tabs(['Gravar reunião','Transcrições salvas'])
    with tab_gravar:
        tab_gravar_reuniao()
    with tab_Selecao:
        tab_selecao_reuniao()
    
    
if __name__ == "__main__":
    main()