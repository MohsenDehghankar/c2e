"""
Simple PubMed API wrapper for searching and retrieving papers.

Uses the NCBI E-utilities API to search PubMed and fetch article details.
"""

import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time


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
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": keyword,
        "retmax": top_k,
        "retmode": "json",
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])

        return pmids

    except requests.exceptions.RequestException as e:
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
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml",
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()

        # Parse XML response (simple parsing)
        xml_text = response.text

        # Extract title
        title = _extract_xml_tag(xml_text, "ArticleTitle")

        # Extract abstract
        abstract = _extract_xml_tag(xml_text, "AbstractText")
        if not abstract:
            abstract = "No abstract available"

        # Extract authors
        authors = _extract_authors(xml_text)

        # Extract journal
        journal = _extract_xml_tag(xml_text, "Title")  # Journal title

        # Extract publication date
        pub_date = _extract_publication_date(xml_text)

        # Extract DOI
        doi = _extract_doi(xml_text)

        # Extract PMC ID
        pmc_id = _extract_pmc_id(xml_text)

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

    except requests.exceptions.RequestException as e:
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
            # Be nice to NCBI servers - add small delay
            time.sleep(0.34)  # Max 3 requests per second
        except Exception as e:
            print(f"Warning: Could not fetch paper {pmid}: {e}")
            continue

    return papers


# Helper functions for XML parsing
def _extract_xml_tag(xml_text: str, tag: str) -> str:
    """Extract content from an XML tag."""
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"

    start_idx = xml_text.find(start_tag)
    if start_idx == -1:
        return ""

    start_idx += len(start_tag)
    end_idx = xml_text.find(end_tag, start_idx)

    if end_idx == -1:
        return ""

    return xml_text[start_idx:end_idx].strip()


def _extract_authors(xml_text: str) -> List[str]:
    """Extract author names from XML."""
    authors = []
    author_section = xml_text

    while True:
        last_name = _extract_xml_tag(author_section, "LastName")
        fore_name = _extract_xml_tag(author_section, "ForeName")

        if not last_name:
            break

        author_name = f"{fore_name} {last_name}".strip() if fore_name else last_name
        authors.append(author_name)

        # Move past this author
        author_idx = author_section.find("</Author>")
        if author_idx == -1:
            break
        author_section = author_section[author_idx + 9 :]

    return authors if authors else ["Unknown"]


def _extract_publication_date(xml_text: str) -> str:
    """Extract publication date from XML."""
    year = _extract_xml_tag(xml_text, "Year")
    month = _extract_xml_tag(xml_text, "Month")
    day = _extract_xml_tag(xml_text, "Day")

    if year:
        date_parts = [year]
        if month:
            date_parts.append(month)
        if day:
            date_parts.append(day)
        return " ".join(date_parts)

    return "Unknown"


def _extract_doi(xml_text: str) -> Optional[str]:
    """Extract DOI from XML."""
    # Look for DOI in ArticleId elements
    doi_start = xml_text.find('IdType="doi"')
    if doi_start == -1:
        return None

    # Find the ArticleId tag that contains the DOI
    tag_start = xml_text.rfind("<ArticleId", 0, doi_start)
    if tag_start == -1:
        return None

    tag_end = xml_text.find("</ArticleId>", tag_start)
    if tag_end == -1:
        return None

    # Extract DOI value
    content_start = xml_text.find(">", tag_start) + 1
    doi = xml_text[content_start:tag_end].strip()

    return doi if doi else None


def _extract_pmc_id(xml_text: str) -> Optional[str]:
    """Extract PMC ID from XML."""
    # Look for PMC ID in ArticleId elements
    pmc_start = xml_text.find('IdType="pmc"')
    if pmc_start == -1:
        return None

    # Find the ArticleId tag that contains the PMC ID
    tag_start = xml_text.rfind("<ArticleId", 0, pmc_start)
    if tag_start == -1:
        return None

    tag_end = xml_text.find("</ArticleId>", tag_start)
    if tag_end == -1:
        return None

    # Extract PMC ID value
    content_start = xml_text.find(">", tag_start) + 1
    pmc_id = xml_text[content_start:tag_end].strip()

    return pmc_id if pmc_id else None


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
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            "db": "pmc",
            "id": pmc_id.replace("PMC", ""),  # Remove PMC prefix
            "retmode": "xml",
        }

        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()

        # If we get a valid response, it's available
        return "article" in response.text.lower()

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
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            "db": "pmc",
            "id": pmc_id.replace("PMC", ""),  # Remove PMC prefix
            "retmode": "xml",
        }

        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()

        xml_text = response.text

        # Extract all text content from body sections
        fulltext_parts = []

        # Extract abstract
        abstract = _extract_xml_tag(xml_text, "abstract")
        if abstract:
            fulltext_parts.append(f"ABSTRACT:\n{abstract}")

        # Extract body text
        body = _extract_xml_tag(xml_text, "body")
        if body:
            # Simple text extraction - remove XML tags
            import re

            text = re.sub(r"<[^>]+>", " ", body)
            text = re.sub(r"\s+", " ", text).strip()
            fulltext_parts.append(f"\nFULL TEXT:\n{text}")

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
