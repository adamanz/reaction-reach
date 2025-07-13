# LinkedIn Reaction Extraction & Email Outreach Workflow

## 🎯 Overview

This document describes the complete end-to-end workflow for extracting LinkedIn post reactions, enriching profiles with email addresses via Apollo.io, and sending personalized outreach emails.

## 📋 Prerequisites

### Required API Keys
- **Browserbase API Key**: For browser automation
- **Browserbase Project ID**: Your project identifier
- **OpenAI API Key**: For GPT-4o intelligent element selection
- **Apollo.io API Key**: For email enrichment
- **Gmail API Access**: For sending emails (via MCP server)

### Environment Setup
```bash
# In your .env file:
BROWSERBASE_API_KEY=your_key_here
BROWSERBASE_PROJECT_ID=your_project_id
OPENAI_API_KEY=your_openai_key
APOLLO_API_KEY=your_apollo_key
LINKEDIN_USERNAME=your_linkedin_email  # Optional if using context
LINKEDIN_PASSWORD=your_linkedin_password  # Optional if using context
```

## 🔄 Complete Workflow

### Step 1: Extract LinkedIn Reactions

**Script**: `smart_linkedin_extractor.py`

```bash
# Navigate to project directory
cd /Users/adamanzuoni/ReactionReach

# Activate virtual environment
source linkedin_env/bin/activate

# Run the extractor
python smart_linkedin_extractor.py
```

**What it does**:
1. Creates a Browserbase session with persistent context
2. Navigates to LinkedIn notifications page
3. Uses GPT-4o to intelligently find and click the most recent post
4. Clicks on reactions to expand the modal
5. Extracts all reactor profiles with:
   - Name
   - Title/Headline
   - Company
   - LinkedIn URL
   - Connection degree
6. Saves data to `reactions_data_[timestamp].json`
7. Creates `reactions_summary_[timestamp].md`

**Key Features**:
- Browserbase context ID: `929c2463-a010-4425-b900-4fde8a7ca327` (default)
- Anti-detection with US proxy
- GPT-4o powered element selection
- Automatic screenshot capture

### Step 2: Enrich with Apollo.io

The script automatically enriches profiles after extraction. Apollo searches for:
- Professional email addresses
- Current company details
- Job titles
- Employment history
- Location data

**Manual Apollo Enrichment** (if needed):
```python
# Using the Apollo MCP tool
mcp__apollo__people_enrichment(
    name="John Doe",
    organization_name="Company Name"
)
```

### Step 3: Generate Email Drafts

The workflow automatically creates Gmail drafts via the integrated `gmail_integration.py` module.

**What happens**:
1. For each reactor with/without email:
   - Creates personalized subject line
   - Generates contextual email body
   - Saves as Gmail draft
2. Creates summary report: `gmail_outreach_summary_[timestamp].md`

**Email Templates**:
- 1st connections: "Great connecting on LinkedIn, [Name]!"
- 2nd/3rd connections: "Following up on your reaction to my LinkedIn post"

### Step 4: Review and Send Emails

1. Check Gmail drafts folder
2. Review each email for personalization
3. Add specific details about their profile/company
4. Send individually or in batches

## 🤖 CrewAI Alternative Workflow

For a more structured approach, use the CrewAI implementation:

```bash
cd /Users/adamanzuoni/ReactionReach/linkedin-reaction-reach
crewai run
```

This orchestrates 4 specialized agents:
1. **LinkedIn Extractor Agent**
2. **Apollo Enricher Agent**
3. **Outreach Strategist Agent**
4. **Report Generator Agent**

## 📊 Output Files

### From Direct Script:
- `reactions_data_[timestamp].json` - Raw extraction data
- `reactions_summary_[timestamp].md` - Human-readable summary
- `gmail_outreach_summary_[timestamp].md` - Email draft summary
- Screenshots: `notifications_*.png`, `reactions_*.png`

### From CrewAI:
- `output/linkedin_reactions_report.md` - Comprehensive analysis
- All intermediate data in crew workspace

## 🛠️ Troubleshooting

### LinkedIn Authentication Issues
1. Check Browserbase context is valid
2. Manually log in to LinkedIn in Browserbase
3. Update context ID in script if needed

### No Reactions Found
1. Ensure you have a recent post with reactions
2. Check LinkedIn notifications are enabled
3. Try manual navigation first

### Apollo Rate Limits
1. Apollo has API rate limits
2. Space out requests if processing many profiles
3. Check your Apollo credit balance

### Gmail Draft Creation Fails
1. Ensure Gmail MCP server is running
2. Check authentication is valid
3. Verify email addresses are in correct format

## 📝 Best Practices

1. **Timing**: Run during business hours for better deliverability
2. **Personalization**: Always customize email drafts before sending
3. **Rate Limiting**: Don't extract/email too frequently
4. **Context**: Reference the specific post they reacted to
5. **Follow-up**: Track responses and engagement

## 🔍 Quick Commands Reference

```bash
# Extract reactions only
python smart_linkedin_extractor.py

# Extract with custom context
BROWSERBASE_CONTEXT_ID="your-id" python smart_linkedin_extractor.py

# Run CrewAI workflow
cd linkedin-reaction-reach && crewai run

# Check Gmail drafts via MCP
mcp__gmail__list_drafts()
```

## 📈 Success Metrics

Track these KPIs:
- Extraction success rate (aim for >90%)
- Email enrichment rate (typically 30-50%)
- Email open rates
- Response rates
- Connection acceptance rates

## 🔒 Security Notes

- Never commit `.env` files
- Rotate API keys regularly
- Use Browserbase contexts vs storing passwords
- Monitor Apollo credit usage
- Respect LinkedIn's terms of service

---

**Last Updated**: 2025-01-13
**Workflow Version**: 2.0
**Compatible with**: ReactionReach main branch