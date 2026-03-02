import json
from datetime import datetime, timezone

# List of your specific files
FILES = ['Userdb.json', 'fglp.json', 'scooby.json']

def clean_files():
    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now() # Used for the DD-MM-YYYY format comparison

    for filepath in FILES:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Skipping {filepath} - file not found.")
            continue
        except json.JSONDecodeError:
            print(f"Skipping {filepath} - invalid JSON format.")
            continue

        changed = False

        # --- SCENARIO A: Array format with DD-MM-YYYY dates ---
        if isinstance(data, list):
            valid_entries = []
            for entry in data:
                expiry_str = entry.get('expirydate')
                if expiry_str:
                    try:
                        expiry_date = datetime.strptime(expiry_str, "%d-%m-%Y")
                        # Compare dates (ignoring time)
                        if expiry_date.date() >= now_local.date():
                            valid_entries.append(entry)
                        else:
                            print(f"[{filepath}] Removed expired key: {entry.get('key')}")
                            changed = True
                    except ValueError:
                        print(f"[{filepath}] Invalid date format: {expiry_str}")
                        valid_entries.append(entry)
                else:
                    valid_entries.append(entry)
            
            if changed:
                data = valid_entries

        # --- SCENARIO B: Dictionary format with ISO dates ---
        elif isinstance(data, dict) and 'keys' in data:
            valid_keys = []
            for entry in data['keys']:
                expiry_str = entry.get('expiry', '').replace('Z', '+00:00')
                if expiry_str:
                    try:
                        expiry_date = datetime.fromisoformat(expiry_str)
                        if expiry_date > now_utc:
                            valid_keys.append(entry)
                        else:
                            print(f"[{filepath}] Removed expired key: {entry.get('key')}")
                            changed = True
                    except ValueError:
                        print(f"[{filepath}] Invalid date format: {expiry_str}")
                        valid_keys.append(entry)
                else:
                    valid_keys.append(entry)
            
            if changed:
                data['keys'] = valid_keys
        
        # --- Save the file only if changes were made ---
        if changed:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[{filepath}] Cleanup complete and saved.")
        else:
            print(f"[{filepath}] No expired keys found.")

if __name__ == "__main__":
    clean_files()
