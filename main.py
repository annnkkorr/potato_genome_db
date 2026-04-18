from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from database import engine, get_db, Base

from models.Organism          import Organism
from models.Genome_assembly   import Genome_assembly
from models.Genome_annotation import Genome_annotation

from schemas.Organism          import OrganismCreate,         OrganismUpdate
from schemas.Genome_assembly   import GenomeAssemblyCreate,   GenomeAssemblyUpdate
from schemas.Genome_annotation import GenomeAnnotationCreate, GenomeAnnotationUpdate

app = FastAPI(title="База геномов картофеля")
templates = Jinja2Templates(directory="templates")

def fmt_date(value: str | None) -> str:
    """yyyy-mm-dd → dd/mm/yyyy для отображения."""
    if not value:
        return ""
    try:
        y, m, d = value.split("-")
        return f"{d}/{m}/{y}"
    except Exception:
        return value or ""

templates.env.filters["fmt_date"] = fmt_date

PLOIDY_RU2EN = {"диплоид": "diploid", "тетраплоид": "tetraploid", "гексаплоид": "hexaploid"}
PLOIDY_EN2RU = {v: k for k, v in PLOIDY_RU2EN.items()}

def ploidy_to_ru(value: str | None) -> str:
    return PLOIDY_EN2RU.get(value or "", value or "")

templates.env.filters["ploidy_ru"] = ploidy_to_ru
Base.metadata.create_all(bind=engine)


def redirect(url: str, message: str = "", error: str = "") -> RedirectResponse:
    params = []
    if message: params.append(f"message={message}")
    if error:   params.append(f"error={error}")
    sep = "?" if params else ""
    return RedirectResponse(f"{url}{sep}{'&'.join(params)}", status_code=303)


# ═══════════════════════════════════════════════════════════════════════════════
# ORGANISMS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/organisms", response_class=HTMLResponse)
def list_organisms(
    request: Request, db: Session = Depends(get_db),
    organism_name: Optional[str] = None,
    ploidy_type:   Optional[str] = None,
    message: str = "", error: str = "",
):
    query = db.query(Organism)
    if organism_name:
        query = query.filter(Organism.organism_name.ilike(f"%{organism_name}%"))
    if ploidy_type:
        query = query.filter(Organism.ploidy_type == ploidy_type)
    ploidy_types = [r[0] for r in db.query(Organism.ploidy_type).distinct() if r[0]]
    return templates.TemplateResponse(request=request, name="Organism.html", context={
        "organisms": query.all(), "ploidy_types": ploidy_types,
        "filters": {"organism_name": organism_name, "ploidy_type": ploidy_type},
        "edit_row": None, "message": message, "error": error,
    })


@app.get("/organisms/{genome_id}/edit", response_class=HTMLResponse)
def edit_organism_form(genome_id: str, request: Request, db: Session = Depends(get_db)):
    org = db.get(Organism, genome_id)
    if not org:
        return redirect("/organisms", error=f"'{genome_id}' не найден.")
    ploidy_types = [r[0] for r in db.query(Organism.ploidy_type).distinct() if r[0]]
    return templates.TemplateResponse(request=request, name="Organism.html", context={
        "organisms": db.query(Organism).all(), "ploidy_types": ploidy_types,
        "filters": {}, "edit_row": org, "message": "", "error": "",
    })


@app.post("/organisms/{genome_id}/edit")
def edit_organism_save(
    genome_id: str, db: Session = Depends(get_db),
    organism_name: str = Form(""), ploidy_type: str = Form(""), description: str = Form(""),
):
    org = db.get(Organism, genome_id)
    if not org:
        return redirect("/organisms", error=f"'{genome_id}' не найден.")
    try:
        data = OrganismUpdate(
            organism_name=organism_name or None,
            ploidy_type=PLOIDY_RU2EN.get(ploidy_type, ploidy_type) or None,
            description=description or None,
        )
    except Exception as exc:
        return redirect("/organisms", error=str(exc))
    for field, val in data.model_dump(exclude_none=False).items():
        setattr(org, field, val)
    db.commit()
    return redirect("/organisms", message=f"Организм '{genome_id}' обновлён.")


