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

def salva_arquivo(caminho_arquivo,conteudo):
    with open(caminho_arquivo,'w') as arquivo:
        arquivo.write(conteudo)

def le_arquivo(caminho_arquivo):
    if caminho_arquivo.exists():
        with open(caminho_arquivo) as arquivo:
            return arquivo.read()
    else:
        return ''
    
        
def listar_reunioes():
    lista_reunioes = PASTA_ARQUIVOS.glob('*')
    lista_reunioes = list(lista_reunioes)
    lista_reunioes.sort(reverse=True)
    reunioes_dict = {}
    for reuniao in lista_reunioes:
        data_reuniao = reuniao.stem
        ano,mes,dia,hora,min,seg = data_reuniao.split('_')
        reunioes_dict[data_reuniao]=f'{dia}/{mes}/{ano} {hora}:{min}:{seg}'
        titulo = le_arquivo(reuniao / 'titulo.txt')
        if titulo != '':
            reunioes_dict[data_reuniao] += f' - {titulo}'
            
    return reunioes_dict

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

def abstract_summary_extraction(transcription):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Você é uma IA altamente qualificada, treinada em compreensão de linguagem e resumo. Gostaria que você lesse o seguinte texto e o resumisse em um parágrafo abstrato e conciso. Busque reter os pontos mais importantes, fornecendo um resumo coerente e legível que possa ajudar uma pessoa a entender os principais pontos da discussão sem precisar ler o texto inteiro. Por favor, evite detalhes desnecessários ou pontos tangenciais."
            },
            {
                "role": "user",
                "content": transcription
            }
        ]
    )
    return response.choices[0].message.content

def key_points_extraction(transcription):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Você é uma IA competente com especialidade em destilar informações em pontos-chave. Com base no seguinte texto, identifique e liste os principais pontos que foram discutidos ou mencionados. Estes devem ser as ideias, descobertas ou tópicos mais importantes que são cruciais para a essência da discussão. Seu objetivo é fornecer uma lista que alguém possa ler para entender rapidamente sobre o que foi falado."
            },
            {
                "role": "user",
                "content": transcription
            }
        ]
    )
    return response.choices[0].message.content

def action_item_extraction(transcription):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Você é uma IA especialista em analisar conversas e extrair itens de ação. Por favor, revise o texto e identifique quaisquer tarefas, atribuições ou ações que foram acordadas ou mencionadas como necessárias a serem realizadas. Estas podem ser tarefas atribuídas a indivíduos específicos ou ações gerais que o grupo decidiu tomar. Por favor, liste esses itens de ação de forma clara e concisa."
            },
            {
                "role": "user",
                "content": transcription
            }
        ]
    )
    return response.choices[0].message.content

def sentiment_analysis(transcription):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Como uma IA com especialização em linguagem e análise de emoções, sua tarefa é analisar o sentimento do seguinte texto. Por favor, considere o tom geral da discussão, a emoção transmitida pela linguagem usada e o contexto em que as palavras e frases são utilizadas. Indique se o sentimento é geralmente positivo, negativo ou neutro, e forneça breves explicações para sua análise, quando possível."
            },
            {
                "role": "user",
                "content": transcription
            }
        ]
    )
    return response.choices[0].message.content

def meeting_minutes(transcription):
    abstract_summary = abstract_summary_extraction(transcription)
    key_points = key_points_extraction(transcription)
    action_items = action_item_extraction(transcription)
    sentiment = sentiment_analysis(transcription)
    return {
        'abstract_summary': abstract_summary,
        'key_points': key_points,
        'action_items': action_items,
        'sentiment': sentiment
    }

## TAB GRAVA REUNIAO ===========================

def adiciona_chunk_audio(frames,audio):
    for frame in frames:
        sound = pydub.AudioSegment(
            data=frame.to_ndarray().tobytes(),
            sample_width=frame.format.bytes,
            frame_rate=frame.sample_rate,
            channels=len(frame.layout.channels),
        )
        audio += sound
    return audio

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
    
    ultima_transcricao = time.time()
    audio_completo= pydub.AudioSegment.empty()
    audio_chunk = pydub.AudioSegment.empty()
    transcricao = ''
    
    while True:
        if webrtc_ctx.audio_receiver:
        
            try:
                frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                time.sleep(0.1)
                continue
            
            audio_chunk = adiciona_chunk_audio(frames,audio_chunk)
            audio_completo = adiciona_chunk_audio(frames,audio_completo)
            
            if len(audio_chunk) > 0 :
                audio_completo.export(pasta_reuniao / 'audio_.mp3')
                agora = time.time()
                if agora - ultima_transcricao > 5:
                    audio_chunk.export(pasta_reuniao / 'audio_temp.mp3')
                    transcricao_chunk = transcreve_audio(pasta_reuniao / 'audio_temp.mp3')
                    transcricao += transcricao_chunk
                    salva_arquivo(pasta_reuniao / 'transcricao.txt',transcricao)
                    
                    container.markdown(transcricao)
                    
                    audio_chunk = pydub.AudioSegment.empty()
            
        else:
            break
    

## TAB SELECAO REUNIAO ===========================
def tab_selecao_reuniao():
    reunioes_dict = listar_reunioes()
    if len(reunioes_dict)>0:
        reuniao_selecionada = st.selectbox('Selecione a reunião',list(reunioes_dict.values()))
        st.divider()
        reuniao_data = [k for k,v in reunioes_dict.items() if v == reuniao_selecionada][0]
        pasta_reuniao = PASTA_ARQUIVOS / reuniao_data
        if not (pasta_reuniao / 'titulo.txt').exists():
            st.warning("Adicione um título.")
            titulo_reuniao =st.text_input('Título da reunião:')
            st.button('Salvar', on_click=salvar_titulo, args=(pasta_reuniao,titulo_reuniao))
        else:
            titulo = le_arquivo(pasta_reuniao / 'titulo.txt')
            transcricao = le_arquivo(pasta_reuniao / 'transcricao.txt')
            st.markdown(f'## {titulo}')
        
            
            if st.button('Gerar resumo'):
                resumo = meeting_minutes(transcricao)
                st.markdown(f'#### Resumo')
                st.markdown(resumo['abstract_summary'])
                st.markdown(f'#### Pontos-chave')
                st.markdown(resumo['key_points'])
                st.markdown(f'#### Itens de ação')
                st.markdown(resumo['action_items'])
                st.markdown(f'#### Sentimento')
                st.markdown(resumo['sentiment'])
        
                
            # se clicar no botao quer que suma o texto e apareça o resumo
            st.markdown(f'### Transcrição da reunião')
            st.markdown(transcricao)

            
        
        
def salvar_titulo(pasta_reuniao,titulo):
    salva_arquivo(pasta_reuniao / 'titulo.txt',titulo)
    
    
    
    
    
    
    
    

def main():
    st.header("Bem-vindo ao transcriptor da Bubup 🎙️",divider=True)
    tab_gravar,tab_Selecao = st.tabs(['Gravar reunião','Transcrições salvas'])
    with tab_gravar:
        tab_gravar_reuniao()
    with tab_Selecao:
        tab_selecao_reuniao()
    
    
if __name__ == "__main__":
    main()