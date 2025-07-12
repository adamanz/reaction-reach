# Stagehand + Browserbase Integration for LinkedIn Automation

## Core Integration Pattern

### Stagehand with Browserbase Configuration
```typescript
import { Stagehand } from "@browserbasehq/stagehand";

const stagehand = new Stagehand({
    env: "BROWSERBASE",
    apiKey: process.env.BROWSERBASE_API_KEY,
    projectId: process.env.BROWSERBASE_PROJECT_ID,
    modelName: "gpt-4o",
    modelClientOptions: {
        apiKey: process.env.OPENAI_API_KEY,
    },
    
    // Stealth and anti-detection
    browserbaseSessionCreateParams: {
        fingerprint: {
            locales: ["en-US"],
            operatingSystems: ["windows"],
        },
        enableProxy: true,
    },
    waitForCaptchaSolves: true,
    verbose: 1,
});
```

## LinkedIn-Specific Automation Patterns

### Authentication Flow
```typescript
async function authenticateLinkedIn(stagehand: Stagehand) {
    const page = stagehand.page;
    
    // Navigate to LinkedIn
    await page.goto("https://linkedin.com");
    
    // Check if already authenticated
    const isLoggedIn = await page.extract({
        instruction: "Check if user is already logged in by looking for profile elements",
        schema: z.object({
            isAuthenticated: z.boolean(),
            profileVisible: z.boolean(),
        }),
    });
    
    if (!isLoggedIn.isAuthenticated) {
        console.log("Manual authentication required");
        console.log("Please log in manually and press Enter when done");
        
        // Wait for manual authentication
        await new Promise(resolve => {
            process.stdin.once('data', () => resolve(void 0));
        });
    }
    
    return true;
}
```

### Post Discovery Pattern
```typescript
async function discoverUserPosts(stagehand: Stagehand, profileUrl: string, daysBack: number = 30) {
    const page = stagehand.page;
    
    // Navigate to user's recent activity
    await page.goto(`${profileUrl}/recent-activity/all/`);
    
    // Wait for content to load
    await page.waitForTimeout(3000);
    
    const posts = [];
    let scrollAttempts = 0;
    const maxScrolls = 10;
    
    while (scrollAttempts < maxScrolls) {
        // Extract visible posts
        const visiblePosts = await page.extract({
            instruction: `Extract all post data visible on screen including:
            - Post URL/ID 
            - Timestamp
            - Content preview
            - Engagement counts (likes, comments, shares)
            Only include posts from the last ${daysBack} days`,
            schema: z.object({
                posts: z.array(z.object({
                    url: z.string(),
                    timestamp: z.string(),
                    content: z.string(),
                    likeCount: z.number().optional(),
                    commentCount: z.number().optional(),
                    shareCount: z.number().optional(),
                }))
            }),
        });
        
        posts.push(...visiblePosts.posts);
        
        // Scroll to load more posts
        await page.act("scroll down to load more posts");
        await page.waitForTimeout(2000);
        
        scrollAttempts++;
    }
    
    // Remove duplicates
    const uniquePosts = posts.filter((post, index, self) =>
        index === self.findIndex(p => p.url === post.url)
    );
    
    return uniquePosts;
}
```

### Reaction Extraction Pattern
```typescript
async function extractPostReactions(stagehand: Stagehand, postUrl: string) {
    const page = stagehand.page;
    
    // Navigate to specific post
    await page.goto(postUrl);
    await page.waitForTimeout(2000);
    
    // Click on reaction counts to open modal
    await page.act("click on the reaction summary showing total likes and reaction types");
    
    // Wait for reaction modal to load
    await page.waitForTimeout(3000);
    
    const allReactions = [];
    let hasMoreReactions = true;
    
    while (hasMoreReactions) {
        // Extract visible reactions
        const reactionBatch = await page.extract({
            instruction: `Extract all visible reaction data including:
            - Person's name and profile URL
            - Reaction type (like, celebrate, support, love, insightful, funny)
            - Person's job title and company
            - Connection degree if visible`,
            schema: z.object({
                reactions: z.array(z.object({
                    name: z.string(),
                    profileUrl: z.string(),
                    reactionType: z.enum(['like', 'celebrate', 'support', 'love', 'insightful', 'funny']),
                    title: z.string(),
                    company: z.string().optional(),
                    connectionDegree: z.string().optional(),
                }))
            }),
        });
        
        allReactions.push(...reactionBatch.reactions);
        
        // Try to scroll for more reactions
        const scrollResult = await page.observe("check if there are more reactions to load by scrolling");
        
        if (scrollResult.length > 0) {
            await page.act("scroll down in the reactions modal to load more reactions");
            await page.waitForTimeout(1500);
        } else {
            hasMoreReactions = false;
        }
    }
    
    // Close modal
    await page.act("close the reactions modal");
    
    return allReactions;
}
```