@app.post("/organisms")
def create_organism(
    db: Session = Depends(get_db),
    genome_id: str = Form(...), organism_name: str = Form(""),
    ploidy_type: str = Form(""), description: str = Form(""),
):
    try:
        data = OrganismCreate(
            genome_id=genome_id, organism_name=organism_name or None,
            ploidy_type=PLOIDY_RU2EN.get(ploidy_type, ploidy_type) or None,
            description=description or None,
        )
    except Exception as exc:
        return redirect("/organisms", error=str(exc))
    if db.get(Organism, data.genome_id):
        return redirect("/organisms", error=f"genome_id '{data.genome_id}' уже существует.")
    db.add(Organism(**data.model_dump()))
    db.commit()
    return redirect("/organisms", message=f"Организм '{data.genome_id}' добавлен.")


@app.post("/organisms/{genome_id}/delete")
def delete_organism(genome_id: str, db: Session = Depends(get_db)):
    org = db.get(Organism, genome_id)
    if not org:
        return redirect("/organisms", error=f"'{genome_id}' не найден.")
    db.delete(org)
    db.commit()
    return redirect("/organisms", message=f"Организм '{genome_id}' удалён.")


# ═══════════════════════════════════════════════════════════════════════════════
# ASSEMBLIES
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/assemblies", response_class=HTMLResponse)
def list_assemblies(
    request: Request, db: Session = Depends(get_db),
    genome_id:  Optional[str] = None,
    sort_date:  Optional[str] = None,   # "asc" | "desc"
    message: str = "", error: str = "",
):
    query = db.query(Genome_assembly)
    if genome_id:
        query = query.filter(Genome_assembly.genome_id.ilike(f"%{genome_id}%"))
    if sort_date == "asc":
        query = query.order_by(Genome_assembly.release_date.asc())
    elif sort_date == "desc":
        query = query.order_by(Genome_assembly.release_date.desc())
    return templates.TemplateResponse(request=request, name="Genome_assembly.html", context={
        "assemblies": query.all(),
        "filters": {"genome_id": genome_id, "sort_date": sort_date},
        "edit_row": None, "message": message, "error": error,
    })


@app.get("/assemblies/{genome_id}/edit", response_class=HTMLResponse)
def edit_assembly_form(genome_id: str, request: Request, db: Session = Depends(get_db)):
    row = db.get(Genome_assembly, genome_id)
    if not row:
        return redirect("/assemblies", error=f"'{genome_id}' не найден.")
    return templates.TemplateResponse(request=request, name="Genome_assembly.html", context={
        "assemblies": db.query(Genome_assembly).all(),
        "filters": {}, "edit_row": row, "message": "", "error": "",
    })


@app.post("/assemblies/{genome_id}/edit")
def edit_assembly_save(
    genome_id: str, db: Session = Depends(get_db),
    assembly_file: str = Form(""), assembly_link: str = Form(""),
    masked_file: str = Form(""), masked_link: str = Form(""),
    softmasked_file: str = Form(""), softmasked_link: str = Form(""),
    release_date: str = Form(""),
):
    row = db.get(Genome_assembly, genome_id)
    if not row:
        return redirect("/assemblies", error=f"'{genome_id}' не найден.")
    try:
        data = GenomeAssemblyUpdate(
            assembly_file=assembly_file or None, assembly_link=assembly_link or None,
            masked_file=masked_file or None, masked_link=masked_link or None,
            softmasked_file=softmasked_file or None, softmasked_link=softmasked_link or None,
            release_date=release_date or None,
        )
    except Exception as exc:
        return redirect("/assemblies", error=str(exc))
    for field, val in data.model_dump(exclude_none=False).items():
        setattr(row, field, val)
    db.commit()
    return redirect("/assemblies", message=f"Сборка '{genome_id}' обновлена.")


