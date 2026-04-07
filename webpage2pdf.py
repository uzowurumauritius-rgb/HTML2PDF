# ================================================================
# IMPORTS
# ================================================================

# pdfkit - Python wrapper for wkhtmltopdf that converts HTML to PDF
import pdfkit

# pathlib - Modern path handling for checking if files exist
from pathlib import Path

# tkinter - For native file dialogs (comes with Python)
# filedialog lets your Python program pop up file browser windows
from tkinter import filedialog, Tk, simpledialog


# ================================================================
# HIDE THE MAIN TKINTER WINDOW
# ================================================================

# Create an instance of the Tk class (this is the main window)
# Tkinter always creates this when it starts, even if we don't want it
root = Tk()

# Call the withdraw() method to hide the main window from view
# The window still exists in memory but is invisible to the user
root.withdraw()

# Call the attributes() method with '-topmost' to set window behavior
# Setting '-topmost' to True forces the dialog windows to appear
# on top of all other applications so the user doesn't lose them
root.attributes('-topmost', True)


print("=== Webpage to PDF Converter (Terminal + File Dialogs) ===\n")


# ================================================================
# HARDCODED PATH TO wkhtmltopdf.exe (STATIC - NO FILE DIALOG)
# ================================================================
# The 'r' creates a raw string - backslashes are treated as literal characters
# This path is hardcoded because wkhtmltopdf is installed once and doesn't change
# Change this path if your wkhtmltopdf is installed in a different location
html2pdf_tool_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

# Verify the hardcoded path is valid
if not Path(html2pdf_tool_path).exists():
    print("❌ Error: wkhtmltopdf not found at the expected file path!")
    print(f"   Expected file path is: {html2pdf_tool_path}")
    print("   Please check that wkhtmltopdf is installed at this location.")
    print("   Or update the html2pdf_tool_path variable in the script.")
    root.destroy()  # Closes the hidden tkinter window and frees memory
    exit()  # Stops the program immediately, nothing after this line runs.

print(f"✓ wkhtmltopdf found at: {html2pdf_tool_path}\n")


# ================================================================
# LET USER ENTER WEBPAGE URL
# ================================================================

print("Please enter the webpage URL you want to convert to PDF...")

# Open a simple input dialog for the user to type or paste the URL
webpage_url = simpledialog.askstring(
    title="Enter Webpage URL",
    prompt="Enter the full URL (e.g., https://example.com):"
)

# Check if user cancelled the dialog
if not webpage_url:
    print("❌ No URL entered. Exiting.")
    root.destroy()  # Closes the hidden tkinter window and frees memory
    exit()  # Stops the program immediately, nothing after this line runs.

# Strip any leading/trailing whitespace from the URL
webpage_url = webpage_url.strip()

print(f"   Webpage URL: {webpage_url}\n")


# ================================================================
# LET USER CHOOSE PDF SAVE LOCATION USING FILE EXPLORER
# ================================================================

print("Opening file explorer to choose PDF save location...")

# Extract a valid filename from the URL (remove https://, www., slashes, etc.)
# First, remove protocol (https:// or http://)
clean_url = webpage_url.replace("https://", "").replace("http://", "")
# Remove www. if present
clean_url = clean_url.replace("www.", "")
# Replace slashes and dots with underscores for a valid filename
import re
clean_url = re.sub(r'[\\/*?:"<>|./]', '_', clean_url)
# Limit filename length to 50 characters
default_filename = f"{clean_url[:50]}.pdf"

# Open save dialog to choose where to save the PDF
pdf_path = filedialog.asksaveasfilename(
    title="Save PDF As",                      # Text that appears in the popup window title bar
    defaultextension=".pdf",                  # Automatically adds .pdf if user doesn't type an extension
    filetypes=[("PDF Files", "*.pdf")],       # Only show .pdf files in the dialog (saves as PDF)
    initialfile=default_filename             # Pre-fills the filename using the URL
)

# Check if user cancelled
if not pdf_path:
    print("❌ Save location not selected. Exiting.")
    root.destroy()  # Closes the hidden tkinter window and frees memory
    exit()  # Stops the program immediately, nothing after this line runs.

# Instantiate "pdf_path" as a "file path object" with the Path() class for 
# cleaner and safer file path handling.
pdf_path = Path(pdf_path)

# ===================================
# CONVERSION EXTENSION SAFETY MEASURE
# ===================================
# Ensure .pdf extension (asksaveasfilename usually adds it, but just in case)
if pdf_path.suffix.lower() != '.pdf':
    pdf_path = pdf_path.with_suffix('.pdf')

print(f"   PDF will be saved as: {pdf_path}\n")


# ================================================================
# CONFIGURE PDFKIT WITH THE EXE PATH
# ================================================================
# Creates a Configuration object that tells pdfkit where wkhtmltopdf is installed
# This is required when wkhtmltopdf is not in your system PATH
print("Configuring pdfkit...")
config_pdfkit = pdfkit.configuration(
    wkhtmltopdf=html2pdf_tool_path  # Using the hardcoded path
)
print("   Configuration complete.\n")


# ================================================================
# CONVERT WEBPAGE TO PDF WITH ERROR HANDLING
# ================================================================
print(f"Converting webpage: {webpage_url}")
print("Processing...")

try:
    # pdfkit.from_url() reads the webpage URL and converts it to PDF
    # First argument: the URL of the webpage to convert
    # output_path: location of the PDF file to create
    # configuration: passes the config object so pdfkit knows where wkhtmltopdf lives
    pdfkit.from_url(
        webpage_url,                # Webpage URL to convert (string)
        output_path=str(pdf_path),  # Output PDF path (convert Path to string)
        configuration=config_pdfkit # Tells pdfkit where to find wkhtmltopdf
    )
    
    # If we reach here, conversion succeeded
    print("\n✅ Conversion completed successfully!")
    print(f"   Webpage URL : {webpage_url}")
    print(f"   Output PDF   : {pdf_path}")

except PermissionError:
    print("❌ Error: Permission denied.")
    print("   You may not have permission to write to that folder.")
    print("   Try saving to your Desktop or Documents folder instead.")
except OSError as e:
    print(f"❌ Error: {e}")
    print("   This often means wkhtmltopdf failed to run or the URL is invalid.")
    print("   Make sure wkhtmltopdf is properly installed.")
    print("   Also check that the URL is correct and accessible.")
except Exception as e:
    print(f"❌ Error during conversion: {e}")
    print("   Check that the URL is valid and you have an internet connection.")
else:
    print("\n✓ PDF is ready to use!")
finally:
    root.destroy()  # Closes the hidden tkinter window and frees memory
    print("\nDone.")