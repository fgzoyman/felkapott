"""
+ Thought: Formulating the Python Code · 69ms
Íme a Python függvény a SeleniumBase Undetected Chromedriver használatával és lapozással:
"""
from datetime import datetime
from seleniumbase import Driver

def scrape_gtrends_with_pagination(url: str, headless: bool = True):
    """
    Letölti a Google Trends weboldal összes oldalát 50-es nézetben, lapozva.
    """
    driver = Driver(uc=True, headless=headless)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    try:
        driver.get(url)
        # Görgetés az oldal aljára, hogy betöltődjön a lapozó
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.sleep(2)
    
        try:
            # Kattintás a "Rows per page" / "Oldalankénti sorszám" legördülő menüre (25 -> 50)
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
            print(f"Nem sikerült átállítani az oldalszámot 50-re: {e}")

        page_index = 0
        previous_html = None

        while True:
            driver.sleep(4) # Várjunk, hogy a dinamikus grafikák/sparkline-ok betöltődjenek
            # html = driver.page_source
            html = driver.execute_script("return document.documentElement.outerHTML;")

            # Ellenőrzés: ha az oldal tartalma megegyezik az előzővel, megállunk
            if previous_html is not None and html == previous_html:
                print("Az oldal tartalma megegyezik az előzővel, elértük a véget.")
                break

            previous_html = html
            letter = chr(ord('a') + page_index)
            fajlnev = f"gtrends_{timestamp}_{letter}.html"
            
            with open(fajlnev, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Mentve: {fajlnev}")

            # Lapozás a következő oldalra
            try:
                # Keresés magyar és angol aria-label alapján
                next_btn = driver.find_element("xpath", "//button[contains(@aria-label, 'következő oldalra') or contains(@aria-label, 'next page')]")

                driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                driver.sleep(1)
                driver.execute_script("arguments[0].click();", next_btn)
                driver.sleep(3) # Várás az új tartalom betöltődésére
                
                page_index += 1
            except Exception as e:
                print(f"Hiba történt a lapozás során: {e}")
                break

    finally:
        driver.quit()

# Használati példa:
url = "https://trends.google.com/trending?geo=HU"
scrape_gtrends_with_pagination(url, headless=True)
