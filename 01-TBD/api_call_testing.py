import requests
import pandas as pd

def export_full_fpl_data(target_web_name="Raya"):
    # --- 1. Fetch Bootstrap Static Data ---
    print("Fetching Bootstrap Static data...")
    base_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    bootstrap_data = requests.get(base_url).json()

    # A. ALL Events (Gameweeks 1-38)
    # This includes deadlines, average scores, and chip usage stats
    events_df = pd.DataFrame(bootstrap_data['events'])
    events_df.to_csv('all_gameweeks_1_38.csv', index=False)

    # B. All Teams
    teams_df = pd.DataFrame(bootstrap_data['teams'])
    teams_df.to_csv('all_teams.csv', index=False)

    # C. David Raya's Snapshot
    elements_df = pd.DataFrame(bootstrap_data['elements'])
    raya_static_df = elements_df[elements_df['web_name'] == target_web_name]
    
    if raya_static_df.empty:
        print(f"Player {target_web_name} not found!")
        return
    
    raya_static_df.to_csv('raya_bootstrap_snapshot.csv', index=False)

    # Get Raya's ID for the summary call
    raya_id = raya_static_df.iloc[0]['id']
    print(f"Found {target_web_name} (ID: {raya_id}). Fetching full history...")

    # --- 2. Fetch Element Summary Data ---
    summary_url = f"https://fantasy.premierleague.com/api/element-summary/{raya_id}/"
    summary_data = requests.get(summary_url).json()

    # D. Fixtures (Upcoming games)
    pd.DataFrame(summary_data['fixtures']).to_csv('raya_future_fixtures.csv', index=False)

    # E. History (Current Season - Game by Game)
    pd.DataFrame(summary_data['history']).to_csv('raya_season_history_by_gw.csv', index=False)

    # F. History Past (Previous Seasons - Totals)
    pd.DataFrame(summary_data['history_past']).to_csv('raya_previous_years_totals.csv', index=False)

    print("\nCSV Exports Complete!")

if __name__ == "__main__":
    export_full_fpl_data("Raya")