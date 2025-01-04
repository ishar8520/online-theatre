from __future__ import annotations

import abc

from .....cache import Parameterizable


class AbstractGetQuery(abc.ABC):
    @abc.abstractmethod
    def compile(self) -> AbstractCompiledGetQuery: ...


class AbstractCompiledGetQuery(Parameterizable, abc.ABC):
    pass


class AbstractSearchQuery(abc.ABC):
    @abc.abstractmethod
    def compile(self) -> AbstractCompiledSearchQuery: ...


class AbstractCompiledSearchQuery(Parameterizable, abc.ABC):
    pass
