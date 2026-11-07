# --- DYNAMIC CHARACTER LOADER (FORCE PURGE FIX) ---
def load_dynamic_player_class(selected_character=None):
    char_name = None

    # Check root directory first, then UI/ folder
    json_path = os.path.join(BASE_DIR, "player_data.json")
    if not os.path.exists(json_path):
        json_path = os.path.join(BASE_DIR, "UI", "player_data.json")

    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                char_name = (
                    data.get("selected_character")
                    or data.get("character")
                    or data.get("current_player")
                )
        except Exception as err:
            print(f"[MAIN] JSON read error: {err}")

    if not char_name and selected_character:
        char_name = selected_character

    if not char_name:
        char_name = "will"

    char_name = str(char_name).lower().strip()

    char_map = {
        "will": "will_move",
        "mike": "mike_move",
        "eleven": "el_move",
        "el": "el_move",
        "dustin": "dustin_move",
        "lucas": "lucas_move",
        "max": "max_move",
    }

    module_name = char_map.get(char_name, f"{char_name}_move")

    print(f"\n==========================================")
    print(
        f" [DYNAMIC LOAD] LOADING CHARACTER: {char_name.upper()} ({module_name}.py)"
    )
    print(f"==========================================\n")

    # FORCE CACHE PURGE: Hard reset module cache to prevent fallback to Will
    if module_name in sys.modules:
        del sys.modules[module_name]

    try:
        mod = importlib.import_module(module_name)
        runner_cls = getattr(mod, "PlayerRunner")
        return runner_cls
    except Exception as err:
        print(
            f"[DYNAMIC LOAD WARNING] Could not import '{module_name}' ({err}). Falling back to 'will_move'."
        )
        try:
            if "will_move" in sys.modules:
                del sys.modules["will_move"]
            mod = importlib.import_module("will_move")
            return getattr(mod, "PlayerRunner")
        except Exception as fatal_err:
            print(
                f"[CRITICAL ERROR] Failed to load fallback character: {fatal_err}"
            )
            sys.exit(1)