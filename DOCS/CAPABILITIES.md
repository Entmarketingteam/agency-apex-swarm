# Agency Capability Registry (January 2026)

This is the "Source of Truth" for tool selection. The Agent reads this file to determine which capability to use for each task.

## Capability Matrix

| Capability | Model/Tool | Use Case | When to Use |
|------------|-----------|----------|-------------|
| **Visual Vibe Check** | Gemini 3.0 Ultra | Analyzing creator videos/images for brand fit | When you need to judge aesthetic, color palette, engagement quality from IG/TikTok posts |
| **Logic/Planning** | Claude Opus 4.5 | Determining workflow sequence and orchestration | When building system architecture or deciding tool-calling order |
| **Persuasive Writing** | GPT-5.2 Pro | Writing final pitch emails/DMs based on Vibe Check data | When crafting high-stakes outreach that requires human-expert level persuasion |
| **Identity/Contact** | Findymail API | Moving from LTK handle to verified business email | When you have a creator handle and need their professional email |
| **Search/Research** | Perplexity Pro API | Finding latest news, trends, or information | When information needs to be < 24 hours old or requires real-time search |
| **Messaging** | Unipile API | Sending LinkedIn DMs | When you need to automate LinkedIn outreach |
| **Email Automation** | Smartlead API | Scheduling and sending email sequences | When you need to schedule follow-ups or email campaigns |
| **Long-Term Memory** | Pinecone (Vector DB) | Checking if we've contacted a creator before | When you need similarity search or to avoid duplicate outreach |
| **Daily Code Edits** | Claude Sonnet 4.5 | Quick refactoring and terminal commands | For 90% of daily coding tasks (balance of smart + fast) |

## Decision Logic

### If the Task is...
- **"I need the latest news/posts"** → Use Perplexity MCP / @Web (Real-time search capability)
- **"I need to see if this IG looks good"** → Use Gemini 3.0 Ultra (Multimodal vision capability)
- **"I need to find a business email"** → Use Findymail API (Enrichment capability)
- **"I need to send a LinkedIn DM"** → Use Unipile API (Communication capability)
- **"I need to find 'lookalike' leads"** → Use Pinecone (Vector DB) (Memory/Similarity capability)
- **"I need to schedule an email"** → Use Smartlead API (Automation capability)
- **"I need to plan a complex workflow"** → Use Claude Opus 4.5 (Architecture/Reasoning capability)
- **"I need to write a persuasive email"** → Use GPT-5.2 Pro (High-stakes persuasion capability)

## Tool Calling Best Practices

1. **Programmatic Tool Calling**: Use Opus 4.5's programmatic tool calling to execute multiple API calls in one block, reducing token costs by 80%
2. **Error Handling**: Always implement exponential backoff (2s, 4s, 8s retries)
3. **Cost Optimization**: Use Gemini 3 Flash for simple tasks, reserve Opus 4.5 for complex orchestration
4. **Context Management**: Use programmatic tool calling to avoid bloating the context window with intermediate results


