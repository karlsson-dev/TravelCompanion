from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, int_pk, str_uniq

class User(Base):
    id: Mapped[int_pk]
    username: Mapped[str_uniq]
    email: Mapped[str_uniq]
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)