# ReactionReach 🚀

> LinkedIn Reaction Intelligence System using CrewAI + Stagehand + Browserbase

**ReactionReach** is a multi-agent system that tracks and analyzes reactions to your LinkedIn posts, providing deep intelligence about who's engaging with your content and how.

## ✨ Features

- **🤖 Multi-Agent Intelligence**: CrewAI-powered specialist agents for each task
- **🕵️ Stealth Operation**: Browserbase enterprise infrastructure with anti-detection
- **🧠 AI-Powered Navigation**: Stagehand handles complex LinkedIn interactions
- **📊 Deep Analytics**: Comprehensive engagement pattern analysis
- **📋 Intelligence Reports**: Actionable insights and recommendations

## 🏗️ Architecture

```
Navigator Agent → Post Hunter → Reaction Harvester → Data Analyst → Reporter
```

Each agent specializes in a specific task, working together to provide comprehensive LinkedIn intelligence.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Browserbase account & API key
- OpenAI API key
- LinkedIn account

### Installation

```bash
# Clone the repository
git clone https://github.com/adamanzuoni/ReactionReach.git
cd ReactionReach

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` with your credentials:

```bash
BROWSERBASE_API_KEY=your_browserbase_api_key
BROWSERBASE_PROJECT_ID=your_browserbase_project_id
OPENAI_API_KEY=your_openai_api_key
LINKEDIN_PROFILE_URL=https://linkedin.com/in/your-profile
```

### Usage

```bash
# Build the project
npm run build

# Run the intelligence gathering
npm start

# Or run in development mode
npm run dev
```

## 🎯 What It Does

1. **Authenticates** to LinkedIn using stealth browser automation
2. **Discovers** all your posts from the last 30 days (configurable)
3. **Extracts** detailed reaction data from each post
4. **Analyzes** engagement patterns and audience behavior
5. **Reports** actionable insights and recommendations

## 📊 Output

### Data Files
- `data/reactions.json` - Raw reaction data
- `data/posts.json` - Post metadata
- `data/intelligence-report.md` - Comprehensive analysis

### Sample Intelligence Report

```markdown
# LinkedIn Engagement Intelligence Report

## Executive Summary
- 47 posts analyzed over 30 days
- 1,247 total reactions collected
- Top engager: John Smith (12 reactions)
- Best performing content: Technical tutorials

## Key Insights
- 68% of engagement comes from your industry network
- Posts with code examples get 3x more reactions
- Optimal posting time: Tuesday 10-11 AM

## Recommendations
1. Focus on technical content with code examples
2. Engage more with your top 10 reactors
3. Post consistently on Tuesday mornings
```

## 🔧 Configuration

### Agent Behavior
Customize agent behavior in `src/config/`:
- `agents.yaml` - Agent configurations
- `tasks.yaml` - Task definitions
- `settings.ts` - Application settings

### Stealth Settings
Adjust automation behavior:
- Rate limiting delays
- Browser fingerprinting
- Session rotation timing
- Error recovery strategies

## 🛡️ Security & Compliance

### Platform Respect
- Respectful rate limiting (2-5 second delays)
- Human-like behavior patterns
- LinkedIn terms of service compliance
- No aggressive automation

### Data Privacy
- Local data storage only
- No cloud data transmission
- Public data only (visible reactions)
- Data deletion capabilities

## 🧪 Development

### Project Structure

```
src/
├── agents/           # CrewAI agent definitions
├── tasks/            # Task configurations  
├── tools/            # Custom tools and utilities
├── models/           # Data models and schemas
├── config/           # Configuration files
└── main.ts           # Entry point
```

### Running Tests

```bash
npm test
```

### Code Quality

```bash
# Linting
npm run lint

# Formatting
npm run format
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## ⚠️ Disclaimer

This tool is for educational and personal insight purposes. Please:
- Respect LinkedIn's terms of service
- Use responsibly and ethically
- Don't use for commercial data harvesting
- Respect individual privacy

## 🔗 Links

- [Browserbase Documentation](https://docs.browserbase.com)
- [Stagehand Documentation](https://docs.stagehand.dev)
- [CrewAI Documentation](https://docs.crewai.com)

---

**Built with ❤️ for LinkedIn intelligence**