#Loading User input
#Version: 1.0.0

def _get_active_chip(user_input):
    # Get the chips dict
    chips = user_input["chips"]
    # Find which one is True
    active_chips = [chip for chip, active in chips.items() if active]
    return active_chips[0] if active_chips else None

def _existing_squad(user_input):
    existing_squad = user_input["existing_squad"] or []
    existing_opta_codes = {p["opta_code"] for p in existing_squad}
    locked_players = [p["opta_code"] for p in existing_squad if p.get("locked")]
    return existing_opta_codes, locked_players

def load_user_input(user_input):
    existing_opta_codes, locked_players = _existing_squad(user_input)
    chip = _get_active_chip(user_input)
    bank = user_input["bank"]
    free_transfers = user_input["free_transfers"]
    horizon = user_input["horizon"]
    return existing_opta_codes, locked_players, chip, bank, free_transfers, horizon