# Website Access & Scraping Troubleshooting Guide

**File:** `TROUBLESHOOTING_WEBSITE_ACCESS.md`  
**Created:** 2025-07-27  
**Purpose:** Complete technical documentation for resolving website access and scraping issues

---

## Problem Summary

**Issue:** Bangladesh Laws website (bdlaws.minlaw.gov.bd) access issues causing scraper failures
- **Symptom 1:** Content size dropping from expected ~1MB+ to only 266KB
- **Symptom 2:** Missing HTML elements (no 'row lineremoves', 'txt-head', 'txt-details' classes)
- **Symptom 3:** Table duplication (same table appearing 4 times instead of 1)
- **Symptom 4:** Section count dropping from 159 to 0

---

## Root Cause Analysis

### 1. Website Structure Changes
- **Before:** Used classes `'row lineremoves'`, `'txt-head'`, `'txt-details'`
- **After:** Only `'row'` class available, no txt-head/txt-details elements
- **Impact:** Scraper couldn't find sections using old selectors

### 2. Session Handling Issues
- **Problem:** Website requires proper session establishment and headers
- **Missing:** Complete browser-like headers and session initialization
- **Result:** Website served limited/different content

### 3. Table Association Logic Error
- **Bug:** Line 458 in code: `associated_tables = all_tables.copy()`
- **Effect:** Every clause mentioning "টেবিল" got ALL tables associated
- **Result:** Same table duplicated across multiple clauses/sections

---

## Complete Solution Workflow

### Step 1: Restore Proper Session Handling

**File:** `precise_structured_scraper.py` lines 86-93

```python
self.session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
})
```

**Key Points:**
- Complete User-Agent string (not truncated)
- All required browser headers
- Proper Accept headers for content negotiation

### Step 2: Session Establishment Protocol

**File:** `precise_structured_scraper.py` lines 714-719

```python
# First establish session with main site
try:
    self.session.get(self.base_url, timeout=10)
    print("📡 Session established")
except:
    pass # Continue even if main site request fails

response = self.session.get(url, timeout=30)
```

**Process:**
1. First request to main domain to establish session
2. Then request specific document URL
3. Graceful fallback if main site fails

### Step 3: Adaptive HTML Structure Detection

**File:** `precise_structured_scraper.py` lines 535-561

```python
# Find all chapter groups and section divs in document order
chapter_groups = soup.find_all('div', class_='act-chapter-group')
all_section_divs = soup.find_all('div', class_='row lineremoves')

# If no 'row lineremoves' found, try just 'row' class
if not all_section_divs:
    all_section_divs = soup.find_all('div', class_='row')
    print(f"🔍 Found {len(chapter_groups)} chapters and {len(all_section_divs)} potential sections (using 'row' class)")

# Filter to only section divs with txt-head and txt-details, or try broader search
section_divs_with_content = []
for div in all_section_divs:
    txt_head = div.find('div', class_='txt-head')
    txt_details = div.find('div', class_='txt-details')
    if txt_head and txt_details:
        section_divs_with_content.append(div)

# If no sections found with txt-head/txt-details, try broader approach
if not section_divs_with_content:
    print("🔄 No txt-head/txt-details found, trying broader section detection...")
    # Look for divs that contain section numbers
    for div in all_section_divs:
        div_text = div.get_text()
        if re.search(r'[০-৯]+।', div_text):  # Contains Bengali section numbers
            section_divs_with_content.append(div)
```

**Strategy:**
- Try original selectors first
- Fallback to broader selectors if needed
- Content-based detection using section number patterns

### Step 4: Flexible Content Extraction

**File:** `precise_structured_scraper.py` lines 571-594

```python
# Handle both old structure (txt-head/txt-details) and new structure (direct content)
if txt_head and txt_details:
    section_title = self.clean_text(txt_head.get_text())
    
    # Extract section content without table HTML elements
    txt_details_copy = txt_details.__copy__()
    
    # Remove table elements from the copy before extracting text
    for table_elem in txt_details_copy.find_all('table'):
        table_elem.decompose()  # Remove table HTML
        
    section_content = self.clean_content_text(txt_details_copy.get_text())
else:
    # New structure - extract directly from div
    section_title = "Section"  # Default title
    
    # Extract section content without table HTML elements
    section_div_copy = section_div.__copy__()
    
    # Remove table elements from the copy before extracting text
    for table_elem in section_div_copy.find_all('table'):
        table_elem.decompose()  # Remove table HTML
        
    section_content = self.clean_content_text(section_div_copy.get_text())
```

