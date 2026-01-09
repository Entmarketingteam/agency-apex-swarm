"""Script to import leads from CSV file."""

import csv
import sys
from pathlib import Path
from typing import List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.lead import Lead
from utils.logger import get_logger

logger = get_logger(__name__)


def import_from_csv(filepath: str) -> List[Lead]:
    """
    Import leads from a CSV file.
    
    Expected CSV format:
    name,handle,platform,bio,linkedin_url,email
    
    Args:
        filepath: Path to CSV file
    
    Returns:
        List of Lead objects
    """
    leads = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                try:
                    lead = Lead(
                        name=row.get('name', '').strip() or None,
                        handle=row.get('handle', '').strip() or None,
                        platform=row.get('platform', 'instagram').strip().lower(),
                        bio=row.get('bio', '').strip() or None,
                        linkedin_url=row.get('linkedin_url', '').strip() or None,
                        email=row.get('email', '').strip() or None
                    )
                    
                    # Validate required fields
                    if not lead.handle and not lead.name:
                        logger.warning(f"Row {row_num}: Skipping - no name or handle")
                        continue
                    
                    leads.append(lead)
                    logger.debug(f"Row {row_num}: Imported {lead.handle or lead.name}")
                    
                except Exception as e:
                    logger.error(f"Row {row_num}: Error importing lead - {e}")
                    continue
        
        logger.info(f"Successfully imported {len(leads)} leads from {filepath}")
        return leads
        
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return []
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return []


def create_sample_csv(filepath: str = "leads/sample_leads.csv"):
    """Create a sample CSV file with example leads."""
    import os
    
    # Create leads directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    sample_data = [
        {
            'name': 'Fashion Creator',
            'handle': 'fashion_creator_2024',
            'platform': 'instagram',
            'bio': 'Fashion and lifestyle content creator',
            'linkedin_url': '',
            'email': ''
        },
        {
            'name': 'Tech Influencer',
            'handle': 'tech_influencer',
            'platform': 'tiktok',
            'bio': 'Tech reviews and tutorials',
            'linkedin_url': '',
            'email': ''
        },
    ]
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'handle', 'platform', 'bio', 'linkedin_url', 'email'])
        writer.writeheader()
        writer.writerows(sample_data)
    
    logger.info(f"Created sample CSV file: {filepath}")


def main():
    """CLI interface for importing leads."""
    if len(sys.argv) < 2:
        print("Usage: python import_leads.py <csv_file>")
        print("\nOr create a sample CSV:")
        print("  python import_leads.py --create-sample")
        return
    
    if sys.argv[1] == "--create-sample":
        create_sample_csv()
        return
    
    csv_file = sys.argv[1]
    leads = import_from_csv(csv_file)
    
    print(f"\nImported {len(leads)} leads:")
    for lead in leads:
        print(f"  - {lead.name or 'N/A'} (@{lead.handle or 'N/A'}) on {lead.platform}")


if __name__ == "__main__":
    main()


