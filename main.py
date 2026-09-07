import sys
from dotenv import load_dotenv
from agents import agent1,agent2,agent3,agent4
from models import PaperDraft,PaperOutline,SectionWriterDeps,ReferenceList,WrittenSection,AbstractAndKeywords
import asyncio
from formatter import build_ieee_docx

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

async def generate_outline(topic: str, total_word_target: int) -> PaperOutline:
    prompt = (
        f"Topic: {topic}\n"
        f"Target total paper length: approximately {total_word_target} words."
    )
    result=await agent1.run(prompt)
    outline:PaperOutline = result.output
    print(f"✓ Outline created: '{outline.title}' with {len(outline.section)} sections")
    return outline

async def write_all_sections(outline: PaperOutline) -> list[WrittenSection]:
    written_sections: list[WrittenSection] = []

    for section_plan in outline.section:
        deps = SectionWriterDeps(
            section_plan=section_plan,
            research_angle=outline.research_angle
        )
        result = await agent2.run(
            f"Write the '{section_plan.section_title}' section.",
            deps=deps
        )
        written_section: WrittenSection = result.output
        written_sections.append(written_section)
        print(f"✓ Wrote section: {written_section.section_title} "
              f"(~{len(written_section.body.split())} words)")
    # <-- loop ends here (nothing indented further after this point)

    return written_sections

async def generate_abstract(written_sections: list[WrittenSection]) -> AbstractAndKeywords:
    # Condense section bodies into one block of text for the agent to read
    combined_content = "\n\n".join(
        f"[{s.section_title}]\n{s.body}" for s in written_sections
    )
    prompt = f"Here is the full paper content:\n\n{combined_content}"
    result = await agent3.run(prompt)
    abstract_data: AbstractAndKeywords = result.output
    print(f"✓ Abstract generated ({len(abstract_data.abstract.split())} words), "
          f"{len(abstract_data.keywords)} keywords")
    return abstract_data

async def generate_references(topic: str, written_sections: list[WrittenSection]) -> ReferenceList:
    # Lean digest instead of full bodies — keeps the prompt smaller
    section_titles = ", ".join(s.section_title for s in written_sections)
    prompt = (
        f"Topic: {topic}\n"
        f"The paper covers these sections: {section_titles}. "
        "Generate an IEEE-style reference list relevant to this topic."
    )
    result = await agent4.run(prompt)
    reference_data: ReferenceList = result.output
    print(f"✓ Generated {len(reference_data.references)} references")
    return reference_data


def assemble_paper_draft(
    outline: PaperOutline,
    written_sections: list[WrittenSection],
    abstract_data: AbstractAndKeywords,
    reference_data: ReferenceList,
) -> PaperDraft:
    return PaperDraft(
        title=outline.title,
        abstract=abstract_data.abstract,
        keywords=abstract_data.keywords,
        sections=written_sections,
        references=reference_data.references,
    )

async def generate_paper(topic: str, total_word_target: int = 3000) -> PaperDraft:
    outline = await generate_outline(topic, total_word_target)
    written_sections = await write_all_sections(outline)
    abstract_data = await generate_abstract(written_sections)
    reference_data = await generate_references(topic, written_sections)

    draft = assemble_paper_draft(outline, written_sections, abstract_data, reference_data)
    print(f"\n✓ Paper draft complete: '{draft.title}' "
          f"({len(draft.sections)} sections, {len(draft.references)} references)")
    return draft

if __name__ == "__main__":
    topic = input("Enter your research paper topic: ")
    paper_draft = asyncio.run(generate_paper(topic))
    build_ieee_docx(paper_draft,"output_paper.docx")