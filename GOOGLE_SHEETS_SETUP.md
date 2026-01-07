# 📊 Google Sheets Integration

Your system is now connected to Google Sheets! Just drop leads into your spreadsheet and they'll be automatically processed.

## Your Google Sheet
**URL:** https://docs.google.com/spreadsheets/d/1R2bYx2-G7cgtkv2GuiYqSZz-A7FOgh1V/edit

## ⚠️ IMPORTANT: Make Your Sheet Public

For the system to read your sheet, you need to make it publicly viewable:

1. Open your Google Sheet
2. Click **"Share"** (top right)
3. Click **"Change to anyone with the link"**
4. Set to **"Viewer"** (read-only is fine)
5. Click **"Done"**

## Required Column Headers

Your sheet should have these columns (first row):

| Column | Description | Required |
|--------|-------------|----------|
| `name` | Creator's name | Yes (or handle) |
| `handle` | Social media handle | Yes (or name) |
| `platform` | Platform (instagram, tiktok, etc.) | No (defaults to instagram) |
| `bio` | Creator's bio/description | No |
| `email` | Email if known | No |
| `linkedin` | LinkedIn URL if known | No |
| `status` | Processing status | No (used to track processed leads) |

### Example Sheet Structure

| name | handle | platform | bio | status |
|------|--------|----------|-----|--------|
| Fashion Creator | @fashion_guru | instagram | Fashion and lifestyle | |
| Tech Reviewer | @tech_review | tiktok | Tech reviews | |
| Beauty Influencer | @beauty_tips | instagram | Makeup tutorials | processed |

## How It Works

1. **Drop leads** into your Google Sheet
2. **System checks** the sheet every hour
3. **Unprocessed leads** (empty or "pending" status) are fetched
4. **Leads are processed** through the workflow
5. **Results** are logged to Railway

## Alternative Column Names

The system recognizes these alternative column names:

| Standard | Alternatives |
|----------|--------------|
| `name` | `creator_name`, `full_name` |
| `handle` | `username`, `instagram`, `ig` |
| `bio` | `description`, `notes` |
| `linkedin` | `linkedin_url` |

## Tips

1. **Add a "status" column** to track which leads have been processed
2. **Leave status empty** for new leads you want processed
3. **Set status to "processed"** after leads are handled (manual for now)
4. **Add new leads anytime** - they'll be picked up in the next hourly run

## Troubleshooting

### "No data found in sheet"
- Make sure the sheet is publicly viewable
- Check that the sheet has data starting from row 1 (headers)

### "Error reading sheet"
- Verify the Google API key is set in Railway
- Check that the sheet ID is correct

### Leads not being processed
- Check the "status" column - only empty or "pending" leads are processed
- Check Railway logs for errors

## Manual Testing

To test the Google Sheets connection locally:

```python
from api_clients.google_sheets_client import GoogleSheetsClient

client = GoogleSheetsClient()
leads = client.get_leads_from_sheet()
print(f"Found {len(leads)} leads")
for lead in leads:
    print(lead)
```

## Your Sheet ID
```
1R2bYx2-G7cgtkv2GuiYqSZz-A7FOgh1V
```

This is already configured in the system!

