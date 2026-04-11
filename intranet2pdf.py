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
# ENV VAR CONSTANTS — INTRANET SPECIFIC SETTINGS,
# ================================================================

# Keywords that identify the login/auth page in the URL
LOGIN_URL_KEYWORDS = ["sign_in", "login", "auth"]

# Path to the Chromium browser binary on Linux
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

# INSPECTED: <input id="user_email" name="user[email]" type="email" ...>
# Using By.ID — most reliable selector since id is unique on the page
SELECTOR_EMAIL = (By.ID, "user_email")

# INSPECTED: <input id="user_password" name="user[password]" type="password" ...>
# Using By.ID — most reliable selector since id is unique on the page
SELECTOR_PASSWORD = (By.ID, "user_password")

# INSPECTED: <input type="submit" name="commit" value="Log in" class="btn btn-primary" ...>
# No id present — using value attribute since it's specific to this button
SELECTOR_SUBMIT = (By.CSS_SELECTOR, "input[value='Log in']")



# ================================================================
# ⚠️  LOGIN SUCCESS DETECTION — INSPECT THIS TOO
# ================================================================
# INSPECTED: <div class="alert alert-danger sm-gap big-zindex">Invalid email or password</div>
# Using .alert.alert-danger — the two most specific classes, ignoring sm-gap and big-zindex
# which are likely just styling/positioning classes that could change
ERROR_SELECTOR = (By.CSS_SELECTOR, ".alert.alert-danger")


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


# ================================================================
# HELPER FUNCTION 1 — CLEAN EXIT
# ================================================================

def clean_exit(message=None):
    # clean_exit() is a reusable shutdown function that safely stops the program
    # from anywhere in the script — whether something went wrong or the user cancelled.
    #
    # It always does three things in order:
    #   1. Print a message to the terminal (if one was passed in)
    #   2. Destroy the hidden tkinter window to free memory
    #   3. Exit the Python program completely
    #
    # WHY DO WE NEED THIS?
    # Without it, if we just called sys.exit() directly, the hidden tkinter window
    # would stay alive in memory. And if we just called root.destroy() without
    # sys.exit(), the program would keep running past the point we wanted it to stop.
    # clean_exit() wraps both into one safe call.
    #
    # THE message=None PARAMETER:
    # message=None means the argument is optional — the caller can pass a message
    # or nothing at all. If a message is passed (e.g. "❌ No URL entered. Exiting.")
    # it gets printed to the terminal before shutdown. If nothing is passed, the
    # function skips the print and just shuts down silently.
    #
    # WHY try/except AROUND root.destroy()?
    # If root.destroy() has already been called earlier (e.g. tkinter already cleaned
    # up), calling it again would throw an error and crash the exit itself — which
    # would be ironic. The try/except silently ignores that edge case with pass,
    # and lets sys.exit() run regardless.

    if message:
        print(message)

    try:
        root.destroy()  # Close the hidden tkinter window and free its memory
    except Exception:
        pass            # Tkinter was already destroyed — safe to ignore and move on

    sys.exit()          # Terminate the Python program immediately and cleanly


# ================================================================
# HELPER FUNCTION 2 — SET UP SELENIUM CHROMIUM DRIVER
# ================================================================

def create_driver():
    """
    Configures and returns a Selenium Chrome WebDriver instance 
    "with the 'Options()' class from 'selenium.webdriver.chrome.options'.
    Uses Selenium Manager (built into Selenium 4.6+) to automatically
    download the correct chromedriver — no manual install needed.
    """


    chrome_options = Options() 

    # ----------------
    # Defining Options
    # ----------------
    # ---- Headless & Sandbox ----
    chrome_options.add_argument("--headless=new")        # No visible browser window



    # -----------------------------------------------------
    # WHAT IS A SANDBOX?

    # Normally when Chromium runs, it wraps itself in a 
    # sandbox — an OS-level security wall that isolates 
    # the browser from the rest of your system. 
    # Think of it like this:

    # WITHOUT sandbox:                  WITH sandbox (normal):
    # ┌─────────────────┐               ┌─────────────────┐
    # │   Your System   │               │   Your System   │
    # │                 │               │  ┌───────────┐  │
    # │    Chromium     │               │  │  SANDBOX  │  │
    # │  (full access)  │               │  │ Chromium  │  │
    # │                 │               │  │(isolated) │  │
    # └─────────────────┘               │  └───────────┘  │
    #                                   └─────────────────┘

    # The sandbox stops a malicious webpage from breaking out 
    # of the browser and touching your files, processes, or system,
    

    # WHY DOES IT BREAK ON KALI / AS ROOT?

    # The sandbox works by creating a restricted child process with 
    # lower privileges than the parent. The OS enforces this.
    # The problem is — if you are already running as root, you are 
    # already at the highest privilege level. The OS cannot create 
    # a process with lower privileges than root, so the sandbox 
    # mechanism fails entirely and Chromium refuses to start.
    # Kali Linux by default logs you in as root, which is why this
    # error always comes up on Kali specifically.
    # -------------------------------------------------------------

    # WHAT --no-sandbox DOES?

    # it simply tells chromium:
    # "skip the sandbox — don't try to create that restricted wrapper process."
    # So Chromium can launch when running as root.
    # Safe here because we control exactly
    # what URLs the browser visits —
    # we are not browsing the open web freely.                               

    chrome_options.add_argument("--no-sandbox") 

    # -----------------------------------------------------------------------
    # /dev/shm is a small shared memory partition on Linux that Chromium uses
    # by default to store temporary rendering data. On many Linux systems — 
    # especially containers and Kali — this partition is too small for 
    # Chromium's needs, causing it to crash mid-render.
    # --disable-dev-shm-usage tells Chromium to use the regular /tmp folder 
    # instead, which has no such size restriction.
    # ------------------------------------------------------------------------  
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