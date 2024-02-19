SELECT
    p.pl_id AS player_id,
    p.pl_name AS player_name,
    COUNT(g.gm_id) AS total_games_played,
    COALESCE(SUM(CASE WHEN (g.gm_result_A > g.gm_result_B AND (g.gm_idPlayer_A1 = 37 OR g.gm_idPlayer_A2 = 37)) OR
                           (g.gm_result_B > g.gm_result_A AND (g.gm_idPlayer_B1 = 37 OR g.gm_idPlayer_B2 = 37))
                      THEN 1 ELSE 0 END), 0) AS total_games_won
FROM
    tb_players p
LEFT JOIN
    tb_game g ON p.pl_id IN (g.gm_idPlayer_A1, g.gm_idPlayer_A2, g.gm_idPlayer_B1, g.gm_idPlayer_B2)
WHERE
    p.pl_id = 37
GROUP BY
    p.pl_id, p.pl_name;
