# WEBPAGE TO PDF CONVERTER

A Python script that converts any webpage URL to a PDF file using wkhtmltopdf + pdfkit. The user enters a URL via a popup dialog, and uses file explorer to choose the PDF save location.

---

## PREREQUISITES

### 1. Install wkhtmltopdf
- Download from: https://wkhtmltopdf.org/downloads.html
- Default Windows path: `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe`
- This is the engine that does the actual HTML/CSS rendering

### 2. Install pdfkit
```bash
pip install pdfkit
```
- This is the Python wrapper that calls wkhtmltopdf

### 3. Internet connection
- Required because the script fetches the live webpage from the URL

---

## WHAT THE SCRIPT DOES

| Step | Action |
|------|--------|
| 1 | Validates that wkhtmltopdf exists at the hardcoded path |
| 2 | Opens a popup dialog asking the user to enter or paste a URL |
| 3 | Opens a file explorer "Save As" dialog to choose where to save the PDF |
| 4 | Automatically generates a default filename from the URL |
| 5 | Calls wkhtmltopdf to fetch the webpage and convert it to PDF |
| 6 | Saves the PDF to the chosen location |
| 7 | Displays success message with the URL and PDF path |

---

## HARDCODED VALUES

| Value | Path |
|-------|------|
| wkhtmltopdf path | `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe` |

*Change this in the script if you installed wkhtmltopdf in a different location*

---

## USER INPUT METHODS

| What user provides | How | Method |
|--------------------|-----|--------|
| Webpage URL | Popup dialog | `simpledialog.askstring()` |
| PDF save location | File explorer | `filedialog.asksaveasfilename()` |

**No typing in terminal. Everything is done through popup windows.**

---

## FILENAME AUTO-GENERATION

When the "Save As" dialog opens, the script pre-fills a filename based on the URL.

**Example:**
```
URL: https://www.example.com/article/how-to-convert
Generated filename: example_com_article_how_to_convert.pdf
```

**Rules applied:**
- Removes `https://` or `http://`
- Removes `www.`
- Replaces slashes (`/`), dots (`.`), colons (`:`), and other invalid characters with underscores
- Limits filename to 50 characters

*User can change the filename before saving.*

---

## ERROR HANDLING

| Error Scenario | What Happens |
|----------------|---------------|
| wkhtmltopdf not found | Script shows error with the expected path and exits |
| User clicks Cancel on URL dialog | Script shows "No URL entered" and exits |
| User clicks Cancel on Save dialog | Script shows "Save location not selected" and exits |
| Invalid URL (typo, dead link) | Script shows OSError with guidance |
| No internet connection | Script shows error during conversion |
| Permission denied when saving | Script suggests saving to Desktop/Documents instead |
| wkhtmltopdf fails to run | Script shows error and suggests checking installation |

---

## COMPARISON: HTML FILE vs WEBPAGE URL

| Feature | HTML File Converter | Webpage URL Converter |
|---------|---------------------|----------------------|
| Input method | File explorer | Text popup dialog |
| Source | Local HTML file | Live webpage from internet |
| pdfkit method | `.from_file()` | `.from_url()` |
| Filename source | HTML file name | Auto-generated from URL |
| Internet required | No | Yes |
| Can convert local files | Yes | No |
| Can convert any public webpage | No | Yes |

---

## EXAMPLE USAGE

**Scenario:** User wants to save a Wikipedia article as a PDF

```
1. User runs: python webpage2pdf.py

2. Terminal shows:
   === Webpage to PDF Converter (Terminal + File Dialogs) ===
   ✓ wkhtmltopdf found at: C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe
   Please enter the webpage URL you want to convert to PDF...

3. Popup dialog appears with title "Enter Webpage URL"
   User types: https://en.wikipedia.org/wiki/Python_(programming_language)
   Clicks OK

4. Terminal shows:
   Webpage URL: https://en.wikipedia.org/wiki/Python_(programming_language)

5. Save As dialog opens with default filename:
   en_wikipedia_org_wiki_Python_(programming_language).pdf
   User chooses Desktop, renames to "python_wiki.pdf", clicks Save

6. Terminal shows:
   Converting webpage: https://en.wikipedia.org/wiki/Python_(programming_language)
   Processing...

7. Terminal shows:
   ✅ Conversion completed successfully!
      Webpage URL : https://en.wikipedia.org/wiki/Python_(programming_language)
      Output PDF   : C:\Users\John\Desktop\python_wiki.pdf
   ✓ PDF is ready to use!
   Done.
```

---

## COMMON USE CASES

1. Save online articles for offline reading
2. Archive webpages as PDF documents
3. Convert documentation pages to PDF
4. Save receipts or invoices from websites
5. Create PDF copies of online forms
6. Backup important web content

---

## LIMITATIONS

1. Some websites may block wkhtmltopdf (they see it as a bot)
2. JavaScript-heavy pages may not render correctly
3. Login-required pages cannot be accessed (no session/cookie support)
4. Very large pages may take a long time to convert
5. Dynamic content loaded after page load may be missing
6. Some CSS features (flexbox, grid, modern CSS) may have rendering issues

---

## TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| "wkhtmltopdf not found" | Verify wkhtmltopdf is installed at the hardcoded path, or update the path in the script |
| PDF is blank or missing content | Some websites require JavaScript. Try a different webpage. Check if the webpage blocks automated tools. |
| Conversion takes very long | The webpage might be very large. Try a different URL. Check your internet speed. |
| Special characters in filename cause issues | Script auto-replaces invalid characters. User can also manually rename in Save As dialog. |

---

## NOTES

- The wkhtmltopdf path is hardcoded (user is never asked for it)
- The script uses Qt WebKit rendering engine (same as older Safari browsers)
- Modern CSS (Grid, Flexbox) may have rendering limitations
- The script works on Windows, Mac, and Linux (with adjusted paths)
- No terminal typing required - all input via popup dialogs

---

## FILES

| Item | Name |
|------|------|
| Script name | `webpage2pdf.py` |
| Output | PDF file at user-specified location |
| Temporary files | None created |

---