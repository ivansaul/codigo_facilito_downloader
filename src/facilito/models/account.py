"""
Account model
"""

from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel


@dataclass
class Account(BaseModel):
    """Account model"""

    email: Optional[str] = None
    password: Optional[str] = None
    cookies: Optional[str] = None

    def login(self) -> None:
        """Login"""
        # TODO: implement
