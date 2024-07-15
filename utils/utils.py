import psycopg2
import pandas as pd
import os
from utils.config import config
import matplotlib.pyplot as plt
from dotenv import load_dotenv
load_dotenv(fr"my_venv\enviroment_variables.env")


def read_query_from_file(file_path, time):
    with open(file_path, 'r') as file:
        query = file.read()
    return query.format(time=time)


def fetch_data_from_postgresql(host, database, user, password, query) -> pd.DataFrame:

    try:
        connection = psycopg2.connect(
            host=host,
            dbname=database,
            user=user,
            password=password
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
    title='Rodada '
    xlabel='Sentimento'
    ylabel='Percentual'

    total = df[y_column].sum()

    df[y_column] = (df[y_column] / total) * 100
    
    plt.figure(figsize=(10, 6))
    for i, row in df.iterrows():
        if row[x_column] == "Positive":
            plt.bar(row[x_column], row[y_column], color='green')
        elif row[x_column] == "Neutral":
            plt.bar(row[x_column], row[y_column], color='grey')
        else:
            plt.bar(row[x_column], row[y_column], color='red')

    formatado = "{}, {}".format(rodada, time)
    title += formatado
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
    title='Sentimento até Rodada '
    xlabel='Rodada'
    ylabel='Qtd Comentários'

    plt.figure(figsize=(10, 6))
    
    df.index = range(1, len(df.index) + 1)
    for column in columns:
        if column == "Positive":
            plt.plot(df.index, df[column], label=column, marker='o', color='green')
        elif column == "Neutral":
            plt.plot(df.index, df[column], label=column, marker='o', color='grey')
        else:
            plt.plot(df.index, df[column], label=column, marker='o', color='red')


    formatado = "{}, {}".format(rodada, time)
    title += formatado    
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
    host = 'localhost'
    database = 'postgres'
    user = 'postgres'
    password = os.environ.get('DB_PASSWORD')

    query = read_query_from_file('queries\sentiment_analysis_query.sql', time)

    data = fetch_data_from_postgresql(host, database, user, password, query)

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
