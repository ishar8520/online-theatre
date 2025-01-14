import datetime
from uuid import uuid4
from sqlalchemy import (
    Column,
    TIMESTAMP
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class CreatedModel(Base):
    __abstract__ = True
    
    id = Column(
        UUID(as_uuid=True),
        unique=True,
        primary_key=True,
        default=uuid4()
    )
    created_at = Column(
        TIMESTAMP,
        nullable=False,
        default=datetime.datetime.now()
    )
    
    def __init__(self, **kwargs):
        self.id = uuid4()
        self.created_at = datetime.datetime.now()
        super().__init__(**kwargs)


class ModifiedModel(Base):
    __abstract__ = True
    
    modified_at = Column(
        TIMESTAMP,
        nullable=False,
        default=datetime.datetime.now()
    )
    
    def __init__(self, **kwargs):
        self.modified_at = datetime.datetime.now()
        super().__init__(**kwargs)
