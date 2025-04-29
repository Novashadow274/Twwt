from config import HEADLINE_NAME, SOURCE_HASHTAG

def format_message(username: str, text: str) -> str:
    display_name = HEADLINE_NAME.get(username, username)
    hashtag = SOURCE_HASHTAG.get(username, "")
    return (
        f"**{display_name}🚨**\n"
        f"{text.strip()}\n"
        f"{'🔗Source ' + hashtag if hashtag else '🔗Source'}"
    )
