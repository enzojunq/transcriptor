# Transcriptor da Bubup 🎙️

## Descrição
O Transcriptor da Bubup é uma aplicação desenvolvida para transcrever, analisar e sumarizar automaticamente reuniões em tempo real. Usando o processamento de áudio avançado e a análise de linguagem natural fornecida pela API do OpenAI, este app oferece uma solução eficiente para gerenciamento e revisão de reuniões.

## Funcionalidades
- **Gravação de Áudio**: Grava o áudio das reuniões em tempo real.
- **Transcrição Automática**: Utiliza a API da OpenAI para transcrever o áudio gravado.
- **Sumarização e Análise**: Produz resumos abstratos, identifica pontos-chave, itens de ação e analisa o sentimento geral da discussão.
- **Histórico de Reuniões**: Mantém um registro das reuniões que podem ser acessadas e revisadas posteriormente.

## Tecnologias Utilizadas
- **Streamlit**: Para a interface do usuário.
- **Pydub**: Para manipulação de áudio.
- **OpenAI GPT-3.5**: Para transcrição e análise de texto.
- **Streamlit-WebRTC**: Para a captura de áudio em tempo real.

## Como Usar
1. **Configuração de Segredos**: Para começar, configure sua chave de API da OpenAI. Dentro da pasta `.streamlit`, crie um arquivo chamado `secrets.toml` com o seguinte conteúdo:

    ```toml
    OPENAI_API_KEY='sua_chave_api_aqui'
    ```
    
    Substitua `sua_chave_api_aqui` pela sua chave de API pessoal da OpenAI.

2. **Instalação**: Instale todas as dependências necessárias listadas no arquivo `requirements.txt`.

3. **Execução**: Rode a aplicação utilizando o Streamlit com o comando `streamlit run seu_script.py`.

4. **Gravação de Reunião**: Acesse a aba 'Gravar reunião' para iniciar a gravação da reunião e a transcrição será feita automaticamente.

5. **Análise e Sumarização**: Para revisar e analisar reuniões passadas, vá até a aba 'Transcrições salvas'.

## Contribuições
Se você quiser contribuir com o projeto, fique à vontade para fazer um fork, propor melhorias ou enviar um pull request.

## Licença
Distribuído sob a licença [INSIRA A LICENÇA AQUI]. Veja `LICENSE` para mais informações.

## Contato
Para qualquer dúvida ou feedback, por favor, entre em contato através de [SEU EMAIL OU LINK DO PERFIL DO GITHUB].

