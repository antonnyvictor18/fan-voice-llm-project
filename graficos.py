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
    formatado = "{}, {}".format(rodada, time)
    title += formatado
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Adcionar grid
    plt.grid(axis = 'y', linestyle = '--', linewidth=0.5)

    # Plotar
    plt.show()


def create_three_lines_chart(df, columns, title='Sentimento até Rodada ', xlabel='Rodada', ylabel='Qtd Comentários'):

    plt.figure(figsize=(10, 6))
    
    for column in columns:
        if column == "Positive":
            plt.plot(df.index, df[column], label=column, marker='o', color='green')
        elif column == "Neutral":
            plt.plot(df.index, df[column], label=column, marker='o', color='grey')
        else:
            plt.plot(df.index, df[column], label=column, marker='o', color='red')


    # Titulo e legendas
    formatado = "{}, {}".format(rodada, time)
    title += formatado    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Grid
    plt.grid(axis = 'y', linestyle = '--', linewidth=0.5)

    # Adicionar legenda
    plt.legend()

    # Plotar
    plt.show()

if __name__ == "__main__":
    host = 'localhost'
    database = 'postgres'
    user = 'postgres'
    password = os.environ.get('DB_PASSWORD')
    query1 = """select comments.comment_sentiment as Sentimento, posts.post_round as Rodada, teams.team_name as Times, count(posts.post_round) as Total
               from brasileirao2023.comments inner join
               brasileirao2023.posts
               on comments.post_id = posts.post_id inner join
               brasileirao2023.teams
               on posts.team_id = teams.team_id
               where posts.post_round = {} and teams.team_name = '{}'
               group by comments.comment_sentiment, posts.post_round, teams.team_name;""".format(rodada, time)

    query2 = """
                with temporaryTable(sentimento, rodada, times, total) as
	                (select
		                comments.comment_sentiment as Sentimento,
		                posts.post_round as Rodada, 
                        teams.team_name as Times,
                        count(posts.post_id) as Total
                        from brasileirao2023.comments inner join
                        brasileirao2023.posts
                        on comments.post_id = posts.post_id inner join
                        brasileirao2023.teams
                        on posts.team_id = teams.team_id
                        where posts.post_round < {} and teams.team_name = '{}'
                        group by comments.comment_sentiment, posts.post_round, teams.team_name)
                    select
                        rodada,
                        MAX(CASE sentimento WHEN 'Positive' THEN total END) as "Positive",
                        MAX(CASE sentimento WHEN 'Neutral' THEN total END) as "Neutral",
                        MAX(CASE sentimento WHEN 'Negative' THEN total END) as "Negative"
                    from temporaryTable
                    group by rodada;""".format(rodada, time)    
    
    
    
    data1 = fetch_data_from_postgresql(host, database, user, password, query1)
    data2 = fetch_data_from_postgresql(host, database, user, password, query2)
    create_bar_chart(data1, 'sentimento', 'total')
    data2.set_index('rodada', inplace=True)
    create_three_lines_chart(data2, ['Positive', 'Neutral', 'Negative'])
    