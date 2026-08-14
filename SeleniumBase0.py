"""
+ Thought: Formulating the Python Code · 69ms
Íme a Python függvény a SeleniumBase Undetected Chromedriver használatával:
"""
from datetime import datetime
from seleniumbase import Driver

def get_html_with_undetected_chromedriver(url: str, headless: bool = True) -> str:
    """
    Letölti egy weboldal HTML kódját a SeleniumBase Undetected Chromedriver-ével.
    """
    driver = Driver(uc=True, headless=headless)
    try:
        driver.get(url)
        # Görgetés az oldal aljára, hogy betöltődjön a lapozó
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.sleep(2)
        
        try:
            # Kattintás a "Rows per page" / "Oldalankénti sorszám" legördülő menüre (25 -> 50) JavaScript segítségével
            dropdown = driver.find_element("xpath", "//*[contains(text(), '25')]")
            driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
            driver.sleep(1)
            driver.execute_script("arguments[0].click();", dropdown)
            driver.sleep(1)
            
            # Kiválasztjuk az 50-es értéket a lenyíló menüből JS kattintással
            option_50 = driver.find_element("xpath", "//div[@role='option']//*[contains(text(), '50')] | //*[text()='50']")
            driver.execute_script("arguments[0].click();", option_50)
            driver.sleep(2)
        except Exception as e:
            print(f"Nem sikerült átállítani az oldalszámot: {e}")

        return driver.page_source
    finally:
        driver.quit()

# Használati példa:

url = "https://trends.google.com/trending?geo=HU"
html = get_html_with_undetected_chromedriver(url)

fajlnev = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_gtrends.txt"

with open(fajlnev, "w", encoding="utf-8") as f:
  f.write(html)

