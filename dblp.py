import requests

def fetch_dblp_data(query, max_results=5):
    base_url = "https://dblp.org/search/publ/api"
    params = {
        "q": "query",
        "h": max_results,
        "format": "json"
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to fetch data. HTTP Status code: {response.status_code}")
        return None

query = "Alan Turing"
dblp_data = fetch_dblp_data("computer")