Select * 
FROM Brasileirao2023.fan_voice
Where 	team_id in (select team_id from Brasileirao2023.Teams where team_name = '{time}') AND
		post_round = {rodada}
