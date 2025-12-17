def classify_commit(message):
    if not message:
        return 'Other'
    msg = message.lower()
    if msg.startswith('merge'): return 'Merge'
    if any(x in msg for x in ['feat', 'add', 'new', 'create']): return 'Feature'
    if any(x in msg for x in ['fix', 'bug', 'resolve', 'patch', 'hotfix']): return 'Bugfix'
    if any(x in msg for x in ['chore', 'refactor', 'style', 'cleanup', 'remove']): return 'Refactor'
    if any(x in msg for x in ['doc', 'readme']): return 'Docs'
    return 'Other'