"""Unit tests for forctx query parser."""

import pytest

from pvrclawk.membank.core.forctx.parser import parse_forctx_query


def test_parse_bracket_and_tag():
    """[phrase one] #tag1 yields tag tag1 and phrase 'phrase one'."""
    tags, phrases = parse_forctx_query("[phrase one] #tag1")
    assert tags == ["tag1"]
    assert phrases == ["phrase one"]


def test_parse_bracket_aware_splitting():
    """Space inside brackets is preserved."""
    tags, phrases = parse_forctx_query("[auth flow] [another phrase]")
    assert "auth flow" in phrases
    assert "another phrase" in phrases
    assert len(phrases) == 2


def test_parse_bare_words_as_content():
    """Bare words after extraction become single-word content phrases."""
    tags, phrases = parse_forctx_query("#task auth")
    assert tags == ["task"]
    assert "auth" in phrases


def test_parse_tag_only():
    """#only yields one tag, no phrases."""
    tags, phrases = parse_forctx_query("#only")
    assert tags == ["only"]
    assert phrases == []


def test_parse_phrase_only():
    """[only phrase] yields one phrase, no tags."""
    tags, phrases = parse_forctx_query("[only phrase]")
    assert tags == []
    assert phrases == ["only phrase"]


def test_parse_empty():
    """Empty query yields empty lists."""
    tags, phrases = parse_forctx_query("")
    assert tags == []
    assert phrases == []


def test_parse_multiple_tags():
    """Multiple #tokens become tag list."""
    tags, phrases = parse_forctx_query("#task #auth #membank")
    assert tags == ["task", "auth", "membank"]
    assert phrases == []
