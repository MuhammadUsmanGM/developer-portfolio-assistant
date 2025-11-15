# Developer Portfolio Assistant Agent

**Subtitle:** Automatically generate and update your developer portfolio with AI-powered agentic workflows.

![thumbnail](thumbnail.png)

## 🚀 Overview

The Developer Portfolio Assistant Agent streamlines creation and upkeep of your developer portfolio by:

- Analyzing your GitHub profile and recent projects
- Summarizing your work with Google Gemini LLM
- Generating ready-to-post content (LinkedIn, blog, README, etc.)
- Logging all activity and saving updates with long-term memory for repeatable, auditable results

This agent demonstrates a **comprehensive multi-agent system** with:

- **4 Specialized Agents**: GitHub Analysis, Content Generation, Portfolio Writer, and Coordinator
- **Agent-to-Agent (A2A) Protocol**: Enables distributed communication between agents
- **Long-Running Operations**: Pause/resume capabilities with checkpoint persistence
- **Context Engineering**: Intelligent context window management with compaction strategies
- **Session Management**: State tracking and conversation history
- **Agent Evaluation**: Performance metrics and content quality assessment
- **Observability**: Comprehensive logging and monitoring

This solves a real developer productivity bottleneck while demonstrating advanced agentic AI capabilities.

---

## 🧩 Problem Statement

Manually writing, updating, and sharing developer portfolios and project summaries is time-consuming—even for experienced programmers. Automating content generation and history management saves hours each month and lets developers focus on building.

---

## 💡 Solution

Using the ADK platform, we built a **sophisticated multi-agent system** that:

- **Automates portfolio updates** through a coordinated workflow of specialized agents
- **Supports multi-repo analysis** with intelligent GitHub data extraction
- **Leverages Gemini AI** for rich, customizable content generation with model fallback
- **Maintains persistent memory** (JSON-backed) for long-term context and history
- **Implements session management** for state tracking across interactions
- **Provides agent evaluation** with success rates, quality metrics, and performance tracking
- **Enables agent-to-agent communication** via A2A protocol for distributed task execution
- **Supports long-running operations** with pause/resume capabilities and checkpoint persistence
- **Manages context windows** with intelligent compaction strategies
- **Offers robust observability** through comprehensive logging and monitoring

This architecture demonstrates production-ready agentic AI with separation of concerns, error isolation, and scalable design patterns.

---

## ✨ Agent Features & Capabilities

### **Multi-Agent System**

The system consists of **4 specialized agents** working together:

1. **GitHub Analysis Agent** (`github_analyst`)

   - Specialized in fetching and analyzing GitHub profiles and repositories
   - Tools: `github_analyzer`, `github_repo_activity`

2. **Content Generation Agent** (`content_generator_agent`)

   - Specialized in AI-powered content generation using Gemini
   - Tools: `content_generator`
   - Features: Model fallback, context management, quality evaluation

3. **Portfolio Writer Agent** (`portfolio_writer_agent`)

   - Specialized in file operations and portfolio management
   - Tools: `portfolio_writer`

4. **Coordinator Agent** (`dpa_root`)
   - Orchestrates the complete workflow
   - Coordinates between specialized agents
   - Has access to all tools for flexible task execution

### **Core Tools (15 Total)**

- `github_analyzer`: Fetches GitHub profile data
- `github_repo_activity`: Analyzes repository commits and activity
- `content_generator`: Generates content using Gemini with context management
- `portfolio_writer`: Saves content to markdown files
- `portfolio_update`: Complete automated workflow with long-running operation support
- `get_history`: Queries persistent memory
- **A2A Protocol Tools**: `send_a2a_request`, `send_a2a_event`, `get_a2a_message_history`, `process_a2a_messages`
- **Long-Running Operation Tools**: `create_long_running_operation`, `pause_operation`, `resume_operation`, `get_operation_status`, `list_operations`

### **Advanced Features**

