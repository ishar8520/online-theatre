from __future__ import annotations

from typing import Annotated

from fastapi import Request
from taskiq import TaskiqDepends

RequestTaskiqDep = Annotated[Request, TaskiqDepends()]
