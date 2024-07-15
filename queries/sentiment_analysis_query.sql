select  comments.comment_sentiment as Sentimento,
        posts.post_round as Rodada, 
        teams.team_name as Times,
        count(*) as Total
from brasileirao2023.comments 
inner join
        brasileirao2023.posts on comments.post_id = posts.post_id 
inner join
        brasileirao2023.teams on posts.team_id = teams.team_id
where teams.team_name = '{time}'
group by comments.comment_sentiment, posts.post_round, teams.team_name;
