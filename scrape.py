import random
import time
from scholarly import scholarly

# A set of broad keywords that may yield diverse research papers
broad_keywords = ["science", "technology",
                  "research", "study", "innovation", "2024"]

# Storage for collected papers
papers = []
target_paper_count = 10

while len(papers) < target_paper_count:
    # Choose a random broad keyword
    keyword = random.choice(broad_keywords)

    # Search for papers with this keyword, focusing on 2024 publications
    search_query = scholarly.search_pubs(f"{keyword}")

    try:
        for _ in range(10):  # Fetch a few papers per keyword to avoid rate-limiting
            paper = next(search_query)
            # Check publication year directly from the dictionary
            if paper.get("pub_year") == "2024":
                papers.append(paper)

            # Stop if we’ve reached the target
            if len(papers) >= target_paper_count:
                break

        # Random delay to avoid rate limiting
        time.sleep(random.uniform(5, 10))

    except StopIteration:
        # Move to the next keyword if no more results
        continue

print(f"Collected {len(papers)} papers.")
# Optionally save to a CSV or JSON file if needed

print(papers[0])
