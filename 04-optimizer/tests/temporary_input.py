#setting values:
#0 will fake a new team/new palyer default. horizon is 3 (will get pulled down to 1 tho due to ML block)
#1 exisitng squad is here, chips are false, simulate normal optimization
#2 existing squad & free_hit = true - pull horizon to 1 & should result in ignoring the locked players. or should it not idk ?
def adjust_user_input(setting: int):
    # Input API structure:
    UserInputPlaceholder = {
        "existing_squad": [
            # GK
            {"opta_code": 200720, "locked": True},   # Kelleher
            {"opta_code": 67089,  "locked": False},   # Dúbravka
            # DEF
            {"opta_code": 445122, "locked": False},    # Timber
            {"opta_code": 226597, "locked": True},   # Gabriel
            {"opta_code": 247348, "locked": False},   # Muñoz
            {"opta_code": 209036, "locked": False},   # Guéhi
            {"opta_code": 437499, "locked": False},   # Lacroix
            # MID
            {"opta_code": 446008, "locked": False},    # Mbeumo
            {"opta_code": 141746, "locked": False},   # B. Fernandes
            {"opta_code": 437730, "locked": True},   # Semenyo
            {"opta_code": 108413, "locked": False},   # Hughes
            {"opta_code": 448047, "locked": False},   # Enzo Fernández
            # FWD
            {"opta_code": 510663, "locked": False},    # Ekitiké
            {"opta_code": 475168, "locked": True},   # João Pedro
            {"opta_code": 102057, "locked": False},   # Raúl Jiménez
        ],
        "chips": {
            "free_hit": False,
            "wildcard": False,
            "bench_boost": False,
            "triple_captain": False,
        },
        "bank": 0.4,
        "free_transfers": 3,
        "horizon": 3,
    }

    match setting:
        case 0:
            UserInputPlaceholder["existing_squad"] = None
            UserInputPlaceholder["bank"] = 100
            return UserInputPlaceholder
        case 1:
            return UserInputPlaceholder
        case 2:
            UserInputPlaceholder["chips"]["free_hit"] = True
            return UserInputPlaceholder

#how to use
#user_input = adjust_user_input(0)
