"""Serialization service for API SketchPad."""

import json
from pathlib import Path

from ..models.interaction import Interaction


class SerializationService:
    """Handles JSON serialization/deserialization of interactions."""

    @staticmethod
    def serialize_interactions(interactions: list[Interaction]) -> tuple[bool, str]:
        """Serialize interactions to JSON string."""
        try:
            data = {
                "version": "1.0",
                "interactions": [
                    interaction.model_dump() for interaction in interactions
                ],
            }
            return True, json.dumps(data, indent=2)
        except (TypeError, ValueError) as e:
            return False, f"Serialization failed: {e!s}"

    @staticmethod
    def deserialize_interactions(
        json_str: str,
    ) -> tuple[bool, list[Interaction], str | None]:
        """Deserialize interactions from JSON string."""
        try:
            data = json.loads(json_str)
            interactions = []

            if not isinstance(data, dict) or "interactions" not in data:
                return False, [], "Invalid JSON structure - missing 'interactions' key"

            for interaction_data in data["interactions"]:
                try:
                    interaction = Interaction(**interaction_data)
                    interactions.append(interaction)
                except (TypeError, ValueError) as e:
                    return False, [], f"Failed to create Interaction: {e!s}"

            return True, interactions, None

        except json.JSONDecodeError as e:
            return False, [], f"Invalid JSON: {e!s}"
        except (TypeError, ValueError) as e:
            return False, [], f"Deserialization failed: {e!s}"

    @staticmethod
    def export_to_file(
        interactions: list[Interaction], filepath: str
    ) -> tuple[bool, str | None]:
        """Export interactions to a JSON file."""
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)

            success, json_str, error = SerializationService.serialize_interactions(
                interactions
            )
            if not success:
                return False, error

            with Path(filepath).open("w", encoding="utf-8") as f:
                f.write(json_str)
            return True, None

        except PermissionError:
            return False, "Permission denied - cannot write to file"
        except OSError as e:
            return False, f"Export failed: {e!s}"

    @staticmethod
    def import_from_file(filepath: str) -> tuple[bool, list[Interaction], str | None]:
        """Import interactions from a JSON file."""
        try:
            with Path(filepath).open(encoding="utf-8") as f:
                json_str = f.read()
            return SerializationService.deserialize_interactions(json_str)

        except FileNotFoundError:
            return False, [], "File not found"
        except PermissionError:
            return False, [], "Permission denied - cannot read file"
        except (OSError, UnicodeDecodeError) as e:
            return False, [], f"Import failed: {e!s}"
