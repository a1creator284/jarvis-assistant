import requests

URL = "https://newsapi.org/v2/top-headlines?country=us&apiKey=68d7d515d90f49e99b353043d1327513"

def get_headlines():
    try:
        res = requests.get(URL)
        data = res.json()
    except Exception:
        return []

    if data.get("status") != "ok":
        return []

    titles = []
    for article in data.get("articles", []):
        title = article.get("title")
        if title:
            titles.append(title)
    return titles