@app.post("/assemblies")
def create_assembly(
    db: Session = Depends(get_db),
    genome_id: str = Form(...),
    assembly_file: str = Form(""), assembly_link: str = Form(""),
    masked_file: str = Form(""), masked_link: str = Form(""),
    softmasked_file: str = Form(""), softmasked_link: str = Form(""),
    release_date: str = Form(""),
):
    try:
        data = GenomeAssemblyCreate(
            genome_id=genome_id,
            assembly_file=assembly_file or None, assembly_link=assembly_link or None,
            masked_file=masked_file or None, masked_link=masked_link or None,
            softmasked_file=softmasked_file or None, softmasked_link=softmasked_link or None,
            release_date=release_date or None,
        )
    except Exception as exc:
        return redirect("/assemblies", error=str(exc))
    if not db.get(Organism, data.genome_id):
        return redirect("/assemblies", error=f"Организм '{data.genome_id}' не найден. Сначала добавьте его.")
    if db.get(Genome_assembly, data.genome_id):
        return redirect("/assemblies", error=f"Сборка для '{data.genome_id}' уже существует.")
    db.add(Genome_assembly(**data.model_dump()))
    db.commit()
    return redirect("/assemblies", message=f"Сборка для '{data.genome_id}' добавлена.")


@app.post("/assemblies/{genome_id}/delete")
def delete_assembly(genome_id: str, db: Session = Depends(get_db)):
    row = db.get(Genome_assembly, genome_id)
    if not row:
        return redirect("/assemblies", error=f"Сборка '{genome_id}' не найдена.")
    db.delete(row)
    db.commit()
    return redirect("/assemblies", message=f"Сборка '{genome_id}' удалена.")


# ═══════════════════════════════════════════════════════════════════════════════
# ANNOTATIONS  (составной PK: genome_id + set_type)
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/annotations", response_class=HTMLResponse)
def list_annotations(
    request: Request, db: Session = Depends(get_db),
    genome_id: Optional[str] = None,
    set_type:  Optional[str] = None,
    message: str = "", error: str = "",
):
    query = db.query(Genome_annotation)
    if genome_id:
        query = query.filter(Genome_annotation.genome_id.ilike(f"%{genome_id}%"))
    if set_type:
        query = query.filter(Genome_annotation.set_type == set_type)
    return templates.TemplateResponse(request=request, name="Genome_annotation.html", context={
        "annotations": query.all(),
        "filters": {"genome_id": genome_id, "set_type": set_type},
        "edit_row": None, "message": message, "error": error,
    })


@app.get("/annotations/{genome_id}/{set_type}/edit", response_class=HTMLResponse)
def edit_annotation_form(genome_id: str, set_type: str, request: Request, db: Session = Depends(get_db)):
    row = db.query(Genome_annotation).filter_by(genome_id=genome_id, set_type=set_type).first()
    if not row:
        return redirect("/annotations", error=f"'{genome_id} / {set_type}' не найден.")
    return templates.TemplateResponse(request=request, name="Genome_annotation.html", context={
        "annotations": db.query(Genome_annotation).all(),
        "filters": {}, "edit_row": row, "message": "", "error": "",
    })


@app.post("/annotations/{genome_id}/{set_type}/edit")
def edit_annotation_save(
    genome_id: str, set_type: str, db: Session = Depends(get_db),
    gff3_file: str = Form(""), gff3_link: str = Form(""),
    cdna_file: str = Form(""), cdna_link: str = Form(""),
    cds_file:  str = Form(""), cds_link:  str = Form(""),
    pep_file:  str = Form(""), pep_link:  str = Form(""),
):
    row = db.query(Genome_annotation).filter_by(genome_id=genome_id, set_type=set_type).first()
    if not row:
        return redirect("/annotations", error=f"'{genome_id} / {set_type}' не найден.")
    try:
        data = GenomeAnnotationUpdate(
            gff3_file=gff3_file or None, gff3_link=gff3_link or None,
            cdna_file=cdna_file or None, cdna_link=cdna_link or None,
            cds_file=cds_file   or None, cds_link=cds_link   or None,
            pep_file=pep_file   or None, pep_link=pep_link   or None,
        )
    except Exception as exc:
        return redirect("/annotations", error=str(exc))
    for field, val in data.model_dump(exclude_none=False).items():
        setattr(row, field, val)
    db.commit()
    return redirect("/annotations", message=f"Аннотация '{genome_id} / {set_type}' обновлена.")


@app.post("/annotations")
def create_annotation(
    db: Session = Depends(get_db),
    genome_id: str = Form(...), set_type: str = Form(...),
    gff3_file: str = Form(""), gff3_link: str = Form(""),
    cdna_file: str = Form(""), cdna_link: str = Form(""),
    cds_file:  str = Form(""), cds_link:  str = Form(""),
    pep_file:  str = Form(""), pep_link:  str = Form(""),
):
    try:
        data = GenomeAnnotationCreate(
            genome_id=genome_id, set_type=set_type,
            gff3_file=gff3_file or None, gff3_link=gff3_link or None,
            cdna_file=cdna_file or None, cdna_link=cdna_link or None,
            cds_file=cds_file   or None, cds_link=cds_link   or None,
            pep_file=pep_file   or None, pep_link=pep_link   or None,
        )
    except Exception as exc:
        return redirect("/annotations", error=str(exc))
    if not db.get(Organism, data.genome_id):
        return redirect("/annotations", error=f"Организм '{data.genome_id}' не найден.")
    if db.query(Genome_annotation).filter_by(genome_id=data.genome_id, set_type=data.set_type).first():
        return redirect("/annotations", error=f"Аннотация '{data.genome_id} / {data.set_type}' уже существует.")
    db.add(Genome_annotation(**data.model_dump()))
    db.commit()
    return redirect("/annotations", message=f"Аннотация '{data.genome_id} / {data.set_type}' добавлена.")


@app.post("/annotations/{genome_id}/{set_type}/delete")
def delete_annotation(genome_id: str, set_type: str, db: Session = Depends(get_db)):
    row = db.query(Genome_annotation).filter_by(genome_id=genome_id, set_type=set_type).first()
    if not row:
        return redirect("/annotations", error=f"Аннотация '{genome_id} / {set_type}' не найдена.")
    db.delete(row)
    db.commit()
    return redirect("/annotations", message=f"Аннотация '{genome_id} / {set_type}' удалена.")


# ═══════════════════════════════════════════════════════════════════════════════
# JOINED VIEW
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/joined", response_class=HTMLResponse)
def joined_view(
    request: Request, db: Session = Depends(get_db),
    organism_name: Optional[str] = None,
    ploidy_type:   Optional[str] = None,
    sort_date:     Optional[str] = None,   # "asc" | "desc"
    message: str = "", error: str = "",
):
    query = (
        db.query(
            Organism.genome_id, Organism.organism_name, Organism.ploidy_type, Organism.description,
            Genome_assembly.release_date, Genome_assembly.assembly_file, Genome_assembly.assembly_link,
            Genome_annotation.set_type,
            Genome_annotation.gff3_file, Genome_annotation.gff3_link,
            Genome_annotation.cdna_file, Genome_annotation.cdna_link,
            Genome_annotation.cds_file,  Genome_annotation.cds_link,
            Genome_annotation.pep_file,  Genome_annotation.pep_link,
        )
        .outerjoin(Genome_assembly,   Organism.genome_id == Genome_assembly.genome_id)
        .outerjoin(Genome_annotation, Organism.genome_id == Genome_annotation.genome_id)
    )
    if organism_name:
        query = query.filter(Organism.organism_name.ilike(f"%{organism_name}%"))
    if ploidy_type:
        query = query.filter(Organism.ploidy_type == ploidy_type)
    if sort_date == "asc":
        query = query.order_by(Genome_assembly.release_date.asc())
    elif sort_date == "desc":
        query = query.order_by(Genome_assembly.release_date.desc())

    ploidy_types = [r[0] for r in db.query(Organism.ploidy_type).distinct() if r[0]]
    return templates.TemplateResponse(request=request, name="joined.html", context={
        "rows": query.all(), "ploidy_types": ploidy_types,
        "filters": {
            "organism_name": organism_name,
            "ploidy_type":   ploidy_type,
            "sort_date":     sort_date,
        },
        "message": message, "error": error,
    })


@app.get("/")
def root():
    return RedirectResponse("/organisms")
