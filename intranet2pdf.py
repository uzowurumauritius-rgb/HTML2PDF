# ================================================================
# IMPORTS
# ================================================================

# pathlib - Modern path handling for checking if files exist
from pathlib import Path

# tkinter - For native file dialogs (comes with Python)
from tkinter import Tk, filedialog, simpledialog

# re - Standard Library module for Regular Expressions
# Used here to clean the URL into a valid filename
import re

# sys - Provides access to system-level operations like exiting the program cleanly
import sys

# base64 - Standard Library module for decoding binary data
# Used here to decode the raw PDF bytes that Chrome returns
import base64

# time - Standard Library module for pausing execution
# Used to give pages time to fully render before converting
import time

# selenium - Third party browser automation library
# Controls a real Chromium browser — handles navigation, form filling,
# clicks, and communicating with the browser's internal DevTools API
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)


# ================================================================
# CONSTANTS — INTRANET SPECIFIC SETTINGS
# ================================================================

# Keywords that identify a login/auth page in the URL
LOGIN_URL_KEYWORDS = ["sign_in", "login", "auth"]

# Path to the Chromium browser binary on Kali Linux
CHROMIUM_PATH = "/usr/bin/chromium"

# How long (in seconds) to wait for elements and page loads
WAIT_TIMEOUT = 20

# ================================================================
# ⚠️  SELECTORS — YOU NEED TO INSPECT THESE YOURSELF
# ================================================================
# HOW TO FIND THE CORRECT SELECTORS:
#
#   1. Open https://intranet.aluswe.com/auth/sign_in in your browser
#   2. Right-click on the Email input field → click "Inspect"
#   3. Look at the HTML element that gets highlighted, for example:
#
#      <input type="email" name="user[email]" id="user_email" ...>
#
#   From that element you can build a selector using ANY of these:
#
#   By.ID          → use the  id="..."         attribute → "user_email"
#   By.NAME        → use the  name="..."       attribute → "user[email]"
#   By.CSS_SELECTOR→ use the  type="..."       attribute → "input[type='email']"
#   By.XPATH       → full path in the DOM tree → "//input[@id='user_email']"
#
#   RECOMMENDED: By.ID is the most reliable if the element has one.
#   FALLBACK:    By.CSS_SELECTOR with type attribute usually works universally.
#
#   Repeat the same inspection for:
#   - The Password input field
#   - The Login/Submit button
#
# ----------------------------------------------------------------
# FILL IN YOUR INSPECTED VALUES BELOW:
# ----------------------------------------------------------------

# Inspect the EMAIL input field and fill in what you find:
# e.g. if you see id="user_email"  → set to: (By.ID, "user_email")
# e.g. if you see name="email"     → set to: (By.NAME, "email")
SELECTOR_EMAIL = (By.CSS_SELECTOR, "input[type='email']")   # ← REPLACE IF NEEDED

# Inspect the PASSWORD input field and fill in what you find:
# e.g. if you see id="user_password" → set to: (By.ID, "user_password")
SELECTOR_PASSWORD = (By.CSS_SELECTOR, "input[type='password']")  # ← REPLACE IF NEEDED

