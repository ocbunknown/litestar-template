import abc

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.base import Base
from src.database.repositories.crud import CRUDRepository


class BaseRepository[M: Base](abc.ABC):
    __slots__ = ("_session", "_crud")

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._crud = CRUDRepository(session, self.model)

    @property
    @abc.abstractmethod
    def model(self) -> type[M]:
        raise NotImplementedError
