from pathlib import Path

from common.local_kb import format_local_knowledge_results, load_documents, search_local_knowledge


def test_load_documents_reads_markdown_corpus():
    documents = load_documents()
    assert documents
    assert any("KSADK" in doc.title for doc in documents)


def test_search_local_knowledge_returns_ranked_matches():
    results = search_local_knowledge("KSADK 部署 Agent", top_k=2)
    assert results
    assert len(results) <= 2
    assert results[0].score >= results[-1].score


def test_search_local_knowledge_returns_empty_for_unknown_query(tmp_path: Path):
    (tmp_path / "doc.md").write_text("# Alpha\nonly alpha content", encoding="utf-8")
    assert search_local_knowledge("zzzz-not-found", corpus_dir=tmp_path) == []


def test_format_local_knowledge_results_includes_sources():
    text = format_local_knowledge_results(search_local_knowledge("知识库", top_k=1))
    assert "来源:" in text

