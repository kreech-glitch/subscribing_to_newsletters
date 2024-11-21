from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import os
import ctypes
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

def disable_quick_edit():
    """
    Disable Quick Edit mode in Windows Command Prompt to prevent accidental pauses.
    """
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-10)  # Get handle to the console input buffer (-10 means STD_INPUT_HANDLE)
    
    # Get the current console mode
    mode = ctypes.c_uint()
    kernel32.GetConsoleMode(handle, ctypes.byref(mode))
    
    # Disable Quick Edit mode (bit 4) and reapply the mode
    new_mode = mode.value & ~(0x0040)  # Clear the ENABLE_QUICK_EDIT_MODE bit
    kernel32.SetConsoleMode(handle, new_mode)

disable_quick_edit()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Counters
Subscribed, good, bad = 0, 0, 0
num = 1000  # Adjust this as needed
driver_path = ''

# Function to request the user to upload the emails.txt file
def select_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    file_path = filedialog.askopenfilename(title="Select emails.txt", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    return file_path

# Function to setup the Chrome driver
def setup_driver():
    service = Service(driver_path)  # Use the Service class for the driver path
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Run headless (without opening a browser window)
    return webdriver.Chrome(service=service, options=options)  # Use the Service class

# Updated list of newsletter URLs and their selectors (removed first name and last name selectors)
newsletters = {
    "https://www.shopify.com/retail": {
        "email": (By.XPATH, '//*[@id="email-input-:R78ln5H1:"]'),
        "button": (By.XPATH, '//*[@id=":R78ln5:"]/div/button'),
        "confirmation": (By.XPATH, '//*[contains(text(), "Thank you for subscription!")]')
    }, 
    "https://www.fragrancefoundation.fr/newsletter-adherents/": {
        "email": (By.XPATH, '//*[@id="mce-EMAIL"]'),
        "button": (By.XPATH, '//*[@id="mc-embedded-subscribe"]'),
        "confirmation": (By.XPATH, '//*[contains(text(), "Thank you for subscribing!")]')
    },
    "https://www.dayspring.com/": {
        "email": (By.XPATH, '//*[@id="st-signup-footer-email"]'),
        "button": (By.XPATH, '//*[@id="sailthru-signup-footer"]'),
        "confirmation": (By.XPATH, '//*[contains(text(), "Your first email is on its way.")]')
    },
    "https://lifehacker.com/newsletters": {
        "email": (By.XPATH, '//*[@id="email"]'),
        "button": (By.XPATH, '//*[@id="newsletter-form"]/button'),
        "confirmation": (By.XPATH, '//*[contains(text(), "Success!")]')
    },
    "https://www.indigo.ca/en-ca/": {
        "email": (By.XPATH, '//*[@id="footercontent"]/div/div[2]/div[4]/div[1]/div[2]/form/div/input'),
        "button": (By.XPATH, '//*[@id="footercontent"]/div/div[2]/div[4]/div[1]/div[2]/form/div/span/button'),
        "confirmation": (By.XPATH, '//*[contains(text(), "Thanks for subscribing!")]')
    },
    "https://my.kiplinger.com/email/signup.php": {
        "email": (By.XPATH, '//*[@id="kipEmail"]'),
        "button": (By.XPATH, '//*[@id="emailsubmit"]'),
        "confirmation": (By.XPATH, '//*[contains(text(), "Form submitted. Thank you for subscribing!")]')
    }
}

# Function to display subscription status
def center(text):
    return "\n".join(line.center(os.get_terminal_size().columns) for line in text.splitlines())

def screen():
    BOLD = '\033[1m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'
    global Subscribed, good, bad, num
    art_text = """
     
      \033[1;37m ██████╗ ██████╗ ██████╗ ███████╗██████╗     ██████╗ ██╗   ██╗    ██╗  ██╗██████╗ ███████╗ ██████╗██╗  ██╗
      \033[1;37m██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗    ██╔══██╗╚██╗ ██╔╝    ██║ ██╔╝██╔══██╗██╔════╝██╔════╝██║  ██║
      \033[1;37m██║     ██║   ██║██║  ██║█████╗  ██║  ██║    ██████╔╝ ╚████╔╝     █████╔╝ ██████╔╝█████╗  ██║     ███████║
      \033[1;31m██║     ██║   ██║██║  ██║██╔══╝  ██║  ██║    ██╔══██╗  ╚██╔╝      ██╔═██╗ ██╔══██╗██╔══╝  ██║     ██╔══██║
      \033[1;31m╚██████╗╚██████╔╝██████╔╝███████╗██████╔╝    ██████╔╝   ██║       ██║  ██╗██║  ██║███████╗╚██████╗██║  ██║
      \033[1;31m ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═════╝     ╚═════╝    ╚═╝       ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝
                                                                                                                          
    """

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the terminal screen
        ctypes.windll.kernel32.SetConsoleTitleW("Subscribing to Newsletters")  # Set the console title

        # Display the centered ASCII art
        print(center(art_text))

        # Display the status below the ASCII art
        print(f"{BOLD}{YELLOW}Created By ANOUAR 009 **YAHOO TEAM**{RESET}")
        print("██████████████████████████████████████████████")
        print(f" - Subscribed: [{Subscribed}/{num}] ")
        print(f" - Good: [{good}]                   ")
        print(f" - Bad: [{bad}]                     ")
        print("██████████████████████████████████████████████")
        time.sleep(2)  # Refresh every 2 seconds

# Start the display function in a separate thread
threading.Thread(target=screen, daemon=True).start()


# Function to subscribe to newsletters
def subscribe_to_newsletters(emails):
    global Subscribed, good, bad
    failed_subscriptions = []  # List to store failed emails and newsletters

    for email in emails:
        for newsletter_url, selectors in newsletters.items():
            driver = setup_driver()
            driver.get(newsletter_url)

            try:
                # Handle popup windows if they appear
                try:
                    # Wait for and close the newsletter sign-up popup if it exists
                    close_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="PopupSignupForm_0"]/div[2]/button'))
                    )
                    close_button.click()
                    logging.info("Popup sign-up window closed.")
                except Exception as e:
                    logging.info("No sign-up popup appeared.")

                try:
                    # Wait for and close the cookies popup if it exists
                    cookie_close_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="cn-close-notice"]'))
                    )
                    cookie_close_button.click()
                    logging.info("Cookies popup closed.")
                except Exception as e:
                    logging.info("No cookies popup appeared.")

                # Now that the popups are closed, search for the email input field
                email_input = WebDriverWait(driver, 8).until(
                    EC.visibility_of_element_located(selectors["email"])
                )
                email_input.clear()
                email_input.send_keys(email)

                # Wait for the subscribe button and click it
                subscribe_button = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable(selectors["button"])
                )
                subscribe_button.click()

                # Wait for the confirmation message
                WebDriverWait(driver, 8).until(
                    EC.visibility_of_element_located(selectors["confirmation"])
                )
                logging.info(f"Successfully subscribed {email} to {newsletter_url}")
                Subscribed += 1
                good += 1

            except Exception as e:
                logging.error(f"Error during subscription for {email} to {newsletter_url}: {e}")
                bad += 1
                failed_subscriptions.append(f"{email}:{newsletter_url}")  # Store email and newsletter URL

            finally:
                driver.quit()

    # After processing, save failed subscriptions to a text file
    if failed_subscriptions:
        with open('failed_subscriptions.txt', 'w') as file:
            for entry in failed_subscriptions:
                file.write(entry + '\n')
        logging.info("Failed subscriptions have been saved to 'failed_subscriptions.txt'.")

    # Notify the user that the process is complete
    notify_completion_popup()  # Use the popup notification

# Function to notify the user with a popup message
def notify_completion_popup():
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    messagebox.showinfo("Script Completed", "The subscription process is finished.\nCheck 'failed_subscriptions.txt' for any errors.")

# Final call to start the script
file_path = select_file()

if file_path:
    try:
        with open(file_path, 'r') as file:
            emails = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logging.error(f"{file_path} file not found.")
    else:
        subscribe_to_newsletters(emails)
else:
    logging.error("No file selected.")