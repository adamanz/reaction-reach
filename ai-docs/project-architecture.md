# ReactionReach Project Architecture

## System Overview

ReactionReach is a multi-agent system built with CrewAI that uses Stagehand + Browserbase for stealth LinkedIn automation. The system extracts reaction data from LinkedIn posts and generates intelligence reports.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    ReactionReach System                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend: CLI Interface                                    │
├─────────────────────────────────────────────────────────────┤
│  Orchestration Layer: CrewAI Multi-Agent System            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  Navigator  │→│ Post Hunter │→│ Harvester   │          │
│  │   Agent     │ │   Agent     │ │   Agent     │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│         │                ↓               ↓                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  Reporter   │←│   Analyst   │←│   Storage   │          │
│  │   Agent     │ │   Agent     │ │   Layer     │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  Automation Layer: Stagehand + Browserbase                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   Stealth   │ │   Browser   │ │  Anti-Bot   │          │
│  │   Manager   │ │   Sessions  │ │ Protection  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure: LinkedIn Platform                         │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Agent Layer (CrewAI)

#### Navigator Agent
- **Purpose**: Handle authentication and stealth navigation
- **Tools**: StagehandTool with Browserbase
- **Responsibilities**:
  - LinkedIn authentication flow
  - Session management
  - Anti-detection measures
  - Safe navigation patterns

#### Post Hunter Agent
- **Purpose**: Discover and catalog user posts
- **Tools**: StagehandTool with scroll automation
- **Responsibilities**:
  - Navigate to user profile activity
  - Handle infinite scroll pagination
  - Extract post metadata
  - Filter posts by engagement

#### Reaction Harvester Agent
- **Purpose**: Extract detailed reaction data
- **Tools**: StagehandTool with modal handling
- **Responsibilities**:
  - Open reaction modals
  - Extract reactor details
  - Handle reaction pagination
  - Implement rate limiting

#### Data Analyst Agent
- **Purpose**: Process and analyze extracted data
- **Tools**: Built-in analysis capabilities
- **Responsibilities**:
  - Pattern recognition
  - Trend analysis
  - Engagement metrics calculation
  - Insight generation

#### Reporter Agent
- **Purpose**: Generate intelligence reports
- **Tools**: Report generation utilities
- **Responsibilities**:
  - Compile analysis results
  - Format comprehensive reports
  - Generate recommendations
  - Create actionable insights

### 2. Automation Layer (Stagehand + Browserbase)

#### StagehandTool Integration
```typescript
const stagehandTool = StagehandTool({
    api_key: process.env.BROWSERBASE_API_KEY,
    project_id: process.env.BROWSERBASE_PROJECT_ID,
    model_api_key: process.env.OPENAI_API_KEY,
    model_name: AvailableModel.GPT_4O,
});
```

#### Browser Session Management
- **Stealth Features**: Fingerprinting, proxy rotation
- **Session Persistence**: Reuse authenticated sessions
- **Error Recovery**: CAPTCHA handling, debug URLs
- **Rate Limiting**: Human-like timing patterns

### 3. Data Layer

#### Input Data
```typescript
interface ExecutionInput {
    profileUrl: string;      // Target LinkedIn profile
    daysBack: number;        // How far back to search
    maxPosts?: number;       // Limit number of posts
    includeComments?: boolean; // Extract comments too
}
```

#### Intermediate Data
```typescript
interface PostMetadata {
    url: string;
    timestamp: Date;
    content: string;
    engagementCounts: {
        likes: number;
        comments: number;
        shares: number;
    };
}
```

#### Output Data
```typescript
interface IntelligenceReport {
    summary: ExecutionSummary;
    topEngagers: EngagerProfile[];
    contentInsights: ContentAnalysis;
    audienceAnalysis: AudienceBreakdown;
    recommendations: string[];
}
```

## Data Flow

### 1. Initialization Flow
```
User Input → Environment Validation → Agent Initialization → Tool Setup
```

### 2. Execution Flow
```
Navigator Agent (Auth) → 
Post Hunter (Discovery) → 
Reaction Harvester (Extraction) → 
Data Analyst (Processing) → 
Reporter (Output)
```

### 3. Data Transformation Flow
```
Raw HTML → Structured Data → Analysis Results → Intelligence Report
```

## File Structure

```
ReactionReach/
├── src/
│   ├── agents/
│   │   ├── navigator.py          # Authentication & navigation
│   │   ├── post_hunter.py        # Post discovery
│   │   ├── reaction_harvester.py # Reaction extraction
│   │   ├── data_analyst.py       # Pattern analysis
│   │   └── reporter.py           # Report generation
│   ├── tasks/
│   │   ├── authentication.py    # Auth task definitions
│   │   ├── discovery.py         # Post discovery tasks
│   │   ├── extraction.py        # Reaction extraction tasks
│   │   ├── analysis.py          # Data analysis tasks
│   │   └── reporting.py         # Report generation tasks
│   ├── tools/
│   │   ├── stagehand_tool.py    # Stagehand integration
│   │   ├── stealth_manager.py   # Anti-detection utilities
│   │   └── data_processor.py    # Data transformation
│   ├── models/
│   │   ├── data_schemas.py      # Pydantic models
│   │   └── report_templates.py  # Report formatting
│   ├── config/
│   │   ├── agents.yaml          # Agent configurations
│   │   ├── tasks.yaml           # Task definitions
│   │   └── settings.py          # Application settings
│   └── main.py                  # Entry point
├── ai-docs/                     # Documentation for AI Assistant
├── data/                        # Output directory
├── tests/                       # Test suites
└── config/                      # Configuration files
```

## Security Architecture

### 1. Credential Management
- Environment variables for API keys
- No hardcoded secrets
- Secure session storage

### 2. Stealth Operations
- Browserbase fingerprinting
- Proxy rotation
- Human-like delays
- Session rotation

### 3. Error Handling
- Graceful degradation
- Retry mechanisms
- Manual intervention points
- Debug URL generation

## Scalability Considerations

### 1. Multi-Profile Support
- Parallel crew execution
- Resource pooling
- Session management across profiles

### 2. Performance Optimization
- Efficient data extraction
- Minimal redundant requests
- Intelligent caching
- Rate limiting compliance

### 3. Resource Management
- Memory usage optimization
- Session cleanup
- Error recovery
- Monitoring and alerting

## Integration Points

### 1. External APIs
- Browserbase API
- OpenAI API
- LinkedIn (via browser automation)

### 2. Data Storage
- JSON file output
- SQLite for persistence (future)
- Report generation (Markdown/HTML)

### 3. Monitoring
- Console logging
- Error tracking
- Performance metrics
- Debug capabilities

This architecture provides a robust, scalable foundation for LinkedIn intelligence gathering while maintaining stealth and compliance with platform guidelines.