- **Agent-to-Agent (A2A) Protocol**: Agents can communicate via request-response and event patterns
- **Long-Running Operations**: Operations can be paused at checkpoints and resumed later
- **Context Engineering**: Intelligent context window management with 3 compaction strategies (importance-based, summarization, truncation)
- **Session Management**: In-memory session service for state tracking and conversation history
- **Agent Evaluation**: Tracks success rates, content quality scores, and performance metrics
- **Persistent Memory**: JSON-backed storage for long-term context and history
- **Observability**: Comprehensive logging with Unicode-safe handling
- **Gemini Integration**: Model fallback mechanism supporting both free and pro API tiers

---

## 🛠️ Architecture

### **Multi-Agent Architecture**

```text
┌─────────────────────────────────────────────────────────────┐
│                    Coordinator Agent                        │
│                   (dpa_root - Orchestrator)                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ GitHub        │ │ Content       │ │ Portfolio     │
│ Analysis      │ │ Generation    │ │ Writer        │
│ Agent         │ │ Agent         │ │ Agent         │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
        └─────────┬───────┴─────────┬───────┘
                  │                 │
        ┌─────────▼─────────┐ ┌─────▼──────────────┐
        │   A2A Protocol    │ │  Long-Running Ops  │
        │  (Communication)  │ │  (Pause/Resume)    │
        └───────────────────┘ └────────────────────┘
                  │
        ┌─────────▼──────────────────────────────┐
        │  Shared Services                       │
        │  - Persistent Memory (JSON)            │
        │  - Session Management                  │
        │  - Context Manager                     │
        │  - Agent Evaluator                     │
        │  - Logging System                      │
        └────────────────────────────────────────┘
```

### **System Components**

**Agents:**

- **Coordinator Agent**: Orchestrates workflow, delegates to specialized agents
- **GitHub Analysis Agent**: Fetches and analyzes GitHub data
- **Content Generation Agent**: Generates AI content using Gemini
- **Portfolio Writer Agent**: Handles file operations

**Communication:**

- **A2A Protocol**: Enables agent-to-agent communication via messages
- **Request-Response Pattern**: Synchronous communication between agents
- **Event Notifications**: Asynchronous event broadcasting

**State Management:**

- **Persistent Memory**: Long-term storage of portfolio updates
- **Session Management**: In-memory session state tracking
- **Context Management**: LLM context window with compaction

**Operations:**

- **Long-Running Operations**: Pause/resume with checkpoint persistence
- **Agent Evaluation**: Performance and quality metrics tracking
- **Observability**: Comprehensive logging and monitoring

---

## 💻 Installation & Usage

### Prerequisites

- Python 3.11+ (required by ADK)
- `git clone` this repository
- Install dependencies: `pip install -r requirements.txt` or `uv pip install -r requirements.txt`
- Set your Google Gemini API Key as an environment variable:
  - **Linux/Mac**: `export GOOGLE_API_KEY="your-api-key"`
  - **Windows (CMD)**: `set GOOGLE_API_KEY=your-api-key`
  - **Windows (PowerShell)**: `$env:GOOGLE_API_KEY="your-api-key"`

### Running the Agent

**Start the agent via ADK CLI:**

```bash
adk run dpa_agent
```

The agent will start and you can interact with it in the terminal. Type `exit` to quit.

**Available tools:**

- `github_analyzer username="YourGitHub"`
- `github_repo_activity username="YourGitHub" top_n=3`
- `content_generator github_summary=... repo_activity=... format_style="Blog" tone="energetic" include_hashtags=true`
- `portfolio_update username="YourGitHub"`
- `get_history username="YourGitHub"`

**Outputs:**

- Generated posts in `portfolio_entry.md`
- Logs in `portfolio_agent.log`
- All history saved in `memory_bank.json`

### (Optional) Test via Kaggle or Colab Notebook

You can run this full workflow as a script and document results for the capstone if you don't have cloud deploy!

