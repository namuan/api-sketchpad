"""Interaction controller for coordinating UI and data operations."""

from PyQt6.QtCore import pyqtSignal

from ..models.interaction import Interaction
from ..repository import InteractionRepository


class InteractionController:
    """Coordinates interactions between UI components and data models."""

    interaction_created = pyqtSignal(Interaction)
    interaction_updated = pyqtSignal(Interaction)
    interaction_deleted = pyqtSignal(Interaction)

    def __init__(self, repository: InteractionRepository) -> None:
        self.repository = repository

    def create_interaction(self) -> Interaction:
        """Create and add a new interaction to the repository."""
        interaction = Interaction()
        self.repository.add_interaction(interaction)
        self.interaction_created.emit(interaction)
        return interaction

    def update_interaction(self, interaction: Interaction) -> None:
        """Update an existing interaction in the repository."""
        # In our current architecture, updates are handled automatically
        # through direct model binding. This method is for future expansion.
        self.interaction_updated.emit(interaction)

    def delete_interaction(self, interaction: Interaction) -> None:
        """Remove an interaction from the repository."""
        if interaction in self.repository.interactions:
            self.repository.remove_interaction(interaction)
            self.interaction_deleted.emit(interaction)

    def select_interaction(self, interaction: Interaction) -> None:
        """Set the current active interaction."""
        self.repository.set_current_interaction(interaction)

    def duplicate_interaction(self, interaction: Interaction) -> Interaction:
        """Create a copy of an existing interaction."""
        new_interaction = self.repository.duplicate_interaction(interaction)
        if new_interaction:
            self.interaction_created.emit(new_interaction)
        return new_interaction
