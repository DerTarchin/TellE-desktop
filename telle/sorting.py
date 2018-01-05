def split_relevant(query, results):
    # At least one keyword must be in the title
    def relevant(e, keywords):
        name = ""

        name = e.get("name", None)
        if name == None:
            name = e.get("title", "")

        name = name.lower()

        for keyword in keywords:
            if keyword in name:
                return True

        return False
    
    keywords = [e.lower() for e in query.split(" ") if len(e) > 0]

    for e in results:
        e["relevant"] = relevant(e, keywords)

def sign(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0

def compare_results(query, r1, r2):
    relevant_cmp = int(r2["relevant"]) - int(r1["relevant"])
    if relevant_cmp != 0:
        return relevant_cmp
    else:
        e1 = title_cmp(r1["title"], query)
        e2 = title_cmp(r2["title"], query)
        e_cmp = e1 - e2

        if e_cmp != 0:
            return e_cmp
        else:
            r1_year = r1.get("year", 0)
            r1_year = 0 if r1_year == None else r1_year
            r2_year = r2.get("year", 0)
            r2_year = 0 if r2_year == None else r2_year
            year_cmp = r2_year - r1_year

            if year_cmp != 0:
                return year_cmp
            else:
                return sign(r2.get("score", 0) - r1.get("score", 0))
                    
# From Professor Kosbies notes on recursion
def memoized(f):
    import functools
    cachedResults = dict()
    @functools.wraps(f)
    def wrapper(*args):
        if args not in cachedResults:
            cachedResults[args] = f(*args)
        return cachedResults[args]
    return wrapper


def substitute(x, y):
    if x == y:
        return 0
    else:
        return 2

@memoized
def title_cmp(query, title):
    i = len(title);
    j = len(query)

    if i == 0:
        return j
    elif j == 0:
        return i
    else:
        return(min(title_cmp(query, title[:i-1]) + 1,
                   title_cmp(query[:j-1], title) + 1,
                   title_cmp(query[:j-1], title[:i-1]) + substitute(query[j-1], title[i-1])))


