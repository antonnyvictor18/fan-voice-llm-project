import psycopg2
from openai import OpenAI
import pandas as pd
import os
from utils.config import config
import matplotlib.pyplot as plt
from dotenv import load_dotenv
load_dotenv(fr"my_venv\enviroment_variables.env")


def read_query_from_file(file_path, args) -> str:
    with open(file_path, 'r') as file:
        query = file.read()
    return query.format(**args)


def fetch_data_from_postgresql(query) -> pd.DataFrame:
    
    try:
        connection = psycopg2.connect(
            host = 'localhost',
            dbname = 'postgres',
            user = 'postgres',
            password = os.environ.get('DB_PASSWORD')
        )

        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        colnames = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=colnames)

        return df

    except Exception as error:
        print(f"Error: {error}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def create_bar_chart(df, time, rodada, x_column, y_column):
    title='Distribuição de Emoções'
    xlabel='Emoção'
    ylabel='%'

    total = df[y_column].sum()

    df[y_column] = (df[y_column] / total) * 100
    
    plt.figure(figsize=(8, 5))
    for _, row in df.iterrows():
        if row[x_column] == "Positive":
            plt.bar("Positiva", row[y_column], color='green')
        elif row[x_column] == "Neutral":
            plt.bar("Neutra", row[y_column], color='grey')
        else:
            plt.bar("Negativa", row[y_column], color='red')

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.grid(axis = 'y', linestyle = '--', linewidth=0.5)

    filepath = rf"./images/Grafico_{time}_Rodada_{rodada}.png"
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    plt.savefig(filepath)
    plt.close()
    return filepath


def create_three_lines_chart(df, time, rodada, columns):
    title='Histórico de Emoções até a Rodada'
    xlabel='Rodada'
    ylabel='Qtd Comentários'

    plt.figure(figsize=(12, 8))
    
    df.index = range(1, len(df.index) + 1)
    for column in columns:
        if column == "Positive":
            plt.plot(df.index, df[column], label="Positiva", marker='o', color='green')
        elif column == "Neutral":
            plt.plot(df.index, df[column], label= "Neutra", marker='o', color='grey')
        else:
            plt.plot(df.index, df[column], label="Negativa", marker='o', color='red')

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis='y', linestyle='--', linewidth=1)
    plt.legend()
    plt.xticks(df.index)

    filepath = rf"./images/Grafico_{time}_ate_Rodada_{rodada}.png"
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    plt.savefig(filepath)
    plt.close()
    return filepath


def graphics_generator(time, rodada):
    
    query_args = {"time": time}
    query = read_query_from_file('queries\sentiment_analysis_query.sql', query_args)

    data = fetch_data_from_postgresql(query)

    data1 = data[data['rodada'] == rodada].reset_index(drop=True)

    data2 = data[data['rodada'] <= rodada].pivot_table(index='rodada', columns='sentimento', values='total', aggfunc='sum').fillna(0)

    bar_chart_filepath = create_bar_chart(data1, time, rodada, 'sentimento', 'total')
    data2.reset_index(inplace=True)
    lines_chart_filepath = create_three_lines_chart(data2, time, rodada, ['Positive', 'Neutral', 'Negative'])
    return bar_chart_filepath, lines_chart_filepath


def match_title_finder(time_selecionado, rodada_selecionada):
    return next((confronto for confronto, rodada in config['rodadas'].items() 
                    if  rodada == rodada_selecionada and 
                        time_selecionado in confronto),
            None
            )

def generate_report(user_content):
    client = OpenAI(
        api_key = os.getenv('OPENAI_API_KEY'),
        organization=os.getenv('OPENAI_ORGANIZATION_ID'),
        project=os.getenv('OPENAI_PROJECT_ID')
    )

    response = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-0125:personal:fan-voice-report:9ld67guO",
        messages=[
            {"role": "system", "content": "Make a report of the fan's impressions about the game"},
            {"role": "user", "content": user_content}
        ],
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].message.content



def summuarize_fan_voice(time, rodada):
    query_args = {"time": time, "rodada": rodada}
    query = read_query_from_file(rf'queries\find_previous_prompt_output.sql', query_args)
    data = fetch_data_from_postgresql(query)

    if not data.empty:
        return data
    
    query = read_query_from_file(rf'queries\concatenate_top_comments_per_round.sql', query_args)
    data = fetch_data_from_postgresql(query)
    data['fan_voice_output'] = generate_report(data['comments'][0])
    data = data[['team_id', 'post_round', 'fan_voice_output']]
    insert_data(data)
    return data


def insert_data(data):
    try:
        connection = psycopg2.connect(
            host = 'localhost',
            dbname = 'postgres',
            user = 'postgres',
            password = os.environ.get('DB_PASSWORD')
        )
       
        team_id = int(data.iloc[0]['team_id'])
        post_round = int(data.iloc[0]['post_round'])
        fan_voice_output = data.iloc[0]['fan_voice_output']

        cursor = connection.cursor()
        cursor.execute("INSERT INTO brasileirao2023.fan_voice (team_id, post_round, fan_voice_output) VALUES (%s, %s, %s) RETURNING (team_id, post_round)",
                       (team_id, post_round, fan_voice_output))
        tuple_id = cursor.fetchone()[0]
        connection.commit()
        cursor.close()
        connection.close()

        return tuple_id

    except Exception as error:
        print(f"Error: {error}")