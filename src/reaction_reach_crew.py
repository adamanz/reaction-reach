from crewai import Agent, Crew, Process, Task
from tools.linkedin_url_builder import linkedin_url_builder
from tools.browserbase_linkedin import browserbase_linkedin

# Import the tools
linkedin_navigator_tools = [linkedin_url_builder, browserbase_linkedin]
post_hunter_tools = [linkedin_url_builder, browserbase_linkedin]
reaction_harvester_tools = [linkedin_url_builder, browserbase_linkedin]

# 1. LinkedIn Navigator Agent
linkedin_navigator_agent = Agent(
    role="Authentication & Stealth Navigation Specialist",
    goal="Establish secure LinkedIn session and maintain stealth operation throughout the intelligence gathering process",
    backstory=(
        "You are an expert in web automation and anti-detection techniques. "
        "Your specialty is navigating LinkedIn's interface safely while avoiding detection. "
        "You understand LinkedIn's authentication flows, session management, and can "
        "implement human-like browsing patterns to maintain stealth operation."
    ),
    tools=linkedin_navigator_tools,
    allow_delegation=False,
    verbose=True
)

# 2. Post Hunter Agent  
post_hunter_agent = Agent(
    role="Content Discovery Specialist",
    goal="Find and catalog all posts from target user in specified timeframe with complete metadata",
    backstory=(
        "You are a specialist in LinkedIn content discovery and pagination handling. "
        "Your expertise lies in navigating LinkedIn's activity feeds, handling infinite scroll, "
        "and extracting comprehensive post metadata including URLs, timestamps, and content previews. "
        "You excel at finding posts with engagement and organizing them for further analysis."
    ),
    tools=post_hunter_tools,
    allow_delegation=False,
    verbose=True
)

# 3. Reaction Harvester Agent
reaction_harvester_agent = Agent(
    role="Engagement Data Extraction Expert", 
    goal="Extract detailed reaction data from each discovered post including reactor profiles and engagement patterns",
    backstory=(
        "You are an expert in data extraction and LinkedIn interface navigation. "
        "Your specialty is diving deep into individual posts to extract complete reaction data. "
        "You can navigate reaction modals, handle pagination in reaction lists, and collect "
        "detailed reactor profiles including names, job titles, companies, and reaction types. "
        "You implement respectful rate limiting to avoid detection."
    ),
    tools=reaction_harvester_tools,
    allow_delegation=False,
    verbose=True
)

# 4. Data Analyst Agent
data_analyst_agent = Agent(
    role="Engagement Intelligence Specialist",
    goal="Analyze reaction patterns and identify meaningful insights from collected engagement data",
    backstory=(
        "You are a data scientist specializing in social media engagement analytics. "
        "Your expertise lies in pattern recognition, trend analysis, and deriving actionable "
        "insights from raw engagement data. You can identify top engagers, analyze audience "
        "segments, calculate engagement metrics, and detect content performance correlations. "
        "You transform raw data into strategic intelligence."
    ),
    tools=[],  # Uses built-in analysis capabilities
    allow_delegation=False,
    verbose=True
)

# 5. Reporter Agent
reporter_agent = Agent(
    role="Intelligence Reporting Specialist",
    goal="Generate comprehensive actionable intelligence reports with strategic recommendations",
    backstory=(
        "You are a business intelligence expert who translates complex data into clear, "
        "actionable strategy. Your specialty is creating comprehensive reports that highlight "
        "key findings, identify opportunities, and provide specific recommendations. "
        "You excel at formatting insights for easy consumption and providing strategic next steps "
        "for content optimization and audience engagement."
    ),
    tools=[],  # Uses built-in reporting capabilities
    allow_delegation=False,
    verbose=True
)

