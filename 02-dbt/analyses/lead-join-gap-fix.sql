-- GW25 h3 → fixture_gameweek_id = 28
insert into archive.player_future_fixtures
    (opta_code, player_id, fetched_gameweek_id, fixture_id, fixture_gameweek_id, is_home, difficulty, team_h, team_a, raw_data)
select
    opta_code, player_id,
    25 as fetched_gameweek_id,
    fixture_id, fixture_gameweek_id, is_home,
    null as difficulty,
    team_h, team_a, raw_data
from archive.player_future_fixtures
where fetched_gameweek_id = 27 and fixture_gameweek_id = 28;

-- GW26 h2 + h3 → fixture_gameweek_id = 28, 29
insert into archive.player_future_fixtures
    (opta_code, player_id, fetched_gameweek_id, fixture_id, fixture_gameweek_id, is_home, difficulty, team_h, team_a, raw_data)
select
    opta_code, player_id,
    26 as fetched_gameweek_id,
    fixture_id, fixture_gameweek_id, is_home,
    null as difficulty,
    team_h, team_a, raw_data
from archive.player_future_fixtures
where fetched_gameweek_id = 27 and fixture_gameweek_id in (28, 29);