### Error Handling & Recovery
```typescript
class LinkedInAutomationHandler {
    private stagehand: Stagehand;
    private sessionId: string;
    
    constructor(stagehand: Stagehand) {
        this.stagehand = stagehand;
    }
    
    async handleDetectionRecovery() {
        // Get debug URL for manual intervention
        const debugUrl = await this.getDebugUrl();
        
        console.log(`Manual intervention may be needed: ${debugUrl}`);
        console.log("Please check for CAPTCHAs or security challenges");
        
        // Wait for user confirmation
        await this.waitForUserConfirmation();
    }
    
    async getDebugUrl(): Promise<string> {
        // Get Browserbase session debug URL
        const response = await fetch(
            `https://www.browserbase.com/v1/sessions/${this.sessionId}/debug`,
            {
                headers: {
                    'x-bb-api-key': process.env.BROWSERBASE_API_KEY!,
                },
            }
        );
        
        const data = await response.json();
        return data.debuggerFullscreenUrl;
    }
    
    async waitForUserConfirmation() {
        return new Promise(resolve => {
            console.log("Press Enter when ready to continue...");
            process.stdin.once('data', () => resolve(void 0));
        });
    }
    
    async retryWithBackoff<T>(
        operation: () => Promise<T>,
        maxRetries: number = 3,
        baseDelay: number = 1000
    ): Promise<T> {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                return await operation();
            } catch (error) {
                if (attempt === maxRetries) {
                    throw error;
                }
                
                const delay = baseDelay * Math.pow(2, attempt - 1);
                console.log(`Attempt ${attempt} failed, retrying in ${delay}ms...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
        
        throw new Error("Max retries exceeded");
    }
}
```

### Rate Limiting & Stealth
```typescript
class StealthManager {
    private delays = {
        betweenPosts: () => this.randomDelay(2000, 5000),
        betweenReactions: () => this.randomDelay(1000, 3000),
        afterScroll: () => this.randomDelay(1500, 2500),
        beforeAction: () => this.randomDelay(500, 1500),
    };
    
    private randomDelay(min: number, max: number): number {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }
    
    async humanLikeDelay(type: keyof typeof this.delays) {
        const delay = this.delays[type]();
        await new Promise(resolve => setTimeout(resolve, delay));
    }
    
    async simulateHumanBehavior(page: any) {
        // Random mouse movements
        await page.evaluate(() => {
            const event = new MouseEvent('mousemove', {
                clientX: Math.random() * window.innerWidth,
                clientY: Math.random() * window.innerHeight,
            });
            document.dispatchEvent(event);
        });
        
        // Random small delays
        await this.humanLikeDelay('beforeAction');
    }
}
```

### Session Management
```typescript
class SessionManager {
    private stagehand: Stagehand;
    private sessionStartTime: Date;
    private maxSessionDuration = 30 * 60 * 1000; // 30 minutes
    
    constructor(stagehand: Stagehand) {
        this.stagehand = stagehand;
        this.sessionStartTime = new Date();
    }
    
    shouldRotateSession(): boolean {
        const now = new Date();
        const sessionDuration = now.getTime() - this.sessionStartTime.getTime();
        return sessionDuration > this.maxSessionDuration;
    }
    
    async rotateSession() {
        console.log("Rotating session for stealth...");
        
        // Close current session
        await this.stagehand.close();
        
        // Wait before creating new session
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Create new session with different fingerprint
        const newStagehand = new Stagehand({
            env: "BROWSERBASE",
            apiKey: process.env.BROWSERBASE_API_KEY,
            projectId: process.env.BROWSERBASE_PROJECT_ID,
            browserbaseSessionCreateParams: {
                fingerprint: {
                    locales: ["en-US", "en"],
                    operatingSystems: ["windows", "macos"][Math.floor(Math.random() * 2)],
                },
                enableProxy: true,
            },
        });
        
        await newStagehand.init();
        this.stagehand = newStagehand;
        this.sessionStartTime = new Date();
        
        return this.stagehand;
    }
}
```

## Best Practices

### 1. Always Use Delays
```typescript
// Between major actions
await stealthManager.humanLikeDelay('betweenPosts');

// Before clicking elements
await stealthManager.humanLikeDelay('beforeAction');
```

### 2. Handle Dynamic Content
```typescript
// Wait for dynamic content to load
await page.waitForTimeout(2000);

// Use observe to check element state
const observations = await page.observe("check if content has finished loading");
```

### 3. Graceful Error Handling
```typescript
try {
    const result = await extractPostReactions(stagehand, postUrl);
    return result;
} catch (error) {
    console.log(`Failed to extract reactions from ${postUrl}: ${error.message}`);
    return null; // Return null instead of crashing
}
```

### 4. Resource Cleanup
```typescript
// Always close Stagehand sessions
process.on('exit', async () => {
    await stagehand.close();
});

process.on('SIGINT', async () => {
    await stagehand.close();
    process.exit(0);
});
```

This integration provides a robust foundation for LinkedIn automation while maintaining stealth and reliability.