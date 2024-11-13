import requests
import time


def fetch_crossref_data():
    url = "https://api.crossref.org/works"
    papers = []
    target_paper_count = 1000  # Number of papers you want
    rows_per_request = 100  # Number of rows to fetch per request
    offset = 0

    while len(papers) < target_paper_count:
        params = {
            "filter": "from-pub-date:2024-01-01,until-pub-date:2024-12-31",
            "rows": rows_per_request,
            "offset": offset
        }

        response = requests.get(url, params=params)
        data = response.json()

        # Get the list of items
        items = data['message'].get('items', [])

        # If no more items are returned, break the loop
        if not items:
            print("No more results available.")
            break

        # Extract data from the API response
        for item in items:
            # Extract authors with both family and given names
            authors = []
            for author in item.get("author", []):
                family = author.get("family")
                given = author.get("given")
                if family and given:
                    authors.append(f"{given} {family}")
                elif family:
                    authors.append(family)
                elif given:
                    authors.append(given)

            # Extract other fields
            title = item.get("title", [None])[0]
            keywords = item.get("subject", [])
            subject_area = item.get("container-title", [None])[0]
            published_date = item.get(
                "published-print", {}).get("date-parts", [[None]])[0]

            # Check if all required fields are non-empty
            if title and authors and keywords and subject_area and published_date:
                paper = {
                    "title": title,
                    "authors": authors,
                    "keywords": keywords,
                    "subject_area": subject_area,
                    "published_date": published_date
                }
                papers.append(paper)

            # Stop if we've reached the target number of papers
            if len(papers) >= target_paper_count:
                break

        # Update offset for pagination
        offset += rows_per_request

        # Avoid hitting rate limits
        time.sleep(1)

    return papers


# Fetch and print or save the data
papers = fetch_crossref_data()
print(papers)
print(f"Collected {len(papers)} papers.")
