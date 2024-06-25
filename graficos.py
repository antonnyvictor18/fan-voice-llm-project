import psycopg2
import pandas as pd
import os
from config import config
import matplotlib.pyplot as plt

time = input('Escolha o time a acompanhar: ')
rodada = input('Escolha a rodada: ')

def fetch_data_from_postgresql(host, database, user, password, query):

    try:
        # Conectar ao banco de dados
        connection = psycopg2.connect(
            host=host,
            dbname=database,
            user=user,
            password=password
        )

        # Criar um cursor
        cursor = connection.cursor()

        # Executar a query
        cursor.execute(query)

        # Pegar todas as entradas da tabela
        rows = cursor.fetchall()

        # Pegar os nomes das colunas
        colnames = [desc[0] for desc in cursor.description]

        # Create a pandas DataFrame from the fetched data
        df = pd.DataFrame(rows, columns=colnames)

        return df

    except Exception as error:
        print(f"Error: {error}")
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def create_bar_chart(df, x_column, y_column, title='Rodada ', xlabel='Sentimento', ylabel='Percentual'):

    # Calcular a soma total de y_column
    total = df[y_column].sum()

    # Converter y_column para percentage
    df[y_column] = (df[y_column] / total) * 100
    
    plt.figure(figsize=(10, 6))
    plt.bar(df[x_column], df[y_column], color='blue')

    # Titulo e labels
    formatado = "{}, {}".format(df.iloc[0]['rodada'], df.iloc[0]['times'])
    title += formatado
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Add grid lines
    plt.grid(axis = 'y', linestyle = '--', linewidth=0.5)

    # Plotar
    plt.show()

if __name__ == "__main__":
    host = 'localhost'
    database = 'postgres'
    user = 'postgres'
    password = os.environ.get('DB_PASSWORD')
    query = """select comments.comment_sentiment as Sentimento, posts.post_round as Rodada, teams.team_name as Times, count(posts.post_round) as Total
               from brasileirao2023.comments inner join
               brasileirao2023.posts
               on comments.post_id = posts.post_id inner join
               brasileirao2023.teams
               on posts.team_id = teams.team_id
               where posts.post_round = {} and teams.team_name = '{}'
               group by comments.comment_sentiment, posts.post_round, teams.team_name;""".format(rodada, time)

    data = fetch_data_from_postgresql(host, database, user, password, query)
    create_bar_chart(data, 'sentimento', 'total')
    