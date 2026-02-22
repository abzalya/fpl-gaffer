#fetched_gameweek_id is the CURRENT GAMEWEEK. 
fetched_gameweek_id = next((event['id'] for event in data['events'] if event['is_current']), None)
opta_code = #extract an optacode must be done to insert later into the elemnt summary tables. 
season_id = 25