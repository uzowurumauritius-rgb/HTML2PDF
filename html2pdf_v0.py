# IMPORT PDFKIT - A PYTHON WRAPPER FOR WKHTMLTOPDF THAT CONVERTS HTML TO PDF
import pdfkit


# =============================
# POINT TO THE ACTUAL EXE FILE (not the folder)
# =============================
html2pdf_tool_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"



# =============================
# HTML FILE PATH
# =============================
path_to_htmlfile = r"sample.html"



# =============================
# CONFIGURE PDFKIT WITH THE EXE PATH
# =============================
# Creates a Configuration object that tells pdfkit where wkhtmltopdf is installed
# This is required when wkhtmltopdf is not in your system PATH

config_pdfkit = pdfkit.configuration(
    wkhtmltopdf=html2pdf_tool_path  # The wkhtmltopdf parameter receives the file path to the executable
)



# =============================
# CONVERT HTML TO PDF
# =============================
pdfkit.from_file(                     # pdfkit.from_file() reads the HTML file and converts it to PDF
    path_to_htmlfile,                 # First argument: path to the source HTML file
    output_path='sample.pdf',         # output_path: name/location of the PDF file to create
    configuration=config_pdfkit       # configuration: passes the config object so pdfkit knows where wkhtmltopdf lives
)


print("✅ Conversion completed successfully!")