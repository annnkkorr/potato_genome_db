from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from database import Base


class Organism(Base):
    __tablename__ = "Organism"

    genome_id    = Column(String, primary_key=True, index=True)
    organism_name = Column(String, nullable=True)
    ploidy_type  = Column(String, nullable=True)
    description  = Column(Text, nullable=True)

    assembly   = relationship(
        "Genome_assembly",
        back_populates="organism",
        cascade="all, delete-orphan",
        uselist=False,
    )
    annotation = relationship(
        "Genome_annotation",
        back_populates="organism",
        cascade="all, delete-orphan",
        uselist=False,
    )