---

## 📝 Memory, Sessions, and Observability

### **Persistent Memory**

- **Long-term storage**: All portfolio updates saved to `memory_bank.json`
- **Timestamp tracking**: Every entry includes creation timestamp
- **Queryable history**: Filter by username or retrieve all history
- **Metadata support**: Rich metadata storage for each entry

### **Session Management**

- **In-memory sessions**: Track user interactions and workflow state
- **Session state**: Store intermediate results and preferences
- **Conversation history**: Maintain chronological interaction records
- **Automatic expiration**: Sessions expire after 24 hours (configurable)

### **Observability & Logging**

- **Comprehensive logging**: All actions logged to `portfolio_agent.log`
- **Unicode-safe**: Handles emojis and international characters
- **Event tracking**: Every tool call, agent action, and error is logged
- **Traceability**: Full audit trail of all operations

### **Agent Evaluation**

- **Success rate tracking**: Monitor tool and operation success rates
- **Content quality metrics**: Evaluate generated content quality (0-100 score)
- **Performance metrics**: Track execution times for optimization
- **Tool-specific metrics**: Individual success rates per tool

---

## ☁️ Deployment

> **Cloud deployment is ready, but due to credit card/billing requirements, demo deployments are currently omitted. All cloud-ready code and a Dockerfile are included for full reproducibility.**

You can deploy in your own GCP project as follows:

gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/dev-portfolio-agent
gcloud run deploy dev-portfolio-agent
--image gcr.io/YOUR_PROJECT_ID/dev-portfolio-agent
--platform managed
--region us-central1
--allow-unauthenticated

---

## 🏆 Capstone Requirements - All Features Implemented

### **Required Features (Minimum 3) - ✅ 7 Implemented**

1. ✅ **Multi-Agent System** - 4 specialized agents with coordinator pattern
2. ✅ **Custom Tools** - 15 custom tools for various operations
3. ✅ **Long-Term Memory** - PersistentMemoryBank with JSON storage
4. ✅ **Sessions & State Management** - InMemorySessionService implementation
5. ✅ **Observability: Logging** - Centralized logging with Unicode handling
6. ✅ **Agent Evaluation** - AgentEvaluator with comprehensive metrics
7. ✅ **Agent Powered by LLM** - All agents use Gemini models

### **Optional Features (Bonus) - ✅ 3 Implemented**

1. ✅ **Long-Running Operations** - Pause/resume with checkpoint persistence
2. ✅ **A2A Protocol** - Full agent-to-agent communication implementation
3. ✅ **Context Engineering/Compaction** - 3 compaction strategies for context management

### **Feature Coverage: 10/10 (100%)**

- **Exceeds minimum requirement by 233%** (10 vs 3 required)
- **All optional features implemented** for maximum bonus points

### **Code Quality**

- ✅ **Comprehensive code comments** throughout all files
- ✅ **Design decision documentation** in code
- ✅ **Architecture documentation** in README
- ✅ **Setup and usage instructions** provided

---

## 📷 Sample Output

```text
🚀 Developer Update: Muhammad Usman
Recent repos:

awesome-ai-toolbox: Improved code gen, added whisper integration

Latest commit: 'Added GPU inference support' (2025-10-12)

Latest commit: 'Documentation improvements' (2025-10-11)
...
#Python #OpenSource #AI
```

---

## 🤖 Future Work

- Add full web/REST API for SaaS-like usage
- Automated deployment pipeline
- Multi-platform integration (update LinkedIn, Hashnode, etc.)

---

## ℹ️ Credits

Built using [Google ADK](https://github.com/google/adk-python), [Google GenerativeAI](https://github.com/google/generative-ai-python), and open-source Python packages.

---

## ❓ Contact

Questions or collaboration? Reach out via [GitHub](https://github.com/MuhammadUsmanGM) or [LinkedIn](https://www.linkedin.com/in/muhammad-usman-099704390).
