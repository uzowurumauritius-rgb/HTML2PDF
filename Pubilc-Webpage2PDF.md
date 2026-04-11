# WEBPAGE TO PDF CONVERTER

A Python script that converts any webpage URL to a PDF file using Chromium's
built-in headless mode. The user enters a URL via a popup dialog, and uses a
file explorer window to choose the PDF save location. No terminal typing required.

---

## PREREQUISITES

### 1. Install Chromium
Chromium is pre-installed on Kali Linux. Verify it is available by running:
```bash
chromium --version
```
If it is missing, install it with:
```bash
sudo apt install chromium
```
The script expects Chromium at `/usr/bin/chromium`. If yours is elsewhere, update
the `html2pdf_tool_path` variable at the top of the script.

### 2. No pip installs needed
This script uses only Python Standard Library modules — `pathlib`, `tkinter`,
`subprocess`, and `re` — all of which ship with Python. No `pip install` required.

### 3. Internet connection
Required because the script fetches the live webpage from the provided URL.

---

## HOW IT WORKS

| Step | Action |
|------|--------|
| 1 | Validates that Chromium exists at the hardcoded path |
| 2 | Opens a popup dialog asking the user to enter or paste a URL |
| 3 | Opens a file explorer "Save As" dialog to choose where to save the PDF |
| 4 | Automatically generates a default filename from the URL |
| 5 | Launches Chromium in headless mode to fetch and render the webpage |
| 6 | Chromium exports the rendered page directly to a PDF file |
| 7 | Displays a success message with the URL and output PDF path |

---

## HARDCODED VALUES

| Value | Path |
|-------|------|
| Chromium binary path | `/usr/bin/chromium` |

Update `html2pdf_tool_path` in the script if Chromium is installed elsewhere on your system.

---

## USER INPUT METHODS

| What the user provides | How | Method |
|------------------------|-----|--------|
| Webpage URL | Popup dialog | `simpledialog.askstring()` |
| PDF save location | File explorer | `filedialog.asksaveasfilename()` |

No terminal typing required. All input is collected through popup windows.

---

## FILENAME AUTO-GENERATION

When the Save As dialog opens, the script pre-fills a filename derived from the URL.

**Example:**
```
URL:               https://www.example.com/article/how-to-convert
Generated filename: example_com_article_how_to_convert.pdf
```

**Rules applied:**
- Removes `https://` or `http://`
- Removes `www.`
- Replaces slashes, dots, colons, and other invalid characters with underscores
- Limits the filename to 50 characters

The user can change the filename before clicking Save.

---

## ERROR HANDLING

| Error Scenario | What Happens |
|----------------|--------------|
| Chromium not found at path | Script shows error with the expected path and exits |
| User cancels the URL dialog | Script shows "No URL entered" and exits |
| User cancels the Save dialog | Script shows "Save location not selected" and exits |
| Chromium exits with a non-zero code | Script prints Chromium's stderr output for diagnosis |
| Permission denied when saving | Script suggests saving to Desktop or Documents instead |
| Chromium binary not found at runtime | Script shows a FileNotFoundError with install instructions |

---

## EXAMPLE USAGE

**Scenario:** User wants to save a Wikipedia article as a PDF

```
1. User runs:
   python webpage2pdf.py

2. Terminal shows:
   === Webpage to PDF Converter (Terminal + File Dialogs) ===
   ✓ Chromium found at: /usr/bin/chromium
   Please enter the webpage URL you want to convert to PDF...

3. Popup dialog appears — user types:
   https://en.wikipedia.org/wiki/Python_(programming_language)
   Clicks OK

4. Terminal shows:
      Webpage URL: https://en.wikipedia.org/wiki/Python_(programming_language)

5. Save As dialog opens with default filename:
   en_wikipedia_org_wiki_Python__programming_language_.pdf
   User chooses Desktop, renames to "python_wiki.pdf", clicks Save

6. Terminal shows:
   Converting webpage: https://en.wikipedia.org/wiki/Python_(programming_language)
   Processing...

7. Terminal shows:
   ✅ Conversion completed successfully!
      Webpage URL : https://en.wikipedia.org/wiki/Python_(programming_language)
      Output PDF  : /home/wurucyber/Desktop/python_wiki.pdf
   ✓ PDF is ready to use!
   Done.
```

---

## WHY CHROMIUM HEADLESS INSTEAD OF WKHTMLTOPDF

| Feature | wkhtmltopdf | Chromium Headless |
|---------|-------------|-------------------|
| JavaScript support | Limited | Full |
| Modern CSS (Grid, Flexbox) | Poor | Excellent |
| Actively maintained | ❌ Abandoned since 2020 | ✅ Yes |
| Requires virtual display on Linux | Sometimes (segfault) | No |
| Extra install needed | Yes (`wkhtmltopdf`) | No (pre-installed on Kali) |
| Runs via Python wrapper | `pdfkit` | `subprocess` (Standard Library) |

---

## COMMON USE CASES

- Save online articles for offline reading
- Archive webpages as PDF documents
- Convert documentation pages to PDF
- Save receipts or invoices from websites
- Create PDF copies of online forms or reports
- Back up important web content before it changes

---

## LIMITATIONS

- Some websites may block automated tools and return an error page instead
- Login-required pages cannot be accessed (no session or cookie support)
- Very large pages may take longer to convert
- Dynamic content that loads only after user interaction may not appear
- Pages that detect and block headless browsers may render incorrectly

---

## TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| "Chromium not found" | Run `which chromium` to find its actual path, then update `html2pdf_tool_path` in the script |
| PDF is blank or shows a login page | The target page requires authentication — use `intranet2pdf.py` instead |
| PDF is missing dynamic content | The page uses JavaScript that loads after the initial render. Try a static page instead |
| Chromium exits with a non-zero error code | Check the stderr output printed in the terminal for the specific Chromium error |
| Permission denied when saving | Save to `/home/yourusername/Desktop` or `/home/yourusername/Documents` instead |

---

## FILES

| Item | Name |
|------|------|
| Script | `webpage2pdf.py` |
| Output | PDF file at user-specified location |
| Temporary files | None created |

---

## RELATED SCRIPTS

| Script | Purpose |
|--------|---------|
| `html2pdf_v0.py` | Convert a local HTML file to PDF (simple, no dialogs) |
| `html2pdf_v1.py` | Convert a local HTML file to PDF (with file dialog support) |
| `webpage2pdf.py` | Convert any public webpage URL to PDF (this script) |
| `intranet2pdf.py` | Convert a login-protected intranet page to PDF using Selenium |