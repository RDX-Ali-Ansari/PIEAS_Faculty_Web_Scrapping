# PIEAS Faculty Web Scraper

This project is a **Python-based web scraper** designed to collect and organize faculty information from various departments at **PIEAS (Pakistan Institute of Engineering and Applied Sciences)**. The script retrieves details such as names, qualifications, research interests, emails, academic profiles, and departmental affiliation.

---

## 📌 Objective

To automate the extraction of structured faculty data from PIEAS’s departmental faculty pages and store the cleaned information into a CSV file for future use, such as research collaboration, internal reference, or analysis.

---

## 🧩 Features

- Scrapes faculty data from multiple department URLs.
- Cleans and standardizes:
  - Names (removing titles and roles)
  - Qualifications
  - Research interests
  - Email addresses (with domain completion if missing)
  - External profile links (Google Scholar, ResearchGate, etc.)
- Removes duplicate entries across departments.
- Outputs a clean, structured DataFrame and saves it to CSV.

---

## 🛠️ Technologies Used

- **Python**: Programming language.
- **Requests**: To fetch HTML pages.
- **BeautifulSoup (bs4)**: For parsing and extracting HTML content.
- **Pandas**: For data storage and CSV export.
- **Regular Expressions (re)**: To clean and extract relevant information from raw HTML/text.

---

## 🌐 Target URLs

The following PIEAS departmental faculty pages were scraped:

- Department of Chemical Engineering (DCHE)
- Department of Computer and Information Sciences (DCIS)
- Department of Communication and Management Sciences (DCMS)
- Department of Electrical Engineering (DEE)
- Department of Mechanical Engineering (DME)
- Department of Medical Sciences (DMS)
- Department of Metallurgy and Materials Engineering (DMME)
- Department of Nuclear Engineering (DNE)
- Department of Physics and Applied Mathematics (DPAM)

---

## 📋 Data Fields Extracted

| Field               | Description                                           |
|--------------------|-------------------------------------------------------|
| `name`             | Cleaned name of the faculty member                    |
| `qualifications`   | List of degrees (e.g., PhD, MSc)                      |
| `research_interests` | Research interests (flattened multi-line text)      |
| `email`            | Verified or constructed email address                 |
| `profiles`         | List of external academic profile URLs                |
| `department`       | Derived from the source URL (e.g., `fa-dcis`)         |

---

## 🧹 Data Cleaning Highlights

- **Name Cleanup**:
  - Removes designations like "Professor", "Head", "Coordinator".
  - Strips parenthetical and redundant content.
- **Email Extraction**:
  - Parses embedded or partial email addresses.
  - Adds `@pieas.edu.pk` if only username is present.
- **Profile URLs**:
  - Extracts all links starting with `http` from the faculty card.
  - Removes duplicates.

---

## 💾 Output

The final cleaned data is stored in:
