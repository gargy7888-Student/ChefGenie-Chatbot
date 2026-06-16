from serpapi import GoogleSearch

def web_search(query, serp_api_key):
    params = {
        "q": query,
        "api_key": serp_api_key,
        "num": 3
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    organic = results.get("organic_results", [])

    if not organic:
        return "Sorry, I couldn't find anything on the web."
    
    snippets = []
    for result in organic[:3]:
        snippet = result.get("snippet", "")
        if snippet:
            snippets.append(snippet)
    return " ".join(snippets)