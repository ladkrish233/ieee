from pydantic import BaseModel
from dataclasses import dataclass

class SectionPlan(BaseModel):
    section_title:str
    key_points:list[str]
    target_word_count:int

class PaperOutline(BaseModel):
    title:str
    section: list[SectionPlan]
    research_angle:str


class WrittenSection(BaseModel):
    section_title:str
    body:str
    figures_or_tables_needed:list[str]

class AbstractAndKeywords(BaseModel):
    abstract:str
    keywords :list[str]

class Reference(BaseModel):
    authors:str
    title: str
    venue: str
    year: int
    ieee_citation_number: int

class ReferenceList(BaseModel):
    references:list[Reference]

class PaperDraft(BaseModel):
    title:str
    abstract: str
    keywords:list[str]
    sections:list[WrittenSection]
    references:list[Reference]

@dataclass
class SectionWriterDeps:
    section_plan: SectionPlan
    research_angle: str