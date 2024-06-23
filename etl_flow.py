import psycopg2
import warnings
from datetime import datetime
from transformers import pipeline, AutoTokenizer
import os
from dotenv import load_dotenv
import praw
import re
from config import config

warnings.filterwarnings('ignore')

def clean_comment(comment):
    # Remover URLs
    comment = re.sub(r'http\S+|www\S+|https\S+', '', comment, flags=re.MULTILINE)
    # Remover hashtags
    comment = re.sub(r'#\w+', '', comment)
    #remover tabs e quebras de linha
    comment = re.sub(r'\n', '', comment)
    comment = re.sub(r'\t', '', comment)
    return comment


def classify_sentiment(text, classifier):
    truncated_text = text[:510]
    result = classifier(truncated_text)[0][0]
    return config["setiment_mapping"][result['label']]


def encontrar_rodada(titulo_post):
    prefixos = ["[Match Thread]", "[jogo]"]
    if any(titulo_post.startswith(prefixo) for prefixo in prefixos):
        match = re.search(r'\: (.+?) x (.+?)$', titulo_post)
        if match:
            time1 = match.group(1)
            time2 = match.group(2)
    else:
        match = re.search(r'\: (.+?) \d+ x \d+ (.+?)$', titulo_post)
        if match:
            time1 = match.group(1)
            time2 = match.group(2)

    if match:
        confronto_formatado = f"{time1} x {time2}"
        rodada = config['rodadas'][confronto_formatado]
        if rodada:
            return rodada
        else:
            raise Exception(f"Confronto {confronto_formatado} não encontrado na configuração.")
    else:
        raise Exception(f"Formato do título do post não reconhecido. \ntitulo_post: {titulo_post}")


def insert_team(team_name, cursor, conn):
    cursor.execute("SELECT team_id FROM brasileirao2023.teams WHERE team_name = %s", (team_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute("INSERT INTO brasileirao2023.teams (team_name) VALUES (%s) RETURNING team_id", (team_name,))
        team_id = cursor.fetchone()[0]
        conn.commit()
        return team_id


def insert_post(team_id, post, cursor, conn):
    post_date = datetime.fromtimestamp(post.created_utc).date()
    post_title = post.title
    post_round = encontrar_rodada(post_title) 
    reddit_post_id = post.id
    cursor.execute("SELECT post_id FROM brasileirao2023.posts WHERE reddit_post_id = %s", (reddit_post_id,))
    result = cursor.fetchone()
    if not result:
        cursor.execute("INSERT INTO brasileirao2023.posts (team_id, post_date, post_title, post_round, reddit_post_id) VALUES (%s, %s, %s, %s, %s) RETURNING post_id",
                       (team_id, post_date, post_title, post_round, reddit_post_id))
        post_id = cursor.fetchone()[0]
        conn.commit()
        return post_id
    else:
        return result[0]


def insert_comments(post_id, comments, cursor, conn, classifier):
    for comment in comments:
        comment_date = datetime.fromtimestamp(comment.created_utc)
        comment_content = clean_comment(comment.body)
        comment_sentiment = classify_sentiment(comment_content, classifier)
        # get the reddit comment upvote score
        comment_score = comment.score
        reddit_comment_id = comment.id
        cursor.execute("SELECT comment_id FROM brasileirao2023.comments WHERE reddit_comment_id = %s", (reddit_comment_id,))
        if cursor.fetchone() is None:
            cursor.execute("""INSERT INTO brasileirao2023.comments 
                           (post_id, comment_date, comment_content, comment_score, comment_sentiment, reddit_comment_id) 
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                           (post_id, comment_date, comment_content, comment_score, comment_sentiment, reddit_comment_id))
            conn.commit()


def main():
    load_dotenv(rf'my_venv\enviroment_variables.env')

    classifier = pipeline(model="lxyuan/distilbert-base-multilingual-cased-sentiments-student", top_k=None)


    reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"),
                        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                        user_agent=os.getenv("REDDIT_USER_AGENT"))

    conn = psycopg2.connect(dbname='postgres', 
                            user='postgres', 
                            password=os.environ.get("DB_PASSWORD"), 
                            host='localhost')
    cursor = conn.cursor()
    
    teams = [ "Flamengo", "Palmeiras", "São Paulo", "Vasco"] 
    for team in teams:
        print(f"Buscando posts do {team}")
        team_id = insert_team(team, cursor, conn)
        subreddit = config['teams_reddit'][team]
        subreddit = reddit.subreddit(subreddit)
        posts = subreddit.search("Campeonato Brasileiro:", sort='new', limit=1000000)
        for post in posts:
            if datetime.fromtimestamp(post.created_utc).year == 2023:
                prefixos = ["[jogo] Campeonato Brasileiro:", "[pós-jogo] Campeonato Brasileiro:", "[Post-Match Thread] Campeonato Brasileiro:", "[Match Thread] Campeonato Brasileiro:"]
                if any(post.title.startswith(prefixo) for prefixo in prefixos):
                    post_id = insert_post(team_id, post, cursor, conn)
                    insert_comments(post_id, post.comments, cursor, conn, classifier)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()