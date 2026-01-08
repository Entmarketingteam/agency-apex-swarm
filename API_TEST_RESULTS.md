# API Test Results

**Last Verified:** January 8, 2026

## ✅ Working APIs (7/8)

### Core AI Models
- ✅ **OpenAI (GPT-5.2 Pro)** - Working
- ✅ **Claude (Sonnet 4)** - Working (updated to `claude-sonnet-4-20250514`)

### Research & Discovery
- ✅ **Perplexity** - Working (updated to `sonar` model)
- ✅ **Findymail** - Working (URL: `app.findymail.com/api/search/name`)

### Outreach
- ✅ **Smartlead** - Working (URL: `server.smartlead.ai/api/v1`)
- ✅ **Unipile** - Initialized (requires DSN from dashboard for full test)

### Vector Database
- ✅ **Pinecone** - Working (`apex-leads` index)

## ❌ Needs Attention (1/8)

- ❌ **Gemini** - API key expired
  - Action: Get new key from [Google AI Studio](https://aistudio.google.com/)
  - Update in Railway variables and `.env`

## API Fixes Applied

| API | Issue | Fix |
|-----|-------|-----|
| Perplexity | 400 Bad Request | Changed model from `llama-3.1-sonar-large-128k-online` to `sonar` |
| Claude | 404 model not found | Changed from `claude-3-opus-20240229` to `claude-sonnet-4-20250514` |
| Findymail | DNS error | Changed URL from `api.findymail.com` to `app.findymail.com/api` |
| Findymail | 401 Unauthorized | Changed header from `X-API-Key` to `Authorization: Bearer` |
| Findymail | 422 format error | Changed params to use `name` + `domain` fields |
| Smartlead | Wrong URL | Changed from `api.smartlead.ai` to `server.smartlead.ai` |
| Smartlead | Auth format | Changed from header to query param `api_key` |

## Notes

- **Unipile** requires a DSN (Data Source Name) from your Unipile dashboard
  - Set `UNIPILE_DSN` environment variable (e.g., `api1.unipile.com`)
- System can run with 7/8 APIs - Gemini is optional for visual vibe checks

