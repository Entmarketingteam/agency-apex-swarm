# Implementation Plan: Agency Apex Swarm Lead Generation System

## Overview
Build a cloud-native orchestration system for influencer lead generation that processes 400 leads/day using multiple AI models and APIs in a coordinated workflow.

## Architecture

### Core Workflow
```
1. Lead Discovery (Input)
   ↓
2. Research & Validation (Perplexity API)
   ↓
3. Visual Vibe Check (Gemini 3.0 Ultra)
   ↓
4. Contact Discovery (Findymail API)
   ↓
5. Duplicate Check (Pinecone Vector DB)
   ↓
6. Content Generation (GPT-5.2 Pro)
   ↓
7. Outreach Execution (Unipile/Smartlead)
   ↓
8. Memory Storage (Pinecone)
```

## Component Breakdown

### 1. Main Orchestrator (`main.py`)
- Entry point for the system
- Uses Claude Opus 4.5 for programmatic tool calling
- Orchestrates all API calls in parallel where possible
- Implements exponential backoff retry logic
- Manages workflow state and error handling

### 2. API Client Modules

#### `api_clients/perplexity_client.py`
- Research and trend discovery
- Real-time information retrieval (< 24 hours old)
- Returns structured data about creators/trends

#### `api_clients/findymail_client.py`
- Email discovery from social handles
- LTK handle → verified business email
- Returns contact information

#### `api_clients/unipile_client.py`
- LinkedIn DM automation
- Message sending and tracking
- Returns delivery status

#### `api_clients/smartlead_client.py`
- Email sequence automation
- Campaign scheduling
- Follow-up management
- Returns campaign status

#### `api_clients/pinecone_client.py`
- Vector database operations
- Lead deduplication
- Similarity search for lookalike leads
- Stores lead embeddings

### 3. AI Model Wrappers

#### `ai_models/claude_client.py`
- Claude Opus 4.5 for orchestration
- Programmatic tool calling
- Complex logic and planning

#### `ai_models/openai_client.py`
- GPT-5.2 Pro for persuasive writing
- Email/DM content generation
- High-stakes outreach copy

#### `ai_models/gemini_client.py`
- Gemini 3.0 Ultra for visual analysis
- Instagram/TikTok post analysis
- Brand fit assessment
- Aesthetic and engagement quality

### 4. Core Modules

#### `utils/config.py`
- Environment variable loading
- Configuration management
- API key validation

#### `utils/retry.py`
- Exponential backoff implementation
- Retry decorators
- Error handling utilities

#### `utils/logger.py`
- Structured logging
- Activity tracking
- Error reporting

#### `models/lead.py`
- Lead data models
- Pydantic schemas for validation
- Data transformation utilities

## Implementation Steps

### Phase 1: Foundation (Current)
1. ✅ Environment setup (Codespace)
2. ✅ API keys configured
3. ⏳ Create project structure
4. ⏳ Install dependencies

### Phase 2: Core Infrastructure
1. Create `requirements.txt` with all dependencies
2. Build `utils/config.py` for environment management
3. Build `utils/retry.py` for error handling
4. Build `utils/logger.py` for logging
5. Create `models/lead.py` for data structures

### Phase 3: API Clients
1. Build Perplexity client
2. Build Findymail client
3. Build Unipile client
4. Build Smartlead client
5. Build Pinecone client

### Phase 4: AI Model Wrappers
1. Build Claude client (Opus 4.5)
2. Build OpenAI client (GPT-5.2 Pro)
3. Build Gemini client (3.0 Ultra)

### Phase 5: Orchestration
1. Build main.py with workflow logic
2. Implement programmatic tool calling
3. Add state management
4. Add error recovery

### Phase 6: Testing & Optimization
1. Test with sample leads
2. Optimize API call batching
3. Add monitoring and metrics
4. Scale to 400 leads/day

## Technical Specifications

### Dependencies
- `anthropic` - Claude API
- `openai` - GPT API
- `google-generativeai` - Gemini API
- `pinecone-client` - Vector DB
- `python-dotenv` - Environment variables
- `pydantic` - Data validation
- `httpx` - HTTP client (async)
- `tenacity` - Retry logic

### Error Handling
- Exponential backoff: 2s, 4s, 8s retries
- Maximum 3 retry attempts
- Graceful degradation on API failures
- Comprehensive error logging

### Performance Targets
- Process 400 leads/day
- Average 3-5 minutes per lead
- 80% cost reduction via programmatic tool calling
- 95%+ success rate on API calls

## Security
- All API keys in `.env` (gitignored)
- No keys in code
- Environment variable validation
- Secure API communication (HTTPS)

## Next Steps
1. Create project structure
2. Build foundation modules
3. Implement API clients
4. Build AI wrappers
5. Create main orchestrator
6. Test end-to-end workflow


