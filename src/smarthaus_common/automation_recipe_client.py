from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_REGISTRY_PATH = (
    Path(__file__).resolve().parents[2] / "registry" / "cross_workload_automation_recipes_v2.yaml"
)


class AutomationRecipeClient:
    """Deterministic local recipe catalog for cross-workload automation patterns."""

    def __init__(self, registry_path: Path | None = None) -> None:
        self._registry_path = registry_path or _REGISTRY_PATH
        raw = yaml.safe_load(self._registry_path.read_text(encoding="utf-8")) or {}
        recipes = raw.get("recipes") or []
        self._recipes: list[dict[str, Any]] = [item for item in recipes if isinstance(item, dict)]

    @staticmethod
    def _recipe_summary(recipe: dict[str, Any]) -> dict[str, Any]:
        return {
            "recipeId": recipe.get("recipeId"),
            "title": recipe.get("title"),
            "summary": recipe.get("summary"),
            "departments": list(recipe.get("departments") or []),
            "primaryPersonas": list(recipe.get("primaryPersonas") or []),
            "workloads": list(recipe.get("workloads") or []),
            "riskClass": recipe.get("riskClass"),
            "approvalProfile": recipe.get("approvalProfile"),
            "stepCount": len(recipe.get("steps") or []),
        }

    def list_recipes(
        self,
        *,
        department: str | None = None,
        persona: str | None = None,
        workload: str | None = None,
        top: int = 50,
    ) -> list[dict[str, Any]]:
        recipes = self._recipes
        if department:
            recipes = [
                recipe for recipe in recipes if department in (recipe.get("departments") or [])
            ]
        if persona:
            recipes = [
                recipe for recipe in recipes if persona in (recipe.get("primaryPersonas") or [])
            ]
        if workload:
            recipes = [recipe for recipe in recipes if workload in (recipe.get("workloads") or [])]
        bounded_top = min(max(1, top), 100)
        return [self._recipe_summary(recipe) for recipe in recipes[:bounded_top]]

    def get_recipe(self, recipe_id: str) -> dict[str, Any]:
        for recipe in self._recipes:
            if recipe.get("recipeId") == recipe_id:
                return recipe
        raise KeyError(f"Unknown automation recipe: {recipe_id}")
