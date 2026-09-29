"""
Acceptance tests for the Recipe Box API, derived from SPEC.md.

Each test references the SPEC.md rule (R-number) it verifies.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def valid_recipe_payload(**overrides):
    payload = {
        "title": "Pancakes",
        "ingredients": ["flour", "milk", "eggs"],
        "instructions": ["Mix ingredients", "Cook on a griddle"],
        "prep_minutes": 15,
        "servings": 4,
    }
    payload.update(overrides)
    return payload


def create_recipe(**overrides):
    response = client.post("/recipes", json=valid_recipe_payload(**overrides))
    assert response.status_code == 201
    return response.json()


# ---------------------------------------------------------------------------
# POST /recipes (R12-R16)
# ---------------------------------------------------------------------------


def test_post_recipe_success_returns_201_with_full_recipe():
    # R14: success -> 201 Created with full Recipe object, including server id
    payload = valid_recipe_payload()
    response = client.post("/recipes", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], str) and body["id"] != ""
    assert body["title"] == payload["title"]
    assert body["ingredients"] == payload["ingredients"]
    assert body["instructions"] == payload["instructions"]
    assert body["prep_minutes"] == payload["prep_minutes"]
    assert body["servings"] == payload["servings"]


def test_post_recipe_missing_required_field_returns_422():
    # R12: a required field (servings) missing -> 422
    payload = valid_recipe_payload()
    del payload["servings"]

    response = client.post("/recipes", json=payload)

    assert response.status_code == 422


def test_post_recipe_negative_prep_minutes_returns_422():
    # R13: prep_minutes out of the 0-1440 range -> 422
    payload = valid_recipe_payload(prep_minutes=-5)

    response = client.post("/recipes", json=payload)

    assert response.status_code == 422


def test_post_recipe_empty_ingredients_list_returns_422():
    # R13/R1: ingredients must have at least 1 entry -> 422
    payload = valid_recipe_payload(ingredients=[])

    response = client.post("/recipes", json=payload)

    assert response.status_code == 422


def test_post_recipe_duplicate_title_is_allowed():
    # R15: duplicate title values across recipes are permitted
    first = create_recipe(title="Pancakes")
    response = client.post("/recipes", json=valid_recipe_payload(title="Pancakes"))

    assert response.status_code == 201
    second = response.json()
    assert second["id"] != first["id"]
    assert second["title"] == first["title"] == "Pancakes"


def test_post_recipe_unknown_field_returns_422():
    # R16: a body field outside the Recipe field list -> 422
    payload = valid_recipe_payload()
    payload["notes"] = "family recipe"

    response = client.post("/recipes", json=payload)

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /recipes (R4-R9)
# ---------------------------------------------------------------------------


def test_get_recipes_default_pagination_returns_200():
    # R4, R5, R6: defaults are limit=20, offset=0; response has items/limit/offset/total
    create_recipe(title="Recipe A")

    response = client.get("/recipes")

    assert response.status_code == 200
    body = response.json()
    assert body["limit"] == 20
    assert body["offset"] == 0
    assert isinstance(body["items"], list)
    assert body["total"] >= 1


def test_get_recipes_respects_limit_and_offset():
    # R4, R5, R6: explicit limit/offset control which page of items is returned
    created = [create_recipe(title=f"Recipe {i}") for i in range(3)]

    response = client.get("/recipes", params={"limit": 1, "offset": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["limit"] == 1
    assert body["offset"] == 1
    assert len(body["items"]) == 1
    assert body["total"] >= len(created)


def test_get_recipes_offset_past_total_returns_empty_items():
    # R7: offset at/beyond total -> 200 with items: [] (not an error)
    response = client.get("/recipes", params={"limit": 20, "offset": 1_000_000})

    assert response.status_code == 200
    assert response.json()["items"] == []


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"limit": "abc"}])
def test_get_recipes_invalid_limit_returns_400(params):
    # R8: limit outside 1-100, or non-integer -> 400
    response = client.get("/recipes", params=params)

    assert response.status_code == 400


@pytest.mark.parametrize("params", [{"offset": -1}, {"offset": "abc"}])
def test_get_recipes_invalid_offset_returns_400(params):
    # R8: offset < 0, or non-integer -> 400
    response = client.get("/recipes", params=params)

    assert response.status_code == 400


def test_get_recipes_items_are_full_recipe_objects():
    # R9: items contain the full Recipe object, not a partial/summary form
    created = create_recipe(title="Full Object Recipe")

    response = client.get("/recipes")

    assert response.status_code == 200
    matching = [item for item in response.json()["items"] if item["id"] == created["id"]]
    assert matching, "created recipe should be present in the list"
    assert matching[0] == created


# ---------------------------------------------------------------------------
# GET /recipes/{id} (R10-R11)
# ---------------------------------------------------------------------------


def test_get_recipe_by_id_found_returns_200():
    # R10: existing id -> 200 with the full Recipe object
    created = create_recipe(title="Findable Recipe")

    response = client.get(f"/recipes/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_recipe_by_id_not_found_returns_404():
    # R11: unknown id -> 404
    response = client.get("/recipes/does-not-exist")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /recipes/{id} (R17-R21)
# ---------------------------------------------------------------------------


def test_patch_recipe_updates_only_given_fields():
    # R21: success -> 200, updated field changes, omitted fields stay the same
    created = create_recipe(servings=2)

    response = client.patch(f"/recipes/{created['id']}", json={"servings": 4})

    assert response.status_code == 200
    body = response.json()
    assert body["servings"] == 4
    assert body["title"] == created["title"]
    assert body["ingredients"] == created["ingredients"]
    assert body["instructions"] == created["instructions"]
    assert body["prep_minutes"] == created["prep_minutes"]


def test_patch_recipe_not_found_returns_404():
    # R18: unknown id -> 404
    response = client.patch("/recipes/does-not-exist", json={"servings": 4})

    assert response.status_code == 404


def test_patch_recipe_unknown_field_returns_422():
    # R17: a body key outside title/ingredients/instructions/prep_minutes/servings -> 422
    created = create_recipe()

    response = client.patch(f"/recipes/{created['id']}", json={"id": "new-id"})

    assert response.status_code == 422


def test_patch_recipe_invalid_field_value_returns_422():
    # R19: a present field failing validation (empty title) -> 422
    created = create_recipe()

    response = client.patch(f"/recipes/{created['id']}", json={"title": ""})

    assert response.status_code == 422


def test_patch_recipe_empty_body_is_noop_returns_200():
    # R20: empty body {} -> 200, recipe unchanged
    created = create_recipe()

    response = client.patch(f"/recipes/{created['id']}", json={})

    assert response.status_code == 200
    assert response.json() == created


# ---------------------------------------------------------------------------
# DELETE /recipes/{id} (R22-R24)
# ---------------------------------------------------------------------------


def test_delete_recipe_success_returns_204_and_removes_it():
    # R23: success -> 204 No Content, hard delete
    created = create_recipe(title="Deletable Recipe")

    delete_response = client.delete(f"/recipes/{created['id']}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(f"/recipes/{created['id']}")
    assert get_response.status_code == 404


def test_delete_recipe_not_found_returns_404():
    # R22: unknown id -> 404
    response = client.delete("/recipes/does-not-exist")

    assert response.status_code == 404


def test_delete_recipe_twice_returns_404_second_time():
    # R24: deleting an already-deleted id -> 404, no soft-delete tombstone
    created = create_recipe(title="Double Delete Recipe")

    first = client.delete(f"/recipes/{created['id']}")
    second = client.delete(f"/recipes/{created['id']}")

    assert first.status_code == 204
    assert second.status_code == 404
