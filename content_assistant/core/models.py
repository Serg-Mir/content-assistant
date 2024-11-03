from sqlalchemy import Column, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.schema import Index


class Base(DeclarativeBase):
    pass


class TextEntry(Base):
    __tablename__ = "texts"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, index=True)
    content = Column(Text, nullable=False)
    audience = Column(String)
    tone = Column(String)

    __table_args__ = (
        UniqueConstraint("content", "domain", "audience", "tone", name="unique_text_entry"),
        Index("idx_domain_audience_tone", "domain", "audience", "tone"),
    )