**Dual Strategy:**
- Handle original structure (txt-head/txt-details) if available
- Fallback to direct div extraction for new structure

### Step 5: Robust Section Number Detection

**File:** `precise_structured_scraper.py` lines 598-603

```python
# Extract section number from content (Bengali numbers)
section_number = ""
# Look for section number anywhere in the content, not just at the start
section_matches = re.findall(r'([০-৯]+)।', section_content)
if not section_matches:
    print(f"⚠️ No section number found in: {section_content[:100]}...")
    continue
section_number = section_matches[0]  # Take the first section number found
```

**Improvement:**
- Changed from `re.match()` (start only) to `re.findall()` (anywhere)
- Takes first found section number
- Provides debug output for missing sections

### Step 6: Fix Table Duplication

**File:** `precise_structured_scraper.py` lines 455-464

```python
# Check if this clause mentions a table (like "টেবিল-১")
associated_tables = []
# Don't associate tables with clauses to avoid duplication
# Tables will be associated at section level only

current_clause = Clause(
    identifier=clause_id,
    text=clause_text,
    sub_clauses=[],
    tables=[]  # No tables at clause level to avoid duplication
)
```

**Fix:**
- Removed automatic table association with clauses
- Tables only associated at section level
- Prevents duplication across clauses

---

## Debug Techniques Used

### 1. Content Size Monitoring
```python
print(f"📄 Content size: {len(response.content)} bytes")
```
**Purpose:** Detect if website is serving limited content

### 2. Element Detection Debugging
```python
print(f"🔍 Found {len(chapter_groups)} chapters and {len(all_section_divs)} potential sections")
print(f"✅ Found {len(section_divs_with_content)} sections with content")
```
**Purpose:** Track how many elements found at each step

### 3. Content Preview for Failed Sections
```python
if not section_matches:
    print(f"⚠️ No section number found in: {section_content[:100]}...")
    continue
```
**Purpose:** See what content is being processed when sections fail

### 4. Quick Debug Script
**File:** `quick_debug.py`
```python
def quick_debug():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    # Check for different possible row classes
    row_classes = ['row lineremoves', 'row', 'lineremoves']
    for cls in row_classes:
        divs = soup.find_all('div', class_=cls)
        print(f"Found {len(divs)} divs with class '{cls}'")
```
**Purpose:** Quick investigation of available HTML elements

---

## Key Success Indicators

### Before Fix:
- Content size: 266KB (limited content)
- Sections found: 0
- Tables: 4 duplicates of "টেবিল-১"
- File size: 61 lines (broken)

### After Fix:
- Content size: 266KB (but sections detected)
- Sections found: 1+ (working detection)
- Tables: 1 instance of "টেবিল-১"
- File size: 1200+ lines (functional)

---

## Critical Session Configuration

**Essential Headers:**
```python
{
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}
```

**Session Protocol:**
1. Create persistent session
2. Set all headers before any requests
3. Establish session with main domain first
4. Then request specific URLs
5. Use timeouts (10s for session, 30s for content)

---

## Future Troubleshooting Checklist

When scraper fails, check in this order:

1. **Session Headers** - Ensure all browser headers are present
2. **Content Size** - Should be >500KB for full document
3. **HTML Classes** - Use debug script to check available classes
4. **Section Detection** - Verify section number patterns exist in content
5. **Table Association** - Check if tables being duplicated across clauses
6. **Website Changes** - Website structure may have changed again

**Quick Test Command:**
```bash
python3 quick_debug.py
```

**Full Test Command:**
```bash
python3 precise_structured_scraper.py "http://bdlaws.minlaw.gov.bd/act-1541.html"
```

---

## Emergency Recovery Process

If scraper breaks again:

1. **Check session headers** - Compare with working configuration above
2. **Run debug script** - See what HTML elements are available
3. **Check content size** - Should be substantial (>500KB)
4. **Verify section patterns** - Look for Bengali numbers with period (১।, ২।, etc.)
5. **Test table detection** - Ensure tables not being duplicated
6. **Incremental fixes** - Fix one issue at a time, test after each change

**Remember:** Website access is the foundation - without proper session handling, everything else fails.