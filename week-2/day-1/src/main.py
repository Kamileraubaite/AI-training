from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()

_recipes: dict[str, "Recipe"] = {}

IngredientStr = Annotated[str, Field(min_length=1, max_length=200)]
InstructionStr = Annotated[str, Field(min_length=1, max_length=500)]


class Recipe(BaseModel):
    id: str
    title: str
    ingredients: list[str]
    instructions: list[str]
    prep_minutes: int
    servings: int


class RecipeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=120)
    ingredients: list[IngredientStr] = Field(min_length=1)
    instructions: list[InstructionStr] = Field(min_length=1)
    prep_minutes: int = Field(ge=0, le=1440)
    servings: int = Field(ge=1, le=100)


class RecipePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=120)
    ingredients: list[IngredientStr] | None = Field(default=None, min_length=1)
    instructions: list[InstructionStr] | None = Field(default=None, min_length=1)
    prep_minutes: int | None = Field(default=None, ge=0, le=1440)
    servings: int | None = Field(default=None, ge=1, le=100)


def _parse_pagination(limit_raw: str, offset_raw: str) -> tuple[int, int]:
    try:
        limit = int(limit_raw)
        offset = int(offset_raw)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="limit and offset must be integers")

    if not (1 <= limit <= 100):
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be >= 0")

    return limit, offset


@app.get("/recipes")
def list_recipes(limit: str = Query(default="20"), offset: str = Query(default="0")):
    parsed_limit, parsed_offset = _parse_pagination(limit, offset)

    all_recipes = list(_recipes.values())
    page = all_recipes[parsed_offset : parsed_offset + parsed_limit]

    return {
        "items": [recipe.model_dump() for recipe in page],
        "limit": parsed_limit,
        "offset": parsed_offset,
        "total": len(all_recipes),
    }


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: str):
    recipe = _recipes.get(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404)
    return recipe.model_dump()


@app.post("/recipes", status_code=201)
def create_recipe(payload: RecipeCreate):
    recipe = Recipe(id=uuid4().hex, **payload.model_dump())
    _recipes[recipe.id] = recipe
    return recipe.model_dump()


@app.patch("/recipes/{recipe_id}")
def patch_recipe(recipe_id: str, payload: RecipePatch):
    recipe = _recipes.get(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404)

    updates = payload.model_dump(exclude_unset=True)
    updated = recipe.model_copy(update=updates)
    _recipes[recipe_id] = updated
    return updated.model_dump()


@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: str):
    if recipe_id not in _recipes:
        raise HTTPException(status_code=404)
    del _recipes[recipe_id]
    return Response(status_code=204)
