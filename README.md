# Fan Voice LLM Project: Uma Plataforma de Análise de Sentimentos e opiniões dos fãs de Futebol

## Visão Geral

O ‘Fan Voice LLM Project’ é uma iniciativa que explora o uso de modelos de linguagem avançados para capturar e analisar a opinião dos torcedores de futebol sobre os jogos de seus times favoritos.
O projeto busca disponibilizar uma plataforma pública e acessível, onde qualquer pessoa possa visualizar e explorar as impressões e emoções dos torcedores sobre jogos de futebol específicos.
O projeto inclui processos de Extração, Transformação e Carregamento (ETL) para capturar dados de redes sociais. Além disso, os dados coletados são analisados por meio de consultas SQL para identificar padrões de sentimentos (positivos, negativos, neutros) e outras métricas relevantes, fornecendo insights sobre a percepção dos torcedores em relação a eventos como gols, substituições e lances polêmicos.
Este projeto não só promete revolucionar a forma como vemos o futebol, mas também como compreendemos a paixão e as emoções que o esporte desperta nos corações dos torcedores.

## Página Principal da Plataforma
Este exemplo foi gerado com base na terceira rodada do Brasileirão 2023 entre Flamengo e Botafogo no Maracanã.
![image](https://github.com/user-attachments/assets/9d2c9df7-4b10-47e0-bac3-c72f4e13fa60)


## Estrutura do Projeto

```plaintext
fan-voice-llm-project/
├── .gitignore
├── app.py
├── README.md
├── requirements.txt
├── queries/
│   ├── concatenate_top_comments_per_round.sql
│   ├── ddl_scripts.sql
│   ├── find_previous_prompt_output.sql
│   ├── sentiment_analysis_query.sql
├── utils/
│   ├── config.py
│   ├── etl_flow.py
│   ├── metricas.py
│   ├── utils.py
```

## Arquivos e Diretórios Principais

- **`.gitignore`**: Arquivo para especificar quais arquivos e diretórios devem ser ignorados pelo Git.
- **`app.py`**: Script principal do projeto que provavelmente contém a lógica de execução.
- **`README.md`**: Este arquivo de documentação.
- **`requirements.txt`**: Arquivo com a lista de dependências do projeto.
- **`queries/`**: Diretório contendo scripts SQL para diversas operações de banco de dados.
  - **`concatenate_top_comments_per_round.sql`**: Script para concatenar os principais comentários por rodada.
  - **`ddl_scripts.sql`**: Scripts de definição de dados (DDL) para criar e modificar estruturas de banco de dados.
  - **`find_previous_prompt_output.sql`**: Script para encontrar a saída de prompts anteriores.
  - **`sentiment_analysis_query.sql`**: Script de análise de sentimento.
- **`utils/`**: Diretório contendo utilitários e scripts de suporte.
  - **`config.py`**: Configurações do projeto.
  - **`etl_flow.py`**: Fluxo de ETL.
  - **`metricas.py`**: Cálculo de métricas.
  - **`utils.py`**: Funções utilitárias diversas.

## Como Executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/antonnyvictor18/fan-voice-llm-project
   cd fan-voice-llm-project
   ```

2. Crie um ambiente virtual com Python 3.12.: 
    ```bash
        python -m venv my_venv
    ```
3. Ative o ambiente virtual:

    Windowns:
   ```bash 
   my_venv/Scripts/Activate
   ```
    macOS/Linux: 
    ```bash 
    source myenv/bin/activate
    ``` 
4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure as variáveis necessárias no arquivo `config.py` e configure suas crediciais em um arquivo `.env`.

6. Execute o script principal:
   ```bash
   streamlit run app.py
   ```
   
