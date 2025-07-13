# LinkedIn Reactions Extractor - CrewAI Version

🤖 **Multi-Agent LinkedIn extraction using CrewAI framework with Browserbase/Stagehand integration**

This is a refactored version of the LinkedIn Reactions Extractor that uses the CrewAI framework to orchestrate multiple AI agents working together to extract reaction data from your LinkedIn posts.

## 🔄 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    CrewAI Framework                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │                  🧠 Crew Manager                 │    │
│  │         (Orchestrates agents & tasks)            │    │
│  └─────────────────┬───────────────────────────────┘    │
│                    │                                      │
│  ┌─────────────────┼─────────────────┬──────────────┐   │
│  ▼                 ▼                 ▼              ▼   │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ Navigator   │ │ Extractor   │ │ Reporter    │        │
│ │   Agent     │ │   Agent     │ │   Agent     │        │
│ │             │ │             │ │             │        │
│ │ Finds post  │ │ Extracts   │ │ Generates   │        │
│ │ & reactions │ │ profiles    │ │ reports     │        │
│ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘        │
│        │               │               │                 │
└────────┼───────────────┼───────────────┼─────────────────┘
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │ Stagehand Tool   │
              │  (Browserbase)   │
              │                  │
              │ - Act()          │
              │ - Extract()      │
              │ - Observe()      │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │    LinkedIn      │
              │  (Cloud Browser) │
              └──────────────────┘
```

## 🤖 Agent Roles

### 1. **Navigator Agent** 🧭
- **Role**: LinkedIn Navigator
- **Goal**: Navigate to the most recent post and open reactions modal
- **Tools**: StagehandTool (Act, Observe)
- **Expertise**: Understanding LinkedIn's DOM structure and handling dynamic content

### 2. **Extractor Agent** 📊
- **Role**: Profile Data Extractor  
- **Goal**: Extract structured profile data from reaction lists
- **Tools**: StagehandTool (Extract)
- **Expertise**: Parsing LinkedIn profiles and handling edge cases

### 3. **Reporter Agent** 📝
- **Role**: Data Report Generator
- **Goal**: Create formatted JSON and Markdown reports
- **Tools**: Built-in Python capabilities
- **Expertise**: Data visualization and report generation

## 🚀 Key Advantages of CrewAI Version

1. **Multi-Agent Collaboration**: Specialized agents work together, each focusing on their expertise
2. **Built-in Memory**: Agents can share context and learn from previous interactions
3. **Planning Mode**: The crew can plan the approach before execution
4. **Natural Language Instructions**: Uses Stagehand's AI-powered browser control
5. **Error Recovery**: Each agent has retry capabilities with max iterations
6. **Modular Design**: Easy to add new agents or modify existing ones

## 📦 Installation

1. **Install CrewAI dependencies**
   ```bash
   pip install -r requirements-crewai.txt
   ```

2. **Set up environment variables** (same as original version)
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## 🎯 Usage

Run the CrewAI version:

```bash
python crewai_linkedin_extractor.py
```

## 📋 Task Flow

1. **Navigation Task**
   - Navigate to LinkedIn notifications
   - Find and click the most recent post
   - Open the reactions modal
   - Take verification screenshot

2. **Extraction Task**
   - Extract all reactor profiles
   - Parse names, titles, companies, connections
   - Structure data in JSON format
   - Handle missing fields gracefully

3. **Reporting Task**
   - Generate timestamped JSON file
   - Create Markdown summary
   - Calculate statistics
   - Format for readability

## 🔧 Customization

### Adding New Agents

```python
analyst = Agent(
    role='Data Analyst',
    goal='Analyze reaction patterns and provide insights',
    backstory='Expert in LinkedIn engagement analytics',
    tools=[custom_analysis_tool],
    verbose=True
)
```

### Modifying Tasks

```python
analysis_task = Task(
    description="Analyze reaction patterns and identify key influencers",
    expected_output="Insights report with engagement metrics",
    agent=analyst,
    context=[extract_task]
)
```

## 🛠️ Stagehand Integration

The CrewAI version uses Stagehand's three core primitives:

1. **Act**: Natural language browser interactions
   ```python
   "Click on the reactions count that says 'and X others'"
   ```

2. **Extract**: Structured data extraction with schemas
   ```python
   {
     "reactors": [{
       "name": "string",
       "title": "string",
       "company": "string"
     }]
   }
   ```

3. **Observe**: Analyze page state and available actions
   ```python
   "Find all clickable reaction elements"
   ```

## 📊 Output

Same as the original version:
- `reactions_data_[timestamp].json` - Structured reactor data
- `reactions_summary_[timestamp].md` - Human-readable report
- Screenshot verification files

## 🔍 Debugging

Enable verbose mode to see:
- Agent reasoning processes
- Task execution steps
- Tool invocations
- Inter-agent communication

## 🚨 Error Handling

- Each agent has retry logic with `max_iter`
- Graceful degradation for missing data
- Context sharing between agents for recovery
- Detailed error messages in verbose mode

## 🎭 Future Enhancements

1. **Additional Agents**:
   - Engagement Analyzer Agent
   - Connection Recommender Agent
   - Content Performance Agent

2. **Advanced Features**:
   - Historical tracking
   - Sentiment analysis
   - Engagement predictions
   - Automated follow-up suggestions

3. **Integration Options**:
   - Webhook notifications
   - CRM integration
   - Analytics dashboards
   - Scheduled runs

## 📝 Notes

- CrewAI adds overhead but provides better modularity and extensibility
- Agents can be reused for other LinkedIn automation tasks
- Memory feature allows learning from previous extractions
- Planning mode helps optimize the extraction strategy

This CrewAI version demonstrates how to build sophisticated automation using collaborative AI agents, making the system more maintainable and extensible compared to monolithic scripts.