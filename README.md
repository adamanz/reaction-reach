# LinkedIn Reactions Extractor

🚀 **Intelligent LinkedIn post reactions extraction using GPT-4o + Browserbase**

Automatically extracts detailed profile information from people who react to your most recent LinkedIn post, including names, titles, companies, connection degrees, and profile URLs.

## ✨ Features

- **🧠 GPT-4o Intelligence**: Uses GPT-4o to intelligently navigate LinkedIn and find the most recent post
- **🕵️ Stealth Automation**: Browserbase integration with persistent contexts to avoid detection
- **📊 Smart Extraction**: Automatically extracts detailed reactor profiles including:
  - Full names
  - Job titles and companies
  - Connection degrees (1st, 2nd, 3rd)
  - LinkedIn profile URLs
  - Professional affiliations
- **📄 Multiple Output Formats**: Generates both JSON data files and human-readable markdown summaries
- **📸 Screenshot Documentation**: Captures screenshots at each step for debugging and verification

## 🛠️ Setup

### Prerequisites

- Python 3.10+
- [Browserbase](https://browserbase.com) account and API key
- [OpenAI](https://openai.com) API key with GPT-4o access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/LinkedInReactionsExtractor.git
   cd LinkedInReactionsExtractor
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Install Playwright browsers**
   ```bash
   playwright install
   ```

### Environment Configuration

Edit your `.env` file with the required API keys:

```bash
# Browserbase Configuration (Required)
BROWSERBASE_API_KEY=your_browserbase_api_key_here
BROWSERBASE_PROJECT_ID=your_browserbase_project_id_here

# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Use pre-authenticated LinkedIn session
BROWSERBASE_CONTEXT_ID=your_context_id_here
```

### Browserbase Setup

1. **Create account** at [browserbase.com](https://browserbase.com)
2. **Get API key** from your dashboard
3. **Create a project** and note the project ID
4. **Optional**: Create a persistent context with LinkedIn authentication for best results

## 🚀 Usage

### Basic Extraction

Run the extractor to analyze your most recent LinkedIn post:

```bash
python smart_linkedin_extractor.py
```

### Expected Output

The script will:

1. **Navigate** to your LinkedIn notifications
2. **Identify** your most recent post using GPT-4o intelligence  
3. **Extract** detailed reactor profiles
4. **Generate** output files:
   - `reactions_data_[timestamp].json` - Raw structured data
   - `reactions_summary_[timestamp].md` - Human-readable report
   - Screenshots for verification

### Sample Output

```
🚀 LinkedIn Reactions Extractor (GPT-4o Powered)
============================================================
✅ Session: cb012c51-57e5-4aa4-96d6-96176ced857e
📍 Navigating to LinkedIn notifications (my posts)...
✅ Loaded: https://www.linkedin.com/notifications/?filter=my_posts_all
🧠 Analyzing page with GPT-4o...
🧠 GPT-4o suggested selector: 'a[href*="/feed/update/"]:first-of-type'
✅ Successfully clicked reaction area!
📊 EXTRACTING REACTOR DATA...
✅ Successfully extracted 9 reactor profiles!
💾 Data saved to: reactions_data_1752374826.json
📄 Summary report created: reactions_summary_1752374826.md

🏁 RESULT: SUCCESS ✅
```

## 📊 Output Format

### JSON Data (`reactions_data_[timestamp].json`)
```json
[
  {
    "name": "John Doe",
    "title": "Senior Software Engineer at Google",
    "company": "Google",
    "connection_degree": "1st",
    "profile_url": "https://linkedin.com/in/johndoe",
    "extraction_timestamp": "2025-01-15T10:30:00",
    "element_text": "John Doe\nSenior Software Engineer at Google..."
  }
]
```

### Markdown Summary (`reactions_summary_[timestamp].md`)
```markdown
# LinkedIn Post Reactions Analysis

**Extraction Date:** 2025-01-15 10:30:00
**Total Reactors:** 9

## 📊 Reactor Profiles

### 1. John Doe
- **Title:** Senior Software Engineer at Google
- **Company:** Google
- **Connection:** 1st
- **Profile:** https://linkedin.com/in/johndoe

## 📈 Summary Statistics

### Top Companies
- Google: 2
- Microsoft: 1

### Connection Degrees
- 1st: 7
- 2nd: 2
```

## 🔧 Advanced Configuration

### Custom Context ID

If you have a pre-authenticated LinkedIn session in Browserbase:

```bash
BROWSERBASE_CONTEXT_ID=your_authenticated_context_id
```

### Debug Mode

Enable debug mode for additional logging:

```bash
DEBUG_MODE=true
```

## 🚨 Important Notes

### LinkedIn Terms of Service
- This tool is for personal use only
- Respect LinkedIn's rate limits and terms of service
- Do not use for spam or harassment
- Only extract data from your own posts and public profiles

### Privacy & Ethics
- Only extracts publicly available information
- Respects connection privacy settings
- Does not store or transmit personal data beyond local files
- Users are responsible for complying with applicable privacy laws

### Rate Limiting
- Built-in delays to respect LinkedIn's servers
- Uses realistic human-like interaction patterns
- Browserbase provides additional IP rotation and fingerprint management

## 🐛 Troubleshooting

### Common Issues

**"Could not find post elements"**
- Ensure you have recent posts on your LinkedIn profile
- Check that your Browserbase context has valid LinkedIn authentication
- Try running during off-peak hours

**"GPT-4o API Error"**
- Verify your OpenAI API key has GPT-4o access
- Check your OpenAI usage limits and billing

**"Browserbase Connection Failed"**
- Verify your Browserbase API key and project ID
- Check Browserbase dashboard for session status
- Ensure you have available session credits

### Debug Steps

1. **Check screenshots** - The tool saves screenshots at each step
2. **Review console output** - Look for specific error messages
3. **Verify authentication** - Ensure LinkedIn session is valid
4. **Test connectivity** - Verify API keys work independently

## 📋 Requirements

- **Python**: 3.10 or higher
- **Browserbase**: Active account with available sessions
- **OpenAI**: API access with GPT-4o model availability
- **Internet**: Stable connection for API calls and LinkedIn access

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is provided "as is" without warranty. Users are responsible for:
- Complying with LinkedIn's Terms of Service
- Respecting privacy and data protection laws
- Using the tool ethically and responsibly
- Any consequences of its use

The authors are not responsible for any misuse or violations of terms of service.