# ================================================================
# IMPORTS
# ================================================================

# pdfkit - Python wrapper for wkhtmltopdf that converts HTML to PDF
import pdfkit

# pathlib - Modern path handling for checking if files exist
from pathlib import Path

# tkinter - For native file dialogs (comes with Python)
# filedialog lets your Python program pop up file browser windows
from tkinter import filedialog, Tk


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


print("=== HTML to PDF Converter (Terminal + File Dialogs) ===\n")


# ================================================================
# HARDCODED PATH TO wkhtmltopdf.exe (STATIC - NO FILE DIALOG)
# ================================================================
# The 'r' creates a raw string - backslashes are treated as literal characters
# This path is hardcoded because wkhtmltopdf is installed once and doesn't change
# Change this path if your wkhtmltopdf is installed in a different location
html2pdf_tool_path = r"/usr/local/bin/wkhtmltopdf"

# Verify the hardcoded path is valid
if not Path(html2pdf_tool_path).exists():
    print("❌ Error: wkhtmltopdf not found at in the expected file path!")
    print(f"   Expected file path is: {html2pdf_tool_path}")
    print("   Please check that wkhtmltopdf is installed at this location.")
    print("   Or update the html2pdf_tool_path variable in the script.")
    root.destroy()  # Closes the hidden tkinter window and frees memory
    exit()  # Stops the program immediately, nothing after this line runs.

print(f"✓ wkhtmltopdf found at: {html2pdf_tool_path}\n")


# ================================================================
# LET USER SELECT HTML FILE USING FILE EXPLORER
# ================================================================

print("Opening file explorer to select HTML file...")

# Open file dialog to select the HTML file to convert
path_to_htmlfile = filedialog.askopenfilename(
    title="Select HTML File to Convert",  # Text that appears in the popup window title bar
    filetypes=[                           # Filters which files are visible in the dialog
        ("HTML Files", "*.html *.htm"),   # First option: show only .html and .htm files
        ("All Files", "*.*")              # Second option: show every file type
    ]
)  # Returns the selected file path as a string, or empty string if user clicks Cancel
# Check if user cancelled the dialog

if not path_to_htmlfile:
    print("❌ No HTML file selected. Exiting.")
    root.destroy()  # Closes the hidden tkinter window and frees memory
    exit()  # Stops the program immediately, nothing after this line runs.


# Instanstiate "path_to_htmlfile" as a file path object with the Path() class for 
# cleaner and safer file path handling.
path_to_htmlfile = Path(path_to_htmlfile)
print(f"   Selected HTML: {path_to_htmlfile}\n")


# ================================================================
# LET USER CHOOSE PDF SAVE LOCATION USING FILE EXPLORER
# ================================================================

print("Opening file explorer to choose PDF save location...")

# Open save dialog to choose where to save the PDF
pdf_path = filedialog.asksaveasfilename(
    title="Save PDF As",                      # Text that appears in the popup window title bar
    defaultextension=".pdf",                  # Automatically adds .pdf if user doesn't type an extension
    filetypes=[("PDF Files", "*.pdf")],       # Only show .pdf files in the dialog (saves as PDF)
    initialfile=f"{path_to_htmlfile.stem}.pdf"  # Pre-fills the filename using the HTML file's name
)  # Returns the selected save path as a string, or empty string if user clicks Cancel

# Check if user cancelled
if not pdf_path:
    print("❌ Save location not selected. Exiting.")
    root.destroy()  # Closes the hidden tkinter window and frees memory
    exit()  # Stops the program immediately, nothing after this line runs.


# Instanstiate "pdf_path" as a "file path object" with the Path() class for 
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
# CONVERT HTML TO PDF WITH ERROR HANDLING
# ================================================================
print(f"Converting: {path_to_htmlfile.name}")
print("Processing...")

try:
    # pdfkit.from_file() reads the HTML file and converts it to PDF
    pdfkit.from_file(
        str(path_to_htmlfile),      # HTML file to convert (convert Path to string)
        output_path=str(pdf_path),  # Output File PDF path (convert Path to string)
        configuration=config_pdfkit # Tells pdfkit where to find wkhtmltopdf
    )
    
    # If we reach here, conversion succeeded
    print("\n✅ Conversion completed successfully!")
    print(f"   Input HTML : {path_to_htmlfile}")
    print(f"   Output PDF  : {pdf_path}")

except PermissionError:
    print("❌ Error: Permission denied.")
    print("   You may not have permission to write to that folder.")
    print("   Try saving to your Desktop or Documents folder instead.")
except OSError as e:
    print(f"❌ Error: {e}")
    print("   This often means wkhtmltopdf failed to run.")
    print("   Make sure wkhtmltopdf is properly installed.")
except Exception as e:
    print(f"❌ Error during conversion: {e}")
    print("   Check that your HTML file is valid and not corrupted.")
else:
    print("\n✓ PDF is ready to use!")
finally:

    root.destroy()  # Closes the hidden tkinter window and frees memory
    print("\nDone.")