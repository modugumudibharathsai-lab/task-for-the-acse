"""
Unit tests verifying campus navigation and spatial direction routing.
Ensures 'where is N-Block?' and other location queries resolve to MAP capability
with Answer-First direct walking directions and interactive navigation cards,
and never get confounded with Student Services / Bonafide requests.
"""

import pytest
from app.agent.capability_registry import find_matching_capability
from app.agent.universal_nlu import UniversalNLU
from app.agent.nlu_engine import NLUEngine
from app.agent.tool_registry import ToolRegistry, CampusGraphService


def test_campus_graph_resolve_nodes():
    assert CampusGraphService.resolve_node_id("where is N-Block?") == "N_BLOCK"
    assert CampusGraphService.resolve_node_id("where is n block") == "N_BLOCK"
    assert CampusGraphService.resolve_node_id("where is nblock") == "N_BLOCK"
    assert CampusGraphService.resolve_node_id("where is u-block") == "U_BLOCK"
    assert CampusGraphService.resolve_node_id("where is A-Block?") == "A_BLOCK"
    assert CampusGraphService.resolve_node_id("where is H-Block?") == "H_BLOCK"
    assert CampusGraphService.resolve_node_id("ntr library") == "NTR_LIBRARY"
    assert CampusGraphService.resolve_node_id("mhp canteen") == "MHP_CANTEEN"
    assert CampusGraphService.resolve_node_id("convocation hall") == "CONVOCATION_HALL"
    assert CampusGraphService.resolve_node_id("where is the mess") == "VIGNAN_VIHAR"


def test_find_matching_capability_spatial():
    queries = [
        "where is N-Block?",
        "where is n block",
        "where is u-block",
        "where is A-Block?",
        "how to reach convocation hall",
        "directions to ntr library",
        "where is mhp canteen",
        "where is the mess",
        "where is pharmacy block",
        "campus map"
    ]
    for q in queries:
        cap = find_matching_capability(q)
        assert cap is not None, f"Expected matching capability for '{q}'"
        assert cap["feature_id"] == "map", f"Expected 'map' for '{q}', got '{cap['feature_id']}'"


def test_nlu_engine_where_is_n_block():
    res = NLUEngine.classify_and_reason(None, "where is N-Block?", [], {})
    assert res is not None
    assert res["category"] == "MAP"
    assert "N-Block" in res["content"]
    assert "Computer Science" in res["content"]
    assert "Turn-by-Turn Walking Route" in res["content"]
    assert "240" in res["content"]

    # Must have navigation action and card
    assert res["action"]["type"] == "navigate"
    assert res["action"]["target"] == "map"
    assert res["action"]["route"] == "/?tab=map"
    assert res["structured_card"]["type"] == "navigation"
    assert res["structured_card"]["actionIntent"] == "navigate:map"

    # Strictly verify NO false student services text
    assert "Bonafide" not in res["content"]
    assert "ID Card Replacement" not in res["content"]
    assert "services" != res.get("redirect_path")


def test_nlu_engine_other_blocks():
    test_cases = [
        ("where is u-block", "U-Block", "Law"),
        ("where is A-Block?", "A-Block", "Freshers"),
        ("how do i get to H-Block from main gate", "H-Block", "Electronics"),
        ("where is the mess", "Vignan Vihar", "hostel"),
        ("where is mhp canteen", "MHP Campus Canteen", "food court")
    ]
    for query, expected_name, expected_keyword in test_cases:
        res = NLUEngine.classify_and_reason(None, query, [], {})
        assert res["category"] == "MAP"
        assert expected_name in res["content"]
        assert expected_keyword.lower() in res["content"].lower()
        assert res["action"]["target"] == "map"