# Inspect the LOGIN BUTTON and fill in what you find:
# e.g. if you see id="submit"              → set to: (By.ID, "submit")
# e.g. if you see type="submit"            → set to: (By.CSS_SELECTOR, "input[type='submit']")
# e.g. if the button says "Log in"         → set to: (By.XPATH, "//button[text()='Log in']")
SELECTOR_SUBMIT = (By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")  # ← REPLACE IF NEEDED

# ================================================================
# ⚠️  LOGIN SUCCESS DETECTION — INSPECT THIS TOO
# ================================================================
# After clicking login, how do we know it WORKED vs FAILED?
#
# Option A — Check the URL changed away from the login page
#             (this is the default — already handled by is_login_page())
#
# Option B — Look for an error message element that appears on bad credentials
#   Right-click the red error message → Inspect → note its id, class, or tag
#   e.g. <div class="alert alert-danger">Invalid email or password</div>
#   Then set: ERROR_SELECTOR = (By.CSS_SELECTOR, ".alert.alert-danger")
#
# FILL IN IF YOU FIND AN ERROR MESSAGE ELEMENT:
ERROR_SELECTOR = None   # ← SET TO e.g. (By.CSS_SELECTOR, ".alert") IF YOU FIND ONE


# ================================================================
# HIDE THE MAIN TKINTER WINDOW
# ================================================================

root = Tk()
root.withdraw()
root.attributes('-topmost', True)


# ================================================================
# HELPER — CLEAN EXIT
# ================================================================

def clean_exit(message=None):
    """Print an optional message, destroy tkinter, and exit cleanly."""
    if message:
        print(message)
    try:
        root.destroy()
    except Exception:
        pass
    sys.exit()


# ================================================================
# HELPER — SET UP SELENIUM CHROMIUM DRIVER
# ================================================================

def create_driver():
    """
    Configures and returns a Selenium Chrome WebDriver instance.
    Uses Selenium Manager (built into Selenium 4.6+) to automatically
    download the correct chromedriver — no manual install needed.
    """
    chrome_options = Options()

    # ---- Headless & Sandbox ----
    chrome_options.add_argument("--headless=new")        # No visible browser window
    chrome_options.add_argument("--no-sandbox")          # Required on Kali / root
    chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent shared memory issues

    # ---- Display & Rendering ----
    chrome_options.add_argument("--disable-gpu")             # Disable GPU in headless mode
    chrome_options.add_argument("--window-size=1920,1080")   # Standard screen resolution

    # ---- Point Selenium to System Chromium ----
    # Without this, Selenium looks for Google Chrome, not Chromium
    chrome_options.binary_location = CHROMIUM_PATH

    # Selenium Manager will auto-download the matching chromedriver
    # for Chromium 142 on first run — no sudo or manual install needed
    driver = webdriver.Chrome(options=chrome_options)

    return driver


# ================================================================
# HELPER — DETECT IF PAGE IS A LOGIN PAGE
# ================================================================

def is_login_page(driver):
    """
    Returns True if the current page looks like a login/sign-in page.
    Checks both the current URL and the presence of a password input field.
    """
    url_is_login = any(keyword in driver.current_url for keyword in LOGIN_URL_KEYWORDS)

    try:
        has_password = len(driver.find_elements(By.CSS_SELECTOR, "input[type='password']")) > 0
    except Exception:
        has_password = False

    return url_is_login or has_password


# ================================================================
# HELPER — COLLECT CREDENTIALS VIA DIALOG
# ================================================================

def collect_credentials():
    """
    Opens two Tkinter dialogs to collect the user's email and password.
    Returns (email, password) as strings, or calls clean_exit() if cancelled.
    """
    print("🔐 Login required — opening credential dialogs...")

    email = simpledialog.askstring(
        title="Intranet Login — Email",
        prompt="Enter your ALU Intranet email address:"
    )
    if not email:
        clean_exit("❌ No email entered. Exiting.")

    password = simpledialog.askstring(
        title="Intranet Login — Password",
        prompt="Enter your ALU Intranet password:",
        show="*"    # Masks the password characters with asterisks
    )
    if not password:
        clean_exit("❌ No password entered. Exiting.")

    return email.strip(), password.strip()


# ================================================================
# HELPER — PERFORM LOGIN
# ================================================================

def perform_login(driver, email, password):
    """
    Locates the login form fields, fills them in, and submits the form.
    Waits for the page to navigate away from the login page.
    Raises ValueError if login fails (still on login page after submit).

    ⚠️  BEFORE THIS WORKS:
        Go to https://intranet.aluswe.com/auth/sign_in in your browser
        Open DevTools (F12) → Inspector tab
        Verify that SELECTOR_EMAIL, SELECTOR_PASSWORD, SELECTOR_SUBMIT
        at the top of this file match what you see in the actual HTML.
    """
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    print("   Waiting for login form to load...")

    # ----------------------------------------------------------------
    # LOCATE EMAIL FIELD
    # ⚠️  If this fails: inspect the email input on the login page
    #     and update SELECTOR_EMAIL at the top of this file
    # ----------------------------------------------------------------
    email_field = wait.until(EC.visibility_of_element_located(SELECTOR_EMAIL))

    # ----------------------------------------------------------------
    # LOCATE PASSWORD FIELD
    # ⚠️  If this fails: inspect the password input on the login page
    #     and update SELECTOR_PASSWORD at the top of this file
    # ----------------------------------------------------------------
    password_field = driver.find_element(*SELECTOR_PASSWORD)

    # ----------------------------------------------------------------
    # LOCATE SUBMIT BUTTON
    # ⚠️  If this fails: inspect the login button on the login page
    #     Right-click the "Log in" button → Inspect
    #     Look for: type="submit", id="...", class="...", text content
    #     Update SELECTOR_SUBMIT at the top of this file
    # ----------------------------------------------------------------
    submit_button = driver.find_element(*SELECTOR_SUBMIT)

    print("   Filling in login form...")

    # Clear any pre-filled content and type credentials
    email_field.clear()
    email_field.send_keys(email)

    password_field.clear()
    password_field.send_keys(password)

    print("   Submitting login form...")
    submit_button.click()

    # ----------------------------------------------------------------
    # WAIT FOR LOGIN RESULT
    # ⚠️  If login detection is unreliable:
    #     Inspect what changes on the page after a failed login
    #     e.g. an error <div> that appears — set ERROR_SELECTOR above
    # ----------------------------------------------------------------
    time.sleep(3)   # Give the page time to respond after clicking submit

    # Check for a visible error message if we defined one
    if ERROR_SELECTOR:
        try:
            error_el = driver.find_element(*ERROR_SELECTOR)
            if error_el.is_displayed():
                raise ValueError(
                    f"Login failed — error message detected on page:\n"
                    f"   '{error_el.text}'"
                )
        except NoSuchElementException:
            pass    # No error message found — good sign

    # Final check — are we still on the login page?
    if is_login_page(driver):
        raise ValueError(
            "Login failed — still on the login page after submission.\n"
            "   Check your email and password and try again."
        )

    print("✓ Login successful!\n")


# ================================================================
# HELPER — EXPORT CURRENT PAGE TO PDF
# ================================================================

def export_to_pdf(driver, pdf_path):
    """
    Uses Chrome's DevTools Protocol (CDP) via Selenium to print
    the currently loaded page to a PDF file.

    CDP is Chrome's internal API — it gives us access to low-level
    browser features like PDF generation that are not part of
    standard Selenium commands.
    """
    result = driver.execute_cdp_cmd("Page.printToPDF", {
        "paperWidth":          8.27,    # A4 width in inches
        "paperHeight":        11.69,    # A4 height in inches
        "marginTop":           0.4,
        "marginBottom":        0.4,
        "marginLeft":          0.4,
        "marginRight":         0.4,
        "printBackground":     True,    # Include background colors and images
        "displayHeaderFooter": False    # No header/footer chrome
    })

    # Chrome returns the PDF as a Base64-encoded string
    # Decode it back to raw bytes and write to disk
    pdf_bytes = base64.b64decode(result["data"])
    Path(pdf_path).write_bytes(pdf_bytes)


# ================================================================
# MAIN PROGRAM
# ================================================================

print("=== ALU Intranet Page to PDF Converter ===\n")


# ----------------------------------------------------------------
# STEP 1 — GET TARGET URL FROM USER
# ----------------------------------------------------------------

print("Please enter the intranet URL you want to convert to PDF...")

webpage_url = simpledialog.askstring(
    title="Enter Intranet URL",
    prompt="Enter the full URL (e.g., https://intranet.aluswe.com/projects/2188):"
)

if not webpage_url:
    clean_exit("❌ No URL entered. Exiting.")

webpage_url = webpage_url.strip()
print(f"   Target URL: {webpage_url}\n")


# ----------------------------------------------------------------
# STEP 2 — GET PDF SAVE LOCATION FROM USER
# ----------------------------------------------------------------

print("Opening file explorer to choose PDF save location...")

clean_url        = webpage_url.replace("https://", "").replace("http://", "")
clean_url        = clean_url.replace("www.", "")
clean_url        = re.sub(r'[\\/*?:"<>|./]', '_', clean_url)
default_filename = f"{clean_url[:50]}.pdf"

pdf_path = filedialog.asksaveasfilename(
    title="Save PDF As",
    defaultextension=".pdf",
    filetypes=[("PDF Files", "*.pdf")],
    initialfile=default_filename
)

if not pdf_path:
    clean_exit("❌ Save location not selected. Exiting.")

pdf_path = Path(pdf_path)

if pdf_path.suffix.lower() != '.pdf':
    pdf_path = pdf_path.with_suffix('.pdf')

print(f"   PDF will be saved as: {pdf_path}\n")


# ----------------------------------------------------------------
# STEP 3 — LAUNCH BROWSER, HANDLE LOGIN, CONVERT TO PDF
# ----------------------------------------------------------------

print("Launching Chromium browser (headless)...")
print("   Selenium Manager will auto-download chromedriver if needed...\n")

driver = None

try:
    driver = create_driver()

    # ----------------------------
    # NAVIGATE TO TARGET URL
    # ----------------------------
    print(f"   Navigating to: {webpage_url}")
    driver.get(webpage_url)
    time.sleep(3)   # Wait for redirect to settle

    # ----------------------------
    # DETECT LOGIN REDIRECT
    # ----------------------------
    if is_login_page(driver):
        print(f"   ⚠️  Redirected to login page: {driver.current_url}")

        email, password = collect_credentials()

        # Attempt login — retry once if credentials are wrong
        attempts = 0
        while attempts < 2:
            try:
                perform_login(driver, email, password)
                break
            except ValueError as login_error:
                attempts += 1
                if attempts >= 2:
                    clean_exit(f"❌ {login_error}")
                print(f"   ⚠️  Attempt {attempts} failed. Please re-enter credentials.")
                email, password = collect_credentials()

        # Navigate back to original target if login redirected us elsewhere
        if driver.current_url != webpage_url:
            print(f"   Navigating to original target: {webpage_url}")
            driver.get(webpage_url)
            time.sleep(3)

    # ----------------------------
    # VERIFY WE REACHED TARGET PAGE
    # ----------------------------
    if is_login_page(driver):
        clean_exit("❌ Could not access the target page after login. Exiting.")

    print(f"✓ Page loaded: {driver.current_url}")

    # ----------------------------
    # WAIT FOR FULL PAGE RENDER
    # ⚠️  If the page uses heavy JavaScript and content loads slowly:
    #     Open DevTools on the target page → Network tab → reload
    #     Look for the last request that finishes loading
    #     You may need to increase time.sleep() below from 2 to 5+
    # ----------------------------
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    time.sleep(2)

    # ----------------------------
    # EXPORT PAGE TO PDF
    # ----------------------------
    print(f"\nConverting page to PDF...")
    print("Processing...")

    export_to_pdf(driver, pdf_path)

    print("\n✅ Conversion completed successfully!")
    print(f"   Target URL  : {webpage_url}")
    print(f"   Output PDF  : {pdf_path}")
    print("\n✓ PDF is ready to use!")

except TimeoutException:
    print("❌ Error: Page took too long to load.")
    print("   Check your internet connection or try again later.")
except WebDriverException as e:
    print(f"❌ Browser error: {e}")
    print("   Make sure Chromium is installed: sudo apt install chromium")
except PermissionError:
    print("❌ Error: Permission denied.")
    print("   Try saving to your Desktop or Documents folder instead.")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
finally:
    if driver:
        driver.quit()
    root.destroy()
    print("\nDone.")