"""
PubMed API wrapper for searching and retrieving papers.

Uses Biopython's Entrez package to access NCBI E-utilities API.
Requires an API key for better rate limits (10 requests/sec vs 3 requests/sec).
"""

from Bio import Entrez
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time
import os
from dotenv import load_dotenv


# Global settings for Entrez
Entrez.email = "your.email@example.com"  # Required by NCBI
Entrez.api_key = None  # Set this with set_api_key() function
Entrez.tool = "PubMedRetriever"


def set_api_key(api_key: str = None, email: str = None, load_from_env: bool = True):
    """
    Set the NCBI API key and email for Entrez.

    Get a free API key from: https://www.ncbi.nlm.nih.gov/account/settings/

    Args:
        api_key: Your NCBI API key (if None and load_from_env=True, reads from .env)
        email: Your email address (required by NCBI, if None reads from .env)
        load_from_env: If True, attempts to load from .env file

    Environment variables (in .env file):
        NCBI_API_KEY: Your NCBI API key
        NCBI_EMAIL: Your email address

    Example:
        >>> set_api_key("your_api_key_here", "your.email@example.com")
        >>> set_api_key()  # Load from .env file
    """
    # Load from .env file if requested
    if load_from_env and (api_key is None or email is None):
        load_dotenv()
        if api_key is None:
            api_key = os.getenv("NCBI_API_KEY")
        if email is None:
            email = os.getenv("NCBI_EMAIL")

    # Set the values
    if api_key:
        Entrez.api_key = api_key
    if email:
        Entrez.email = email


@dataclass
class PubMedPaper:
    """Container for PubMed paper information."""

    pmid: str
    title: str
    abstract: str
    authors: List[str]
    journal: str
    publication_date: str
    doi: Optional[str] = None
    pmc_id: Optional[str] = None
    is_free_in_pmc: bool = False
    paper_url: Optional[str] = None


def search_pubmed(keyword: str, top_k: int = 10) -> List[str]:
    """
    Search PubMed for papers matching a keyword.

    Args:
        keyword: Search query/keyword
        top_k: Maximum number of papers to retrieve

    Returns:
        List of PubMed IDs (PMIDs) for the top-k matching papers

    Example:
        >>> pmids = search_pubmed("machine learning", top_k=5)
        >>> print(pmids)
        ['12345678', '87654321', ...]
    """
    try:
        handle = Entrez.esearch(db="pubmed", term=keyword, retmax=top_k)
        record = Entrez.read(handle)
        handle.close()

        pmids = record.get("IdList", [])
        return pmids

    except Exception as e:
        raise Exception(f"Error searching PubMed: {str(e)}")


def fetch_paper_details(pmid: str) -> PubMedPaper:
    """
    Fetch detailed information for a single paper by PMID.

    Args:
        pmid: PubMed ID of the paper

    Returns:
        PubMedPaper object with paper details

    Example:
        >>> paper = fetch_paper_details("12345678")
        >>> print(paper.title)
    """
    try:
        handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        records = Entrez.read(handle)
        handle.close()

        if not records.get("PubmedArticle"):
            raise Exception(f"No article found for PMID {pmid}")

        article = records["PubmedArticle"][0]
        medline = article["MedlineCitation"]
        article_data = medline["Article"]

        # Extract title
        title = article_data.get("ArticleTitle", "No title available")

        # Extract abstract
        abstract_list = article_data.get("Abstract", {}).get("AbstractText", [])
        if abstract_list:
            # Handle multiple abstract sections
            if isinstance(abstract_list, list):
                abstract = " ".join(str(section) for section in abstract_list)
            else:
                abstract = str(abstract_list)
        else:
            abstract = "No abstract available"

        # Extract authors
        author_list = article_data.get("AuthorList", [])
        authors = []
        for author in author_list:
            if "LastName" in author:
                fore_name = author.get("ForeName", "")
                last_name = author.get("LastName", "")
                full_name = f"{fore_name} {last_name}".strip()
                authors.append(full_name)
        if not authors:
            authors = ["Unknown"]

        # Extract journal
        journal = article_data.get("Journal", {}).get("Title", "Unknown Journal")

        # Extract publication date
        pub_date_dict = (
            article_data.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
        )
        year = pub_date_dict.get("Year", "")
        month = pub_date_dict.get("Month", "")
        day = pub_date_dict.get("Day", "")
        pub_date = " ".join(filter(None, [year, month, day])) or "Unknown"

        # Extract DOI and PMC ID
        doi = None
        pmc_id = None
        article_ids = article.get("PubmedData", {}).get("ArticleIdList", [])
        for article_id in article_ids:
            if article_id.attributes.get("IdType") == "doi":
                doi = str(article_id)
            elif article_id.attributes.get("IdType") == "pmc":
                pmc_id = str(article_id)

        # Check if available in PMC
        is_free_in_pmc = False
        if pmc_id:
            is_free_in_pmc = check_pmc_availability(pmc_id)

        # Generate paper URL
        paper_url = None
        if doi:
            paper_url = f"https://doi.org/{doi}"
        elif pmc_id:
            paper_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/"

        return PubMedPaper(
            pmid=pmid,
            title=title,
            abstract=abstract,
            authors=authors,
            journal=journal,
            publication_date=pub_date,
            doi=doi,
            pmc_id=pmc_id,
            is_free_in_pmc=is_free_in_pmc,
            paper_url=paper_url,
        )

    except Exception as e:
        raise Exception(f"Error fetching paper {pmid}: {str(e)}")


def get_papers(keyword: str, top_k: int = 10) -> List[PubMedPaper]:
    """
    Search PubMed and retrieve detailed information for top-k papers.

    This is the main function that combines searching and fetching.

    Args:
        keyword: Search query/keyword
        top_k: Maximum number of papers to retrieve

    Returns:
        List of PubMedPaper objects

    Example:
        >>> papers = get_papers("COVID-19 vaccine", top_k=5)
        >>> for paper in papers:
        ...     print(f"{paper.title} - {paper.publication_date}")
    """
    # Search for papers
    pmids = search_pubmed(keyword, top_k)

    if not pmids:
        return []

    # Fetch details for each paper
    papers = []
    for pmid in pmids:
        try:
            paper = fetch_paper_details(pmid)
            papers.append(paper)
            # Rate limiting (with API key: 10 req/s, without: 3 req/s)
            if Entrez.api_key:
                time.sleep(0.11)  # ~10 requests per second
            else:
                time.sleep(0.34)  # ~3 requests per second
        except Exception as e:
            print(f"Warning: Could not fetch paper {pmid}: {e}")
            continue

    return papers


def check_pmc_availability(pmc_id: str) -> bool:
    """
    Check if a paper is available for free in PubMed Central.

    Args:
        pmc_id: PubMed Central ID (e.g., "PMC1234567")

    Returns:
        True if the paper is freely available in PMC, False otherwise
    """
    try:
        # Try to fetch from PMC
        handle = Entrez.efetch(db="pmc", id=pmc_id.replace("PMC", ""), retmode="xml")
        xml_text = handle.read()
        handle.close()

        # If we get a valid response with article content, it's available
        return b"article" in xml_text.lower()

    except Exception:
        return False


def fetch_pmc_fulltext(pmc_id: str) -> Optional[str]:
    """
    Fetch full-text article from PubMed Central.

    Args:
        pmc_id: PubMed Central ID (e.g., "PMC1234567")

    Returns:
        Full-text content as string, or None if not available

    Example:
        >>> fulltext = fetch_pmc_fulltext("PMC1234567")
        >>> if fulltext:
        ...     print(fulltext[:500])
    """
    try:
        handle = Entrez.efetch(db="pmc", id=pmc_id.replace("PMC", ""), retmode="xml")
        xml_text = handle.read()
        handle.close()

        # Convert bytes to string
        if isinstance(xml_text, bytes):
            xml_text = xml_text.decode("utf-8")

        # Simple text extraction - remove XML tags
        import re

        # Extract content between body tags
        body_match = re.search(
            r"<body>(.*?)</body>", xml_text, re.DOTALL | re.IGNORECASE
        )
        abstract_match = re.search(
            r"<abstract>(.*?)</abstract>", xml_text, re.DOTALL | re.IGNORECASE
        )

        fulltext_parts = []

        if abstract_match:
            abstract = re.sub(r"<[^>]+>", " ", abstract_match.group(1))
            abstract = re.sub(r"\s+", " ", abstract).strip()
            fulltext_parts.append(f"ABSTRACT:\n{abstract}")

        if body_match:
            body = re.sub(r"<[^>]+>", " ", body_match.group(1))
            body = re.sub(r"\s+", " ", body).strip()
            fulltext_parts.append(f"\nFULL TEXT:\n{body}")

        if fulltext_parts:
            return "\n\n".join(fulltext_parts)

        return None

    except Exception as e:
        print(f"Error fetching PMC full text: {e}")
        return None


def get_paper_url(
    pmid: str = None, doi: str = None, pmc_id: str = None
) -> Optional[str]:
    """
    Get the URL to access a paper.

    Priority: DOI > PMC > PubMed

    Args:
        pmid: PubMed ID
        doi: Digital Object Identifier
        pmc_id: PubMed Central ID

    Returns:
        URL string to access the paper

    Example:
        >>> url = get_paper_url(doi="10.1038/nature12345")
        >>> print(url)
        https://doi.org/10.1038/nature12345
    """
    if doi:
        return f"https://doi.org/{doi}"
    elif pmc_id:
        return f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/"
    elif pmid:
        return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

    return None
