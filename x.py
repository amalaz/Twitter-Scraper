import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def login_to_twitter(driver, your_email, your_password):
    try:
        driver.get("https://twitter.com/i/flow/login")
        time.sleep(3)

        # Step 1: Enter email/username
        email_field = driver.find_element(By.XPATH, "//input[@autocomplete='username']")
        email_field.send_keys(your_email)
        driver.find_element(By.XPATH, "//span[text()='Next']").click()
        time.sleep(3)

        # Skip email or username verification steps

        # Step 2: Enter password
        password_field = driver.find_element(By.XPATH, "//input[@autocomplete='current-password']")
        password_field.send_keys(your_password)
        driver.find_element(By.XPATH, "//span[text()='Log in']").click()
        time.sleep(5)

        # Skip any 2FA code inputs

        return True
    except Exception as e:
        print(f"Login failed: {str(e)}")
        return False

def get_following_list(target_username, your_email, your_password):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    if not login_to_twitter(driver, your_email, your_password):
        print("❌ Failed to login to Twitter")
        driver.quit()
        return

    print(f"Logged in successfully. Fetching following list for @{target_username}...")

    try:
        driver.get(f"https://twitter.com/{target_username}/following")
        time.sleep(5)

        # Scroll to load enough followers (adjust number of scrolls as needed)
        scroll_pause_time = 2
        last_height = driver.execute_script("return document.body.scrollHeight")
        scrolls = 5
        for _ in range(scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Extract following usernames
        following_elements = driver.find_elements(By.XPATH, "//div[@data-testid='UserCell']//div[@dir='ltr']/span")
        following_usernames = set()
        for elem in following_elements:
            username_text = elem.text
            if username_text.startswith("@"):
                following_usernames.add(username_text[1:])  # strip '@'

        print(f"@{target_username} is following {len(following_usernames)} users:")
        for u in sorted(following_usernames):
            print(u)
    except Exception as e:
        print(f"❌ Error fetching following list: {str(e)}")
    finally:
        driver.quit()

def main():
    target_usernames = os.getenv("TARGET_USERNAMES", "").split(",")
    your_email = os.getenv("TWITTER_EMAIL")
    your_password = os.getenv("TWITTER_PASSWORD")

    if not target_usernames or target_usernames == [""]:
        print("❌ No usernames provided. Please set the TARGET_USERNAMES environment variable.")
        return

    if not your_email or not your_password:
        print("❌ Twitter email or password environment variables not set.")
        return

    for target_username in target_usernames:
        target_username = target_username.strip()
        if target_username:
            print(f"🔍 Processing @{target_username}")
            try:
                get_following_list(target_username, your_email, your_password)
            except Exception as e:
                print(f"❌ Error processing @{target_username}: {str(e)}")

if __name__ == "__main__":
    main()
