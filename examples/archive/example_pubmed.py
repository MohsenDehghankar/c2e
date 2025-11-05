"""
Example usage of the pubmed.py module for retrieving papers.

This demonstrates how to search PubMed and retrieve paper details.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.pubmed import (
    get_papers,
    search_pubmed,
    fetch_paper_details,
    fetch_pmc_fulltext,
    get_paper_url,
    set_api_key,
)


def setup_api_key_example():
    """Example showing how to set up the NCBI API key."""
    print("=" * 60)
    print("NCBI API Key Setup")
    print("=" * 60)

    # Try to load from .env file first
    print("\nAttempting to load API key from .env file...")
    set_api_key()  # This will load from .env if available

    from Bio import Entrez

    if Entrez.api_key:
        print(f"✓ API key loaded from .env file!")
        print(f"✓ Email: {Entrez.email}")
        print("You can now make up to 10 requests per second.\n")
        return

    print("\nNo .env file found or API key not set.")
    print("To get better rate limits (10 req/s vs 3 req/s),")
    print("get a free API key from:")
    print("https://www.ncbi.nlm.nih.gov/account/settings/")
    print("\nTip: Create a .env file in the project root with:")
    print("  NCBI_API_KEY=your_api_key_here")
    print("  NCBI_EMAIL=your.email@example.com")
    print()

    choice = input("Do you want to enter credentials manually? (y/n): ").strip().lower()
    if choice == "y":
        api_key = input("Enter your NCBI API key: ").strip()
        email = input("Enter your email address: ").strip()

        if api_key and email:
            set_api_key(api_key, email, load_from_env=False)
            print("\n✓ API key configured!")
            print("You can now make up to 10 requests per second.\n")
        elif email:
            set_api_key(None, email, load_from_env=False)
            print("\n✓ Email configured (no API key)")
            print("Limited to 3 requests per second.\n")
    else:
        print("\n⚠ Using default settings (3 requests per second)\n")


def simple_search_example():
    """Simple example of searching and retrieving papers."""
    print("=" * 60)
    print("Simple PubMed Search Example")
    print("=" * 60)

    keyword = "machine learning healthcare"
    top_k = 3

    print(f"\nSearching for: '{keyword}'")
    print(f"Retrieving top {top_k} papers...\n")

    papers = get_papers(keyword, top_k)

    if not papers:
        print("No papers found.")
    else:
        print(f"Found {len(papers)} papers:\n")

        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:3])}")
            if len(paper.authors) > 3:
                print(f"           et al. ({len(paper.authors)} total)")
            print(f"   Journal: {paper.journal}")
            print(f"   Date: {paper.publication_date}")
            print(f"   PMID: {paper.pmid}")
            if paper.doi:
                print(f"   DOI: {paper.doi}")
            if paper.pmc_id:
                print(f"   PMC ID: {paper.pmc_id}")
            if paper.is_free_in_pmc:
                print(f"   ✓ FREE full-text available in PMC!")
            if paper.paper_url:
                print(f"   URL: {paper.paper_url}")
            print(f"   Abstract: {paper.abstract[:150]}...")
            print()


def pmc_fulltext_example():
    """Example showing how to fetch full-text from PMC."""
    print("\n" + "=" * 60)
    print("PMC Full-Text Retrieval Example")
    print("=" * 60)

    # Search for open-access papers
    keyword = "COVID-19 treatment"
    top_k = 5

    print(f"\nSearching for open-access papers on '{keyword}'...")
    papers = get_papers(keyword, top_k)

    # Find papers available in PMC
    pmc_papers = [p for p in papers if p.is_free_in_pmc]

    if not pmc_papers:
        print("\nNo free full-text papers found in this search.")
        print("Try searching for more recent or open-access topics.")
    else:
        print(f"\nFound {len(pmc_papers)} paper(s) with free full-text in PMC:\n")

        for i, paper in enumerate(pmc_papers, 1):
            print(f"{i}. {paper.title}")
            print(f"   PMC ID: {paper.pmc_id}")
            print(f"   Fetching full text...")

            fulltext = fetch_pmc_fulltext(paper.pmc_id)

            if fulltext:
                print(f"   ✓ Full text retrieved ({len(fulltext)} characters)")
                print(f"   Preview: {fulltext[:300]}...\n")
            else:
                print(f"   ✗ Could not retrieve full text\n")


def paper_url_example():
    """Example showing how to get paper URLs."""
    print("\n" + "=" * 60)
    print("Paper URL Generation Example")
    print("=" * 60)

    keyword = "machine learning"
    top_k = 3

    print(f"\nSearching for '{keyword}'...")
    papers = get_papers(keyword, top_k)

    print("\nPaper access URLs:\n")

    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper.title}")
        print(f"   PMID: {paper.pmid}")

        if paper.paper_url:
            print(f"   Primary URL: {paper.paper_url}")

        # Show alternative URLs
        if paper.doi and paper.pmc_id:
            print(f"   Alternative URLs:")
            print(f"     - DOI: https://doi.org/{paper.doi}")
            print(
                f"     - PMC: https://www.ncbi.nlm.nih.gov/pmc/articles/{paper.pmc_id}/"
            )
            print(f"     - PubMed: https://pubmed.ncbi.nlm.nih.gov/{paper.pmid}/")

        if paper.is_free_in_pmc:
            print(f"   ✓ FREE full-text available!")
        else:
            print(f"   ⚠ May require institutional access or payment")

        print()


def search_and_display_abstracts():
    """Example showing how to retrieve and display full abstracts."""
    print("\n" + "=" * 60)
    print("Full Abstract Display Example")
    print("=" * 60)

    keyword = "CRISPR gene editing"
    top_k = 2

    print(f"\nSearching for: '{keyword}'")
    print(f"Retrieving top {top_k} papers...\n")

    papers = get_papers(keyword, top_k)

    for i, paper in enumerate(papers, 1):
        print(f"\nPaper {i}:")
        print("-" * 60)
        print(f"Title: {paper.title}")
        print(f"Authors: {', '.join(paper.authors)}")
        print(f"Journal: {paper.journal} ({paper.publication_date})")
        print(f"\nAbstract:\n{paper.abstract}")
        print("-" * 60)


def search_by_pmid_example():
    """Example showing how to fetch a specific paper by PMID."""
    print("\n" + "=" * 60)
    print("Fetch by PMID Example")
    print("=" * 60)

    # Example PMID (you can replace with any valid PMID)
    pmid = "34426522"  # Example PMID

    print(f"\nFetching paper with PMID: {pmid}...\n")

    try:
        paper = fetch_paper_details(pmid)

        print(f"Title: {paper.title}")
        print(f"Authors: {', '.join(paper.authors)}")
        print(f"Journal: {paper.journal}")
        print(f"Date: {paper.publication_date}")
        if paper.doi:
            print(f"DOI: {paper.doi}")
        print(f"\nAbstract:\n{paper.abstract}")

    except Exception as e:
        print(f"Error: {e}")


def interactive_search():
    """Interactive search allowing user input."""
    print("\n" + "=" * 60)
    print("Interactive PubMed Search")
    print("=" * 60)

    keyword = input("\nEnter search keyword: ").strip()
    if not keyword:
        keyword = "artificial intelligence"
        print(f"Using default keyword: {keyword}")

    top_k_input = input("Enter number of papers to retrieve (default: 5): ").strip()
    top_k = int(top_k_input) if top_k_input else 5

    print(f"\nSearching PubMed for '{keyword}'...")
    print("This may take a moment...\n")

    try:
        papers = get_papers(keyword, top_k)

        if not papers:
            print("No papers found.")
        else:
            print(f"Found {len(papers)} papers:\n")
            print("=" * 60)

            for i, paper in enumerate(papers, 1):
                print(f"\n{i}. {paper.title}")
                print(f"   Authors: {', '.join(paper.authors[:3])}")
                if len(paper.authors) > 3:
                    print(f"           et al. ({len(paper.authors)} total)")
                print(f"   Journal: {paper.journal}")
                print(f"   Date: {paper.publication_date}")
                print(f"   PMID: {paper.pmid}")
                if paper.doi:
                    print(f"   DOI: {paper.doi}")
                if paper.pmc_id:
                    print(f"   PMC ID: {paper.pmc_id}")
                    if paper.is_free_in_pmc:
                        print(f"   ✓ FREE full-text available in PMC!")
                if paper.paper_url:
                    print(f"   URL: {paper.paper_url}")
                print(f"   Abstract: {paper.abstract[:200]}...")

            print("\n" + "=" * 60)

    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main function to run examples."""
    print("\nPubMed API Examples")
    print("=" * 60)

    # Setup API key first
    setup_api_key_example()

    print("\nSelect example to run:")
    print("1. Simple search (machine learning healthcare)")
    print("2. Full abstract display (CRISPR)")
    print("3. Fetch by PMID")
    print("4. PMC full-text retrieval (open-access papers)")
    print("5. Paper URL generation")
    print("6. Interactive search")
    print("7. Run all non-interactive examples")

    choice = input("\nEnter choice (1-7, default: 7): ").strip() or "7"

    if choice == "1":
        simple_search_example()
    elif choice == "2":
        search_and_display_abstracts()
    elif choice == "3":
        search_by_pmid_example()
    elif choice == "4":
        pmc_fulltext_example()
    elif choice == "5":
        paper_url_example()
    elif choice == "6":
        interactive_search()
    elif choice == "7":
        simple_search_example()
        search_and_display_abstracts()
        search_by_pmid_example()
        pmc_fulltext_example()
        paper_url_example()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
