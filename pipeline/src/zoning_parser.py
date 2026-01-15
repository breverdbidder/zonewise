"""
ZoneWise Zoning Parser
Extracts zoning district information from scraped Municode content
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ZoningDistrict:
    """Parsed zoning district"""
    jurisdiction_id: int
    code: str
    name: str
    category: str
    description: str
    ordinance_section: Optional[str] = None
    min_lot_size: Optional[int] = None
    max_height: Optional[int] = None
    max_lot_coverage: Optional[int] = None
    front_setback: Optional[int] = None
    side_setback: Optional[int] = None
    rear_setback: Optional[int] = None
    max_density: Optional[str] = None
    permitted_uses: Optional[List[str]] = None
    conditional_uses: Optional[List[str]] = None
    effective_date: str = "2024-01-01"


class ZoningParser:
    """Parser for zoning ordinance content"""
    
    # Category detection keywords
    CATEGORY_KEYWORDS = {
        "Residential": [
            "residential", "single-family", "single family", "multi-family", 
            "multifamily", "duplex", "dwelling", "home", "house", "apartment",
            "townhouse", "condominium"
        ],
        "Commercial": [
            "commercial", "business", "retail", "office", "store", "shop",
            "restaurant", "hotel", "motel", "service"
        ],
        "Industrial": [
            "industrial", "manufacturing", "warehouse", "factory", "plant",
            "processing", "fabrication", "assembly"
        ],
        "Mixed-Use": [
            "mixed-use", "mixed use", "planned unit", "pud", "planned development",
            "town center", "overlay"
        ],
        "Agricultural": [
            "agricultural", "rural", "farming", "ranch", "agri", "estate"
        ],
        "Institutional": [
            "institutional", "public", "government", "civic", "school",
            "church", "hospital", "park"
        ],
        "Conservation": [
            "conservation", "preservation", "environmental", "wetland",
            "coastal", "floodplain"
        ]
    }
    
    # District code patterns
    DISTRICT_CODE_PATTERNS = [
        # Standard patterns: R-1, C-2, RM-3, etc.
        r'\b([A-Z]{1,3}-\d{1,2}[A-Z]?)\b',
        # Alphanumeric: R1, C2, etc.
        r'\b([A-Z]{1,2}\d{1,2})\b',
        # Named districts: PUD, CBD, etc.
        r'\b(PUD|CBD|TOD|MXD|AG|RR|GU|ITU|LIU)\b',
    ]
    
    # Section reference patterns
    SECTION_PATTERNS = [
        r'[Ss]ec(?:tion)?\.?\s*(\d+[-–.]\d+(?:[-–.]\d+)?)',
        r'§\s*(\d+[-–.]\d+(?:[-–.]\d+)?)',
        r'[Aa]rticle\s+([IVXLC]+|\d+)',
    ]
    
    # Numeric extraction patterns
    NUMERIC_PATTERNS = {
        "min_lot_size": [
            r'(?:minimum|min\.?)\s+(?:lot\s+)?(?:area|size)[:\s]+(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft|square\s*feet)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft|square\s*feet)\s+(?:minimum|min)',
        ],
        "max_height": [
            r'(?:maximum|max\.?)\s+(?:building\s+)?height[:\s]+(\d+)\s*(?:feet|ft|\')',
            r'(\d+)\s*(?:feet|ft|\')\s+(?:maximum|max)',
            r'height[:\s]+(\d+)\s*(?:feet|ft)',
        ],
        "max_lot_coverage": [
            r'(?:maximum|max\.?)\s+(?:lot\s+)?coverage[:\s]+(\d+)\s*%',
            r'lot\s+coverage[:\s]+(\d+)\s*%',
        ],
        "front_setback": [
            r'front[:\s]+(\d+)\s*(?:feet|ft|\')',
            r'front\s+(?:yard\s+)?setback[:\s]+(\d+)',
        ],
        "side_setback": [
            r'side[:\s]+(\d+)\s*(?:feet|ft|\')',
            r'side\s+(?:yard\s+)?setback[:\s]+(\d+)',
        ],
        "rear_setback": [
            r'rear[:\s]+(\d+)\s*(?:feet|ft|\')',
            r'rear\s+(?:yard\s+)?setback[:\s]+(\d+)',
        ],
    }
    
    def __init__(self):
        pass
    
    def detect_category(self, text: str) -> str:
        """Detect zoning category from text"""
        text_lower = text.lower()
        
        # Count keyword matches for each category
        scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score
        
        if not scores:
            return "Other"
        
        # Return category with highest score
        return max(scores, key=scores.get)
    
    def extract_section(self, text: str) -> Optional[str]:
        """Extract ordinance section reference"""
        for pattern in self.SECTION_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return f"Sec. {match.group(1)}"
        return None
    
    def extract_numeric(self, text: str, field: str) -> Optional[int]:
        """Extract numeric value for a field"""
        patterns = self.NUMERIC_PATTERNS.get(field, [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).replace(",", "")
                try:
                    return int(value)
                except ValueError:
                    continue
        return None
    
    def extract_description(self, text: str, max_length: int = 500) -> str:
        """Extract a clean description from district text"""
        # Remove section numbers and formatting
        clean = re.sub(r'[§\*#]+', '', text)
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # Find intent or purpose statement
        intent_match = re.search(
            r'(?:intent|purpose|provisions)[:\.]?\s*(.{50,500}?)(?:\.|$)',
            clean, re.IGNORECASE
        )
        
        if intent_match:
            desc = intent_match.group(1).strip()
        else:
            # Take first substantial paragraph
            paragraphs = [p.strip() for p in clean.split('\n') if len(p.strip()) > 50]
            desc = paragraphs[0] if paragraphs else clean[:max_length]
        
        # Truncate if needed
        if len(desc) > max_length:
            desc = desc[:max_length-3] + "..."
        
        return desc
    
    def parse_district_section(self, text: str, jurisdiction_id: int, 
                               code: str, name: str) -> ZoningDistrict:
        """Parse a single district section"""
        
        category = self.detect_category(text)
        section = self.extract_section(text)
        description = self.extract_description(text)
        
        # Extract numeric values
        min_lot = self.extract_numeric(text, "min_lot_size")
        max_height = self.extract_numeric(text, "max_height")
        max_coverage = self.extract_numeric(text, "max_lot_coverage")
        front_setback = self.extract_numeric(text, "front_setback")
        side_setback = self.extract_numeric(text, "side_setback")
        rear_setback = self.extract_numeric(text, "rear_setback")
        
        return ZoningDistrict(
            jurisdiction_id=jurisdiction_id,
            code=code,
            name=name,
            category=category,
            description=description,
            ordinance_section=section,
            min_lot_size=min_lot,
            max_height=max_height,
            max_lot_coverage=max_coverage,
            front_setback=front_setback,
            side_setback=side_setback,
            rear_setback=rear_setback
        )
    
    def find_district_sections(self, content: str) -> List[Tuple[str, str, str]]:
        """
        Find all district sections in content
        
        Returns:
            List of (code, name, section_text) tuples
        """
        districts = []
        
        # Pattern for district headers like "§ 30-407. R-1A, single-family residential district"
        # or "Sec. 166-87. R-1 Single-family residential district"
        header_patterns = [
            # Municode style: § 30-407. R-1A, single-family residential district
            r'[§\*]*\s*(\d+[-–.]\d+)\.?\s+([A-Z]{1,3}[-–]?\d{0,2}[A-Z]?),?\s+(.+?district)',
            # Alternative: R-1. Single-Family Residential District
            r'([A-Z]{1,3}[-–]\d{1,2}[A-Z]?)[\.,]?\s+(.+?district)',
            # Section style: Section 24-5. RS-1 Single Family Residential
            r'[Ss]ection\s+(\d+[-–.]\d+)[\.,]?\s+([A-Z]{1,3}[-–]?\d{0,2}[A-Z]?)\s+(.+?)(?:\n|$)',
        ]
        
        # Split content into sections
        sections = re.split(r'\n(?=[§\*]*\s*\d+[-–.]\d+\.)', content)
        
        for section in sections:
            # Try each pattern
            for pattern in header_patterns:
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    
                    if len(groups) == 3:
                        # Pattern with section number
                        code = groups[1].upper().replace('–', '-')
                        name = groups[2].strip().title()
                    else:
                        # Pattern without section number
                        code = groups[0].upper().replace('–', '-')
                        name = groups[1].strip().title()
                    
                    # Clean up name
                    name = re.sub(r'\s+', ' ', name)
                    name = name.replace(' District', '').strip()
                    
                    districts.append((code, name, section))
                    break
        
        return districts
    
    def parse_content(self, content: str, jurisdiction_id: int, 
                      jurisdiction_name: str) -> List[ZoningDistrict]:
        """
        Parse all districts from content
        
        Args:
            content: Scraped markdown/HTML content
            jurisdiction_id: Database jurisdiction ID
            jurisdiction_name: Name for logging
            
        Returns:
            List of parsed ZoningDistrict objects
        """
        districts = []
        
        # Find all district sections
        sections = self.find_district_sections(content)
        
        print(f"[{jurisdiction_id}] Found {len(sections)} district sections in {jurisdiction_name}")
        
        for code, name, section_text in sections:
            district = self.parse_district_section(
                section_text, jurisdiction_id, code, name
            )
            districts.append(district)
            print(f"  - {code}: {name} ({district.category})")
        
        return districts
    
    def parse_file(self, filepath: str, jurisdiction_id: int, 
                   jurisdiction_name: str) -> List[ZoningDistrict]:
        """Parse a scraped content file"""
        with open(filepath, "r") as f:
            content = f.read()
        
        return self.parse_content(content, jurisdiction_id, jurisdiction_name)


def parse_all_scraped_files(scraped_dir: str = "data/scraped",
                            output_file: str = "data/parsed/all_districts.json") -> List[Dict]:
    """
    Parse all scraped files and output combined JSON
    """
    parser = ZoningParser()
    all_districts = []
    
    scraped_path = Path(scraped_dir)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    for filepath in sorted(scraped_path.glob("*.md")):
        # Extract jurisdiction ID from filename (e.g., "02_palm_bay.md")
        filename = filepath.stem
        parts = filename.split("_", 1)
        
        try:
            jurisdiction_id = int(parts[0])
            jurisdiction_name = parts[1].replace("_", " ").title() if len(parts) > 1 else "Unknown"
        except ValueError:
            print(f"Skipping {filepath} - cannot parse jurisdiction ID")
            continue
        
        # Parse the file
        districts = parser.parse_file(str(filepath), jurisdiction_id, jurisdiction_name)
        
        # Convert to dicts
        for d in districts:
            district_dict = asdict(d)
            # Remove None values for cleaner output
            district_dict = {k: v for k, v in district_dict.items() if v is not None}
            all_districts.append(district_dict)
    
    # Save combined output
    with open(output_file, "w") as f:
        json.dump(all_districts, f, indent=2)
    
    print(f"\nParsed {len(all_districts)} districts total")
    print(f"Saved to: {output_file}")
    
    return all_districts


if __name__ == "__main__":
    # Parse all scraped files
    districts = parse_all_scraped_files()
    
    # Summary by jurisdiction
    from collections import Counter
    by_jurisdiction = Counter(d["jurisdiction_id"] for d in districts)
    
    print("\nDistricts per jurisdiction:")
    for jid, count in sorted(by_jurisdiction.items()):
        print(f"  {jid}: {count} districts")
