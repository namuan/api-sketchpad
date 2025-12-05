"""Interaction repository for managing API interactions."""

from __future__ import annotations

import logging
from typing import Any

from .models.interaction import Interaction

logger = logging.getLogger(__name__)


class InteractionRepository:
    """Manages the collection of interactions."""

    def __init__(self) -> None:
        self.interactions: list[Interaction] = []
        self.current_interaction: Interaction | None = None

    def add_interaction(self, interaction: Interaction) -> None:
        """Add an interaction to the repository."""
        self.interactions.append(interaction)
        if len(self.interactions) == 1:  # If this is the first interaction
            self.current_interaction = interaction

    def remove_interaction(self, interaction: Interaction) -> bool:
        """Remove an interaction from the repository. Returns True if removed, False if not found."""
        if interaction in self.interactions:
            self.interactions.remove(interaction)
            # If we removed the current interaction, clear it or select another
            if self.current_interaction == interaction:
                self.current_interaction = (
                    self.interactions[0] if self.interactions else None
                )
            return True
        return False

    def get_interaction(self, index: int) -> Interaction | None:
        """Get an interaction by index. Returns None if index is out of bounds."""
        if 0 <= index < len(self.interactions):
            return self.interactions[index]
        return None

    def get_interaction_by_name(self, name: str) -> Interaction | None:
        """Get an interaction by name. Returns None if not found."""
        for interaction in self.interactions:
            if interaction.name == name:
                return interaction
        return None

    def set_current_interaction(self, interaction: Interaction) -> None:
        """Set the current interaction."""
        if interaction in self.interactions:
            self.current_interaction = interaction

    def get_current_interaction(self) -> Interaction | None:
        """Get the current interaction."""
        return self.current_interaction

    def get_interactions_count(self) -> int:
        """Get the number of interactions in the repository."""
        return len(self.interactions)

    def clear(self) -> None:
        """Clear all interactions from the repository."""
        self.interactions.clear()
        self.current_interaction = None

    def has_interactions(self) -> bool:
        """Check if the repository has any interactions."""
        return len(self.interactions) > 0

    def get_interaction_names(self) -> list[str]:
        """Get a list of all interaction names."""
        return [interaction.name for interaction in self.interactions]

    def update_interaction(
        self, old_interaction: Interaction, new_interaction: Interaction
    ) -> bool:
        """Update an existing interaction with new data. Returns True if updated, False if not found."""
        try:
            index = self.interactions.index(old_interaction)
            self.interactions[index] = new_interaction
            # Update current interaction if it's the one being updated
            if self.current_interaction == old_interaction:
                self.current_interaction = new_interaction
            return True
        except ValueError:
            return False

    def duplicate_interaction(self, interaction: Interaction) -> Interaction | None:
        """Create a duplicate of an interaction with a new name. Returns the new interaction."""
        if interaction not in self.interactions:
            return None

        # Create a copy with a modified name
        new_name = f"{interaction.name} (Copy)"
        counter = 1
        while self.get_interaction_by_name(new_name):
            new_name = f"{interaction.name} (Copy {counter})"
            counter += 1

        # Create a deep copy of the interaction
        new_interaction = Interaction(
            name=new_name,
            description=interaction.description,
            method=interaction.method,
            path=interaction.path,
            request_headers=interaction.request_headers.copy(),
            request_body=interaction.request_body,
            responses=interaction.responses.copy(),
        )

        self.add_interaction(new_interaction)
        return new_interaction

    def export_to_dict(self) -> dict[str, Any]:
        """Export all interactions to a dictionary format for serialization."""
        return {
            "interactions": [interaction.to_dict() for interaction in self.interactions]
        }

    def import_from_dict(self, data: dict[str, Any]) -> None:
        """Import interactions from a dictionary format."""
        if "interactions" in data:
            self.clear()
            for interaction_data in data["interactions"]:
                try:
                    interaction = Interaction.from_dict(interaction_data)
                    self.add_interaction(interaction)
                except (TypeError, ValueError, KeyError) as e:
                    logger.warning("Skipping invalid interaction during import: %s", e)
