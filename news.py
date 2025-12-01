import requests

URL = "https://newsapi.org/v2/top-headlines?country=us&apiKey=68d7d515d90f49e99b353043d1327513"

def get_headlines():
    try:
        response = requests.get(URL)
        data = response.json()
    except Exception as e:
        print("News request error:", e)
        return []

    if data.get("status") != "ok":
        print("News API error:", data)
        return []

    titles = []
    for article in data.get("articles", []):
        title = article.get("title")
        if title:
            titles.append(title)

    return titles
