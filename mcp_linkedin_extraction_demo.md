# LinkedIn Post Extraction with MCP + Stagehand

## Overview

This demonstrates how to use Browserbase + Stagehand MCP servers with CrewAI for intelligent LinkedIn post extraction using natural language instructions.

## Architecture

```
CrewAI Agent → MCP Tools → Stagehand → Browserbase Context → LinkedIn
```

## Available MCP Tools

### Browserbase MCP Server
- **Purpose**: Raw browser automation and session management
- **Tools**: Basic browser operations, session creation, context management

### Stagehand MCP Server  
- **Purpose**: AI-powered browser automation with natural language
- **Tools**:
  - `stagehand_navigate`: Navigate to URLs
  - `stagehand_act`: Perform actions with natural language ("Click the login button", "Fill in username")
  - `stagehand_extract`: Extract structured data with JSON schema

## Usage Example

### 1. Navigate to LinkedIn Activity Page
```typescript
// Using Stagehand MCP tool
await stagehand_navigate({
  url: "https://linkedin.com/in/adamanz/recent-activity/all/"
});
```

### 2. Extract Posts with Natural Language
```typescript
// Using Stagehand extraction with schema
await stagehand_extract({
  instruction: "Extract the last 10 LinkedIn posts from this activity page",
  schema: {
    type: "object",
    properties: {
      posts: {
        type: "array",
        items: {
          type: "object", 
          properties: {
            content: { type: "string", description: "Post text content" },
            timestamp: { type: "string", description: "When the post was made" },
            reactions: { type: "number", description: "Number of reactions" },
            comments: { type: "number", description: "Number of comments" },
            shares: { type: "number", description: "Number of shares" }
          }
        }
      }
    }
  }
});
```

### 3. Handle Authentication (if needed)
```typescript
// Stagehand can handle complex flows
await stagehand_act({
  action: "Complete LinkedIn login process if prompted"
});
```

## CrewAI Integration

### Agent Definition
```python
linkedin_navigator = Agent(
    role='LinkedIn Navigator',
    goal='Extract posts and engagement data from LinkedIn profiles',
    backstory='Expert at navigating LinkedIn and extracting post data',
    tools=[
        # MCP tools are automatically available in yolo mode
        'stagehand_navigate',
        'stagehand_act', 
        'stagehand_extract'
    ]
)
```

### Task Definition
```python
extract_posts_task = Task(
    description='''
    Extract the last 10 posts from linkedin.com/in/adamanz using the 
    authenticated Browserbase context (b03b0494-a12d-4e4c-b99f-59651591529e).
    
    Steps:
    1. Navigate to the LinkedIn activity page
    2. Use natural language extraction to get post data
    3. Return structured JSON with post content, engagement metrics
    ''',
    agent=linkedin_navigator,
    expected_output='JSON array of 10 most recent posts with engagement data'
)
```

## Key Advantages

### 🤖 **AI-Powered Actions**
- Natural language instructions instead of CSS selectors
- "Click the login button" vs `await page.click('#login-submit')`
- Adapts to UI changes automatically

### 🔒 **Context Persistence**  
- Uses existing authenticated context: `b03b0494-a12d-4e4c-b99f-59651591529e`
- No re-authentication needed
- Instant access to LinkedIn

### 🚀 **Simplified Integration**
- Direct MCP tool calls in CrewAI agents
- No complex Playwright setup code
- Error handling built-in

### 📊 **Structured Extraction**
- JSON schema-based data extraction
- Consistent output format
- Type-safe results

## Test Commands

### Start with yolo (includes MCP servers):
```bash
source ~/.zshrc  # Reload with updated yolo command
yolo  # Now includes browserbase + stagehand MCP servers
```

### Available Tools in Claude Code:
- `stagehand_navigate` - Navigate to URLs
- `stagehand_act` - Perform actions with natural language  
- `stagehand_extract` - Extract data with JSON schemas

## Next Steps

1. **Test MCP Integration**: Run `yolo` to test the new MCP servers
2. **Extract Posts**: Use Stagehand tools to extract LinkedIn posts
3. **Build CrewAI Pipeline**: Create full multi-agent system
4. **Scale Up**: Add more LinkedIn intelligence gathering capabilities

## Environment Variables Required

```bash
# Already configured in .env
BROWSERBASE_API_KEY=bb_live_APnCzG_NvsKnCTvw-YGxJXnsMGk
BROWSERBASE_PROJECT_ID=91a6c1c4-ad01-4cf4-824a-37e7260bd114
OPENAI_API_KEY=sk-proj-y6n_...
CONTEXT_ID=b03b0494-a12d-4e4c-b99f-59651591529e
```

## Ready to Test!

The MCP + Stagehand setup is complete. You can now:
1. Run `yolo` to start Claude Code with MCP servers
2. Use natural language to extract LinkedIn posts
3. Build CrewAI agents with MCP tools
4. Leverage the persistent Browserbase Context for instant access