import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

# List of URLs to scrape
urls = [
    'https://www.pieas.edu.pk/faculty-partials/fa-dche.cshtml',
    'https://www.pieas.edu.pk/faculty-partials/fa-dcis.cshtml',
    'https://www.pieas.edu.pk/faculty-partials/fa-dcms.cshtml',
    'https://www.pieas.edu.pk/faculty-partials/fa-dee.cshtml',
    'https://www.pieas.edu.pk/faculty-partials/fa-dme.cshtml',
    'https://www.pieas.edu.pk/faculty-partials/fa-dms.cshtml',
    'https://www.pieas.edu.pk/faculty-partials/fa-dmme.cshtml',
    'https://www.pieas.edu.pk/faculty-partials/fa-dne.cshtml',
    'https://www.pieas.edu.pk/faculty-partials/fa-dpam.cshtml'
]

# List to store faculty data
faculty_data = []

def clean_name(name_text):
    """Extract clean name from text that may contain titles and roles"""
    # Remove parenthetical content
    name_text = re.sub(r'\s*\([^)]*\)\s*', '', name_text)
    # Remove titles and roles after comma
    name_text = re.sub(r',\s*(Professor|Associate Professor|Assistant Professor|Head|Director|Coordinator|Pro-Rector|Lecturer|Manager|Warden).*$', '', name_text, flags=re.IGNORECASE)
    # Extract name before comma or end
    name_match = re.match(r'^([A-Za-z\s\.\-]+?)(?:,|$)', name_text.strip())
    if name_match:
        return name_match.group(1).strip()
    # Fallback: take first meaningful part
    parts = name_text.split(',')
    return parts[0].strip() if parts else name_text.strip()

def extract_email(email_text):
    """Extract email from text that may contain HTML or extra content"""
    # Remove HTML tags and image-related content
    email_text = re.sub(r'<[^>]+>', '', email_text)
    # Look for existing complete email
    full_email_match = re.search(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+)', email_text)
    if full_email_match:
        return full_email_match.group(1)
    # Look for email username part
    username_match = re.search(r'([a-zA-Z0-9._-]+)', email_text.strip())
    if username_match:
        username = username_match.group(1)
        if '@' not in username:
            return username + '@pieas.edu.pk'
        return username
    return ''

# Process each URL
for url_index, url in enumerate(urls):
    try:
        # Fetch HTML content
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes
        html_content = response.text

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all div elements with class 'note'
        faculty_divs = soup.find_all('div', class_='note')

        # Process each faculty div
        for div_index, div in enumerate(faculty_divs):
            try:
                # Find the inner table containing faculty details
                inner_table = div.find('table')
                if not inner_table:
                    print(f"Skipping div {div_index} in {url}: No table found")
                    continue
                content_td = inner_table.find('td', {'valign': 'top'})
                if not content_td:
                    print(f"Skipping div {div_index} in {url}: No content td found")
                    continue
                content_table = content_td.find('table')
                if not content_table:
                    print(f"Skipping div {div_index} in {url}: No content table found")
                    continue
                
                # Get all rows in the inner table
                rows = content_table.find_all('tr')
                if not rows:
                    print(f"Skipping div {div_index} in {url}: No rows found")
                    continue
                
                # Initialize data dictionary for this faculty member
                faculty_info = {
                    'name': '',
                    'qualifications': [],
                    'research_interests': '',
                    'email': '',
                    'profiles': [],
                    'department': url.split('/')[-1].replace('.cshtml', '')  # Extract department (e.g., fa-dche)
                }
                
                # Get all text content from the table
                all_text = content_table.get_text(separator='\n')
                text_lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                
                current_section = None
                found_faculty = False
                
                # Process each line
                for line in text_lines:
                    line = line.replace('\r', '').strip()
                    if not line:
                        continue
                    
                    # First non-empty line is usually the name
                    if not faculty_info['name'] and not line.startswith(('PhD', 'MS', 'MSc', 'BSc', 'Postdoc', 'Research Interests:', 'E-mail:', 'Academic')):
                        faculty_info['name'] = clean_name(line)
                        found_faculty = True
                        continue
                    
                    # Check for qualifications
                    if re.match(r'^(PhD|MS|MSc|BSc|Postdoc)\b', line, re.IGNORECASE):
                        faculty_info['qualifications'].append(line)
                        continue
                    
                    # Check for research interests
                    if line.startswith('Research Interests:'):
                        current_section = 'research'
                        research_text = line.replace('Research Interests:', '').strip()
                        if research_text:
                            faculty_info['research_interests'] = research_text
                        continue
                    
                    # Continue research interests if in section
                    if current_section == 'research' and not line.startswith(('E-mail:', 'Academic', 'http')):
                        if faculty_info['research_interests']:
                            faculty_info['research_interests'] += ' ' + line
                        else:
                            faculty_info['research_interests'] = line
                        continue
                    
                    # Check for email
                    if line.startswith('E-mail:'):
                        current_section = 'email'
                        email_text = line.replace('E-mail:', '').strip()
                        if email_text:
                            faculty_info['email'] = extract_email(email_text)
                        continue
                    
                    # Continue email if in email section
                    if current_section == 'email' and not faculty_info['email'] and not line.startswith(('Academic', 'http')):
                        faculty_info['email'] = extract_email(line)
                        continue
                    
                    # Check for academic profile section
                    if line.startswith('Academic and Research Profile:'):
                        current_section = 'profiles'
                        continue
                    
                    # URLs for profiles
                    if line.startswith(('http://', 'https://')):
                        faculty_info['profiles'].append(line)
                        continue
                
                # Also check for links in the HTML structure
                profile_links = content_table.find_all('a', href=True)
                for link in profile_links:
                    href = link.get('href', '').strip()
                    if href.startswith(('http://', 'https://')) and href not in faculty_info['profiles']:
                        faculty_info['profiles'].append(href)
                
                # Clean up research interests
                if faculty_info['research_interests']:
                    faculty_info['research_interests'] = re.sub(r'\s*\<.*?\>\s*.*$', '', faculty_info['research_interests']).strip()
                
                # Only append if we found a valid faculty member
                if found_faculty and faculty_info['name']:
                    # Check for duplicates by name
                    existing_index = next((i for i, f in enumerate(faculty_data) if f['name'] == faculty_info['name']), None)
                    if existing_index is not None:
                        # If duplicate found, keep the entry with email or from preferred department
                        existing = faculty_data[existing_index]
                        if not existing['email'] and faculty_info['email']:
                            faculty_data[existing_index] = faculty_info  # Replace with entry that has email
                        elif existing['email'] and faculty_info['email']:
                            # If both have emails, keep the one from earlier department (or merge if needed)
                            continue
                    else:
                        faculty_data.append(faculty_info)
            
            except Exception as e:
                print(f"Error processing div {div_index} in {url}: {e}")
                continue
    
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        continue

# Create pandas DataFrame
df = pd.DataFrame(faculty_data)

# Convert lists to strings for cleaner display
if not df.empty:
    df['qualifications'] = df['qualifications'].apply(lambda x: '; '.join(x) if x else '')
    df['profiles'] = df['profiles'].apply(lambda x: '; '.join(x) if x else '')
    
    # Reorder columns for clarity
    df = df[['name', 'qualifications', 'research_interests', 'email', 'profiles', 'department']]

# Display the DataFrame
print(df)

# Save to CSV for verification
df.to_csv('faculty_data_all_depts.csv', index=False)
