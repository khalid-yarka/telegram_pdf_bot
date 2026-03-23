# telegram_pdf_bot/state_management.py
# Functions for managing user states (registration, upload, search, etc.)

import json
import database as db
from config import DEBUG

def set_user_state(user_id, state, data=None):
    """Set the user's current state and optional data."""
    db.set_user_state(user_id, state, data)
    if DEBUG:
        print(f"📌 State set for {user_id}: {state}")

def get_user_state(user_id):
    """Return (state, data) for the user, or (None, None) if none."""
    return db.get_user_state(user_id)

def clear_user_state(user_id):
    """Clear the user's state."""
    db.clear_user_state(user_id)
    if DEBUG:
        print(f"🗑️ State cleared for {user_id}")

def get_state_data(user_id):
    """Return only the data part of the user's state."""
    _, data = get_user_state(user_id)
    return data

def is_state_active(user_id, expected_state=None):
    """Check if user has a state. If expected_state is given, check if it matches."""
    state, _ = get_user_state(user_id)
    if state is None:
        return False
    if expected_state and state != expected_state:
        return False
    return True

def update_state_data(user_id, data_update):
    """Update only the data part of the user's state without changing the state name."""
    current_state, current_data = get_user_state(user_id)
    if current_state:
        if current_data is None:
            current_data = {}
        current_data.update(data_update)
        set_user_state(user_id, current_state, current_data)