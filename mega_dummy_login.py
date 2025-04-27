import asyncio
from playwright.async_api import async_playwright, TimeoutError
import random
import time


async def random_delay(min_delay=3, max_delay=7):
    delay = random.uniform(min_delay, max_delay)
    await asyncio.sleep(delay)


async def type_humanlike(element, text):
    for char in text:
        await element.type(char)
        await random_delay(0.1, 0.3)


async def handle_alert(page):
    try:
        # Create a future to store the dialog
        dialog_future = asyncio.Future()

        async def handle_dialog(dialog):
            print("Alert message:", dialog.message)
            await dialog.accept()
            if not dialog_future.done():
                dialog_future.set_result(True)

        # Listen for dialog events
        page.on('dialog', handle_dialog)

        try:
            # Wait for the dialog with a timeout
            await asyncio.wait_for(dialog_future, timeout=15.0)
            print("Alert detected and handled")
            return True
        except asyncio.TimeoutError:
            print("No alert detected")
            return False
        finally:
            # Remove the listener
            page.remove_listener('dialog', handle_dialog)

    except Exception as e:
        print(f"Error handling alert: {str(e)}")
        return False


async def handle_terms_policy(page):
    try:
        print("Looking for Terms Policy...")
        terms_button = await page.wait_for_selector(
            'button.mega-button.js-more-info[data-continue-link="https://mega.io/terms-upcoming"]', timeout=5000)
        if terms_button:
            print("Found Terms Policy, looking for close button...")
            close_button = await page.wait_for_selector(
                'button.mega-component.nav-elem.mega-button.action.icon.js-close', timeout=5000)
            if close_button:
                print("Clicking close button for Terms Policy...")
                await close_button.click()
                await random_delay(3, 7)
                return True
    except TimeoutError:
        print("No Terms Policy found")
        return False
    return True


async def handle_storage_full(page):
    try:
        print("Checking for storage full popup...")
        storage_header = await page.wait_for_selector(
            '#bodyel > section:nth-child(40) > div.mega-dialog.dialog-template-action.storage-dialog.almost-full > header > h2.almost-full',
            timeout=10000)
        if storage_header:
            print("Found storage full popup, looking for close button...")
            close_button = await page.wait_for_selector(
                '#bodyel > section:nth-child(40) > div.mega-dialog.dialog-template-action.storage-dialog.almost-full > button',
                timeout=10000)
            if close_button:
                print("Clicking close button for storage full...")
                await close_button.click()
                await random_delay(3, 7)
                return True
    except TimeoutError:
        print("No storage full popup found")
        return False
    return True


async def handle_pro_upgrade(page):
    try:
        print("Checking for Pro upgrade popup...")
        upgrade_title = await page.wait_for_selector('div.upgrade-to-pro-dialog-title', timeout=10000)
        if upgrade_title:
            print("Found Pro upgrade popup, looking for 'Maybe later' button...")
            maybe_later = await page.wait_for_selector(
                '#bodyel > section:nth-child(40) > div.mega-dialog.dialog-template-action.storage-dialog.almost-full > button',
                timeout=10000)
            if maybe_later:
                print("Clicking 'Maybe later'...")
                await maybe_later.click()
                await random_delay(3, 7)
                return True
    except TimeoutError:
        print("No Pro upgrade popup found")
        return False
    return True


async def handle_final_popup(page):
    try:
        print("Looking for checkbox...")
        checkbox = await page.wait_for_selector('#show-again', timeout=15000)
        if checkbox:
            print("Checking the checkbox...")
            await checkbox.check()
            await random_delay(3, 4)

        print("Looking for final close button...")
        close_button = await page.wait_for_selector(
            '#bodyel > div.mega-component.mega-sheet.custom-alpha.overlay-wrap.with-footer.active.normal.dynamic-height > div > div.header.mb-4.relative > button',
            timeout=15000)
        if close_button:
            print("Clicking final close button...")
            await close_button.click()
            await random_delay(3, 4)
            return True
    except TimeoutError:
        print("No final popup found")
        return False
    return True


async def login_mega(email, password):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="your browser path",
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-startup-window',
                '--silent-launch',
                '--window-position=-32000,-32000',
            ]
        )

        context = await browser.new_context(
            viewport=None,
            ignore_https_errors=True
        )

        page = await context.new_page()

        try:
            print("Navigating to mega.nz...")
            await page.goto('https://mega.nz/login', timeout=60000)
            print("Waiting for initial page load...")
            await random_delay(5, 8)

            print("Looking for email input...")
            email_input = await page.wait_for_selector('#login-name2', timeout=30000)
            if email_input:
                await email_input.click()
                await random_delay(1, 2)
                await type_humanlike(email_input, email)
                await random_delay(2, 3)
            else:
                print("Email input not found")
                return False

            print("Looking for password input...")
            password_input = await page.wait_for_selector('#login-password2', timeout=30000)
            if password_input:
                await password_input.click()
                await random_delay(1, 2)
                await type_humanlike(password_input, password)
                await random_delay(2, 3)
            else:
                print("Password input not found")
                return False

            # Set up alert handler before clicking login
            print("Setting up alert handler...")
            alert_future = handle_alert(page)

            print("Looking for login button...")
            login_button = await page.wait_for_selector('button.login-button', timeout=30000)
            if login_button:
                await random_delay(1, 2)
                await login_button.click()
                print("Clicked login button")
            else:
                print("Login button not found")
                return False

            print("Waiting for login process...")
            await random_delay(8, 12)

            # Wait for alert handler to complete
            print("Waiting for potential alert...")
            await alert_future
            await random_delay(3, 5)

            # Check current URL and redirect if needed
            current_url = page.url
            print(f"Current URL after login: {current_url}")
            if "blog.mega.io" in current_url:
                print("Detected blog redirect, navigating back to mega.nz...")
                await page.goto('https://mega.nz', timeout=60000)
                await random_delay(3, 5)

            # Wait for FM to load
            try:
                try:
                    await page.wait_for_selector('#pmlayout', timeout=30000)
                    print(f"Successfully logged in with {email}")
                except:
                    pass

                # Handle all possible popups in sequence
                await handle_terms_policy(page)
                await random_delay(3, 5)

                await handle_storage_full(page)
                await random_delay(3, 5)

                await handle_pro_upgrade(page)
                await random_delay(3, 5)

                await handle_final_popup(page)
                await random_delay(3, 5)

                await browser.close()

            except TimeoutError:
                print(f"Failed to detect successful login {email}")
                print(f"Current URL: {page.url}")
                return False

        except Exception as e:
            print(f"Error during login: {str(e)}")
            print(f"Current URL: {page.url}")
            return False


async def main():
    # Read accounts from file
    with open('accounts.txt', 'r') as f:
        lines = f.readlines()
        for account in lines[109:]:
            try:
                email, password, *_ = account.strip().split(',')
                print(f"\nAttempting login for: {email}")
                await login_mega(email, password)
            except KeyboardInterrupt:
                print("\nScript interrupted by user.")
                break
            except Exception as e:
                print(f"Error processing account: {email}\n {str(e)}")
                continue


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClosing browser...")