def create_reaction_reach_crew(
    target_profile_url: str,
    days_back: int = 30,
    max_posts: int = 10
) -> Crew:
    """
    Creates and returns the ReactionReach crew with all agents and tasks configured
    
    :param target_profile_url: LinkedIn profile URL to analyze
    :param days_back: Number of days to look back for posts
    :param max_posts: Maximum number of posts to analyze
    :return: Configured CrewAI Crew instance
    """
    
    # Task 1: Navigate and Authenticate
    navigate_task = Task(
        description=(
            f"Navigate to LinkedIn profile {target_profile_url} and establish a secure session. "
            f"Ensure stealth operation and prepare for content discovery. "
            f"Verify the profile is accessible and return the profile's activity feed URL."
        ),
        expected_output="Confirmation of successful LinkedIn navigation and session establishment with activity feed URL",
        agent=linkedin_navigator_agent,
    )

    # Task 2: Hunt Posts
    hunt_posts_task = Task(
        description=(
            f"Discover and catalog all posts from the target profile from the last {days_back} days. "
            f"Extract post metadata including URLs, timestamps, content previews, and engagement indicators. "
            f"Focus on posts with reactions and comments. Limit to {max_posts} most recent posts with engagement."
        ),
        expected_output=(
            "JSON list of posts with metadata: post_url, timestamp, content_preview, "
            "reaction_count, comment_count, post_id for each discovered post"
        ),
        agent=post_hunter_agent,
        context=[navigate_task]  # Depends on navigation
    )

    # Task 3: Harvest Reactions
    harvest_reactions_task = Task(
        description=(
            "For each post discovered in the previous task, extract detailed reaction data. "
            "Navigate to each post's reaction details and collect: reactor names, profile URLs, "
            "job titles, companies, reaction types (like, celebrate, support, etc.), and connection degrees. "
            "Implement 2-5 second delays between requests for respectful rate limiting."
        ),
        expected_output=(
            "Complete reaction dataset in JSON format with reactor details for each post: "
            "reactor_name, profile_url, job_title, company, reaction_type, connection_degree, post_id"
        ),
        agent=reaction_harvester_agent,
        context=[hunt_posts_task]  # Depends on post discovery
    )

    # Task 4: Analyze Data
    analyze_data_task = Task(
        description=(
            "Analyze the collected reaction data to identify patterns and insights. "
            "Calculate engagement metrics, identify top engagers, analyze audience segments by industry/seniority, "
            "detect content performance correlations, and determine optimal posting patterns. "
            "Provide statistical analysis of reaction types and engagement trends."
        ),
        expected_output=(
            "Intelligence analysis report with: top 10 engagers, audience breakdown by industry/role, "
            "best performing content types, engagement patterns, and key insights for content strategy"
        ),
        agent=data_analyst_agent,
        context=[harvest_reactions_task]  # Depends on reaction data
    )

    # Task 5: Generate Report
    generate_report_task = Task(
        description=(
            "Create a comprehensive intelligence report combining all analysis results. "
            "Include executive summary, detailed findings, actionable recommendations, "
            "and strategic next steps. Format as a professional markdown report with clear sections "
            "for audience analysis, content insights, top engagers, and recommendations."
        ),
        expected_output=(
            "Professional markdown intelligence report with executive summary, detailed findings, "
            "audience analysis, content recommendations, and strategic action items"
        ),
        agent=reporter_agent,
        context=[analyze_data_task],  # Depends on analysis
        output_file='data/intelligence-report.md'
    )

    # Create and return the crew
    crew = Crew(
        agents=[
            linkedin_navigator_agent,
            post_hunter_agent, 
            reaction_harvester_agent,
            data_analyst_agent,
            reporter_agent
        ],
        tasks=[
            navigate_task,
            hunt_posts_task,
            harvest_reactions_task, 
            analyze_data_task,
            generate_report_task
        ],
        process=Process.sequential,  # Tasks run in sequence
        memory=True,  # Enable memory for context sharing
        cache=True,   # Enable caching for efficiency
        max_rpm=30,   # Conservative rate limiting for LinkedIn
        verbose=True,
        planning=True
    )
    
    return crew