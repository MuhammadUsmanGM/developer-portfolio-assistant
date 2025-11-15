from google.adk.agents import Agent
from .tools.github_analyzer import github_analyzer
from .tools.content_generator import content_generator
from .tools.portfolio_writer import portfolio_writer
from .tools.portfolio_update import portfolio_update
from .tools.memory_query import get_history
from .tools.github_analyzer import github_repo_activity

from .memory import PersistentMemoryBank
memory_bank = PersistentMemoryBank()  # This auto-loads all history at startup



# Root agent definition for ADK
root_agent = Agent(
    model="gemini-2.5-flash",
    name="dpa_root",
    description="Developer Portfolio Assistant Root Agent",
    instruction=(
        "You coordinate analysis of GitHub activity, generate professional content (summaries, posts, README), "
        "and help automate portfolio maintenance for developers."
    ),
    tools=[
        github_analyzer,
        content_generator,
        portfolio_writer,
        portfolio_update,
        get_history,
        github_repo_activity,
    ]
)
