def human_friendly_cmp(a, b):
    if (a.startswith('priority:')
        and not b.startswith('priority:')):
        return -1
    elif (not a.startswith('priority:')
          and b.startswith('priority:')):
        return 1
    elif (':' in a
          and ':' not in b):
        return 1
    elif (':' not in a
          and ':' in b):
        return -1
    else:
        return cmp(a, b)

def human_friendly_tagsort(tags):
    """
    Sort the tags in a way that makes sense to humans in context of a
    bug.

    @param tags: tags to sort in any order

    @type tags: iterable of str
    """
    return sorted(tags, cmp=human_friendly_cmp)
