from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base


class Genome_annotation(Base):
    __tablename__ = "Genome_annotation"
    __table_args__ = (
        UniqueConstraint("genome_id", "set_type", name="uq_genome_set"),
        CheckConstraint("set_type IN ('hc', 'representative', 'working')", name="ck_set_type"),
    )

    id        = Column(Integer, primary_key=True, autoincrement=True)
    genome_id = Column(String, ForeignKey("Organism.genome_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    set_type  = Column(String, nullable=False)   # 'hc' | 'representative' | 'working'
    gff3_file = Column(String, nullable=True)
    gff3_link = Column(String, nullable=True)
    cdna_file = Column(String, nullable=True)
    cdna_link = Column(String, nullable=True)
    cds_file  = Column(String, nullable=True)
    cds_link  = Column(String, nullable=True)
    pep_file  = Column(String, nullable=True)
    pep_link  = Column(String, nullable=True)

    organism = relationship("Organism", back_populates="annotation")
