from abc import ABC, abstractmethod

from dspy import Module
from pydantic import field_validator


class BaseModule(Module):

    agent_name: str

    @field_validator('agent_name')
    def validate_agent_name(cls, value):
        if not value.strip():
            raise ValueError("agent_name is required and must be a non-empty string.")
        return value

    @abstractmethod
    def forward(self, *args, **kwargs):
        """Method that must be implemented by subclasses."""
        pass
