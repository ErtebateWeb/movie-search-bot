from collections import defaultdict

def group_movies(rows):
    """
    Group versions of same movie together.
    """

    grouped = defaultdict(list)

    for r in rows:
        key = f"{r['title']}|{r['year']}"
        grouped[key].append(r)

    return grouped