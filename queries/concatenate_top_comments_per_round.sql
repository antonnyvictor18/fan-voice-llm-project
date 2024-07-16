WITH TeamID AS (
    SELECT 
        team_id
    FROM 
        Brasileirao2023.Teams
    WHERE 
        team_name = '{time}' 
),
TopComments AS (
    SELECT 
        c.comment_id,
        c.post_id,
        c.comment_content,
        c.comment_score,
        p.team_id,
        p.post_round,
        ROW_NUMBER() OVER (PARTITION BY p.team_id, p.post_round ORDER BY c.comment_score DESC) AS rn
    FROM 
        Brasileirao2023.Comments c
    JOIN 
        Brasileirao2023.Posts p ON c.post_id = p.post_id
    JOIN 
        TeamID t ON p.team_id = t.team_id
    WHERE 
        p.post_round = {rodada} 
        AND c.comment_content NOT LIKE '%| Estatística |%'
),
FilteredComments AS (
    SELECT 
        comment_id,
        post_id,
        comment_content,
        comment_score,
        team_id,
        post_round
    FROM 
        TopComments
    WHERE 
        rn <= 10
)
SELECT 
    team_id,
    post_round,
    STRING_AGG('"' || REPLACE(comment_content, ';', '.') || '"', ';') AS comments
FROM 
    FilteredComments
GROUP BY 
    team_id, post_round;
