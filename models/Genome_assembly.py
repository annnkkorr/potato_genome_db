from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Genome_assembly(Base):
    __tablename__ = "Genome_assembly"

    genome_id      = Column(String, ForeignKey("Organism.genome_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True, index=True)
    assembly_file  = Column(String, nullable=True)
    assembly_link  = Column(String, nullable=True)
    masked_file    = Column(String, nullable=True)
    masked_link    = Column(String, nullable=True)
    softmasked_file = Column(String, nullable=True)
    softmasked_link = Column(String, nullable=True)
    release_date   = Column(String, nullable=True)

    organism = relationship("Organism", back_populates="assembly")
