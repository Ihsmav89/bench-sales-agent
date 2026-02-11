"""Tests for the X-ray search engine."""

from bench_sales_agent.search.xray_engine import (
    ConsultantSearchParams,
    SearchPlatform,
    XRaySearchEngine,
)


def test_generate_all_queries_returns_results():
    engine = XRaySearchEngine()
    params = ConsultantSearchParams(
        job_title="Java Developer",
        primary_skills=["Java", "Spring Boot", "Microservices", "AWS"],
        location="Dallas, TX",
        remote_ok=True,
        visa_status="H1B",
    )
    queries = engine.generate_all_queries(params)
    assert len(queries) > 10
    platforms = {q.platform for q in queries}
    assert SearchPlatform.LINKEDIN in platforms
    assert SearchPlatform.DICE in platforms
    assert SearchPlatform.INDEED in platforms


def test_queries_include_job_title():
    engine = XRaySearchEngine()
    params = ConsultantSearchParams(
        job_title="Data Engineer",
        primary_skills=["Python", "Spark", "AWS", "Snowflake"],
    )
    queries = engine.generate_all_queries(params)
    title_in_query = [q for q in queries if "Data Engineer" in q.query]
    assert len(title_in_query) > 5


def test_location_included_when_provided():
    engine = XRaySearchEngine()
    params = ConsultantSearchParams(
        job_title="React Developer",
        primary_skills=["React", "TypeScript", "Node.js"],
        location="Chicago, IL",
    )
    queries = engine.generate_all_queries(params)
    location_queries = [q for q in queries if "Chicago" in q.query]
    assert len(location_queries) >= 3


def test_hotlist_queries():
    engine = XRaySearchEngine()
    params = ConsultantSearchParams(
        job_title="Python Developer",
        primary_skills=["Python", "Django", "AWS"],
    )
    hotlist = engine.generate_hotlist_queries(params)
    assert len(hotlist) >= 1
    assert any("hotlist" in q.query.lower() for q in hotlist)


def test_role_synonyms():
    engine = XRaySearchEngine()
    synonyms = engine.get_role_synonyms("java developer")
    assert len(synonyms) > 1
    assert "java developer" in synonyms

    unknown = engine.get_role_synonyms("Quantum Computing Specialist")
    assert unknown == ["Quantum Computing Specialist"]


def test_queries_are_c2c_only_no_w2():
    """Verify all queries use C2C/corp-to-corp terms and never W2."""
    engine = XRaySearchEngine()
    params = ConsultantSearchParams(
        job_title="Java Developer",
        primary_skills=["Java", "Spring Boot", "AWS"],
        location="Dallas, TX",
    )
    queries = engine.generate_all_queries(params)
    hotlist = engine.generate_hotlist_queries(params)
    for q in queries + hotlist:
        assert '"w2"' not in q.query.lower(), f"W2 found in query: {q.query}"
        # Ensure C2C terms are present in job search queries
    c2c_queries = [q for q in queries if "c2c" in q.query.lower() or "corp to corp" in q.query.lower()]
    assert len(c2c_queries) >= 5


def test_all_queries_have_search_urls():
    engine = XRaySearchEngine()
    params = ConsultantSearchParams(
        job_title="DevOps Engineer",
        primary_skills=["AWS", "Kubernetes", "Terraform", "Docker"],
        location="Seattle, WA",
    )
    queries = engine.generate_all_queries(params)
    for q in queries:
        assert q.search_url.startswith("https://www.google.com/search?q=")
        assert q.description
        assert q.platform
