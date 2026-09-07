from models import PaperOutline,WrittenSection,SectionWriterDeps,AbstractAndKeywords,ReferenceList
from pydantic_ai import Agent,RunContext
from dotenv import load_dotenv

load_dotenv()

model="anthropic:claude-haiku-4-5"

agent1=Agent(
    model,
    system_prompt="act as a research paper planner, produce an IEEE-appropriate section structure (Abstract is handled separately, so start from Introduction), stay within the user's total word budget, and fill in research_angle as a one-sentence thesis statement",
    output_type=PaperOutline
)

agent2=Agent(
    model,
    output_type=WrittenSection,
    deps_type=SectionWriterDeps
)

@agent2.system_prompt
def section_writer_prompt(ctx: RunContext[SectionWriterDeps]) -> str:
    plan = ctx.deps.section_plan
    return (
        "Write in formal academic/IEEE tone. Address every point in the "
        f"following key points: {plan.key_points}. "
        f"Target approximately {plan.target_word_count} words for this "
        f"section titled '{plan.section_title}'. "
        f"The paper's overall research angle/thesis is: {ctx.deps.research_angle}. "
        "Do not invent inline citations — citations are handled in a "
        "separate pass. Write naturally; if a claim clearly needs a source, "
        "just let that be implicit for now."
    )

agent3=Agent(
    model,
    system_prompt="read the finished section content, produce a 150–250 word abstract following IEEE conventions (problem → approach → result → significance, in that order), and 4–6 keywords",
    output_type=AbstractAndKeywords
)

agent4=Agent(
    model,
    system_prompt="generate references that are representative and plausible for this topic, but the system prompt should make the agent aware these are drafts, not verified — this matters because we're not doing real search yet",
    output_type=ReferenceList
)
