import urllib.parse

def parse_query(query_string: str) -> dict[str, str]:
    query = {
        key.decode(): [v.decode() for v in value] # type: ignore
        for key, value in urllib.parse.parse_qs(query_string).items() # честно взято из чата :)
    }

    return { # type: ignore
        key: value[0] if len(value) == 1 else value
        for key, value in query.items()
    }
