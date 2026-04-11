# ================================================================
# IMPORTS
# ================================================================

# pathlib - Modern path handling for checking if files exist
from pathlib import Path

# tkinter - For native file dialogs (comes with Python)
# filedialog lets your Python program pop up file browser windows
from tkinter import filedialog, Tk, simpledialog

# subprocess - A module from Python's Standard Library (no pip install needed)
# It allows Python to step OUTSIDE the interpreter and talk to the Operating System
# to spawn, control, and communicate with external system processes/programs.
# When called, Python hands off a task to a brand new independent program running
# alongside it, then waits for that program to finish, collects its output,
# before continuing execution.
import subprocess

# re - Standard Library module for Regular Expressions
# Used here to clean the URL into a valid filename
import re


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
# HARDCODED PATH TO CHROMIUM (STATIC - NO FILE DIALOG)
# ================================================================
# Chromium is installed system-wide on Kali Linux at this path
# Change this path if chromium is installed in a different location
html2pdf_tool_path = "/usr/bin/chromium"

# Verify the hardcoded path is valid
if not Path(html2pdf_tool_path).exists():
    print("❌ Error: Chromium not found at the expected file path!")
    print(f"   Expected file path is: {html2pdf_tool_path}")
    print("   Please install Chromium with: sudo apt install chromium")
    root.destroy()  # Closes the hidden tkinter window and frees memory
    exit()          # Stops the program immediately, nothing after this line runs.

print(f"✓ Chromium found at: {html2pdf_tool_path}\n")


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
    exit()          # Stops the program immediately, nothing after this line runs.

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
clean_url = re.sub(r'[\\/*?:"<>|./]', '_', clean_url)
# Limit filename length to 50 characters
default_filename = f"{clean_url[:50]}.pdf"

# Open save dialog to choose where to save the PDF
pdf_path = filedialog.asksaveasfilename(
    title="Save PDF As",                    # Text that appears in the popup window title bar
    defaultextension=".pdf",               # Automatically adds .pdf if user doesn't type an extension
    filetypes=[("PDF Files", "*.pdf")],    # Only show .pdf files in the dialog (saves as PDF)
    initialfile=default_filename           # Pre-fills the filename using the URL
)

# Check if user cancelled
if not pdf_path:
    print("❌ Save location not selected. Exiting.")
    root.destroy()  # Closes the hidden tkinter window and frees memory
    exit()          # Stops the program immediately, nothing after this line runs.

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
# CONVERT WEBPAGE TO PDF USING CHROMIUM HEADLESS
# ================================================================
# Chromium's --headless mode renders the full page (including JavaScript)
# and exports it directly to PDF — no display required.
#
# --headless         : Run Chromium with no visible window
# --no-sandbox       : Required on Kali/root environments
# --print-to-pdf     : Export the rendered page as a PDF to the given path
print(f"Converting webpage: {webpage_url}")
print("Processing...")

try:
    # subprocess.run() hands off the command to the OS and waits for it to finish
    result = subprocess.run(
        [
            html2pdf_tool_path,             # /usr/bin/chromium
            "--headless",                   # No visible browser window
            "--no-sandbox",                 # Required when running as root on Kali
            f"--print-to-pdf={pdf_path}",   # Output PDF path
            webpage_url                     # The webpage to convert
        ],
        capture_output=True,    # Capture stdout and stderr instead of printing them
        text=True               # Return stdout/stderr as strings instead of bytes
    )

    # Check if Chromium exited with an error (non-zero return code = failure)
    if result.returncode != 0:
        print(f"❌ Chromium exited with an error:")
        print(result.stderr)
    else:
        print("\n✅ Conversion completed successfully!")
        print(f"   Webpage URL : {webpage_url}")
        print(f"   Output PDF  : {pdf_path}")
        print("\n✓ PDF is ready to use!")

except PermissionError:
    print("❌ Error: Permission denied.")
    print("   You may not have permission to write to that folder.")
    print("   Try saving to your Desktop or Documents folder instead.")
except FileNotFoundError:
    print("❌ Error: Chromium not found.")
    print("   Install it with: sudo apt install chromium")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
finally:
    root.destroy()  # Closes the hidden tkinter window and frees memory
    print("\nDone.")