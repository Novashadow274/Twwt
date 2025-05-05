# utils.py

def is_admin_or_owner(user_id, chat_member):
    return chat_member.status in ("administrator", "creator")
