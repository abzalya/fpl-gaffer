--run in archive schema to see each players first and last gameweek

select
    ph.opta_code,
    ps.web_name,
    ph.season_id,
    COUNT(*) gw_count,
    MIN(ph.gameweek_id) first_gw,
    MAX(ph.gameweek_id) last_gw
from archive.player_gw_history ph
left join (
    select distinct on (opta_code)
        opta_code, web_name
    from archive.player_snapshots
    order by opta_code, fetched_gameweek_id desc
) ps on ps.opta_code = ph.opta_code
group by ph.opta_code, ps.web_name, ph.season_id
order by gw_count asc;