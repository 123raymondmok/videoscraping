from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Config
screenshotDir = "Screenshots"  # Directory to store screenshots
screenWidth = 400  # Width of the browser window for taking screenshots
screenHeight = 800  # Height of the browser window for taking screenshots

def getPostScreenshots(filePrefix, script):
    """
    Captures screenshots of the post and comment frames using Selenium.

    Parameters:
    - filePrefix: Prefix for naming the screenshot files.
    - script: An instance of the VideoScript class containing information about the video script.
    """
    print("Taking screenshots...")
    driver, wait = __setupDriver(script.url)
    script.titleSCFile = __takeScreenshot(filePrefix, driver, wait)
    for commentFrame in script.frames:
        commentFrame.screenShotFile = __takeScreenshot(filePrefix, driver, wait, f"t1_{commentFrame.commentId}")
    driver.quit()

def __takeScreenshot(filePrefix, driver, wait, handle="Post"):
    """
    Takes a screenshot of a specific element on the webpage.

    Parameters:
    - filePrefix: Prefix for naming the screenshot file.
    - driver: The Selenium WebDriver.
    - wait: The WebDriverWait for handling waits.
    - handle: Identifier for the element to capture (default is "Post").

    Returns:
    - The filename of the saved screenshot.
    """
    method = By.CLASS_NAME if (handle == "Post") else By.ID
    search = wait.until(EC.presence_of_element_located((method, handle)))
    driver.execute_script("window.focus();")

    fileName = f"{screenshotDir}/{filePrefix}-{handle}.png"
    fp = open(fileName, "wb")
    fp.write(search.screenshot_as_png)
    fp.close()
    return fileName

def __setupDriver(url: str):
    """
    Sets up the Selenium WebDriver with specified options and navigates to the given URL.

    Parameters:
    - url: The URL to navigate to.

    Returns:
    - A tuple containing the WebDriver and WebDriverWait instances.
    """
    options = webdriver.FirefoxOptions()
    options.headless = False  # Set to True for headless mode (no visible browser window)
    options.enable_mobile = False  # Set to True for mobile emulation

    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 10)

    driver.set_window_size(width=screenWidth, height=screenHeight)
    driver.get(url)

    return driver, wait
