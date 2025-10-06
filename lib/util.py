

def truncateUtf8(text, limit=128):
    if not isinstance(text, str):
        return text
    encoded = text.encode('utf-8')
    if len(encoded) <= limit:
        return text
    truncated = encoded[:limit]
    # Ensure we don’t cut in the middle of a UTF-8 character
    while True:
        try:
            decoded = truncated.decode('utf-8')
            break
        except UnicodeDecodeError:
            truncated = truncated[:-1]
    return decoded + "..."


