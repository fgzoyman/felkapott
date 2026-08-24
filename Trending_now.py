"""
+ Thought: Formulating the Python Code · 69ms
Íme a Python függvény a SeleniumBase Undetected Chromedriver használatával és lapozással:
"""

import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from seleniumbase import Driver


def scrape_gtrends_with_pagination(url: str, headless: bool = True):
    """
    Letölti a Google Trends weboldal összes oldalát, lapozva.
    """
    # Automatikus Chromedriver ellenőrzés és illesztés a Chrome verzióhoz
    ChromeUpdateException = None
    try:
        subprocess.run([sys.executable, "-m", "seleniumbase", "get", "chromedriver", "latest"], check=True)
    except ChromeUpdateException as e:
        print(f"Nem sikerült frissíteni a Chromedriver-t: {e}")

    driver = Driver(uc=True, headless=headless)
    timestamp = datetime.now(tz = ZoneInfo("Europe/Budapest")).strftime("%Y-%m-%d_%H-%M-%S")
    
    try:
        driver.get(url)
        # Görgetés az oldal aljára, hogy betöltődjön a lapozó
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.sleep(2)
    
        # Alapértelmezett 25-ös nézet megtartása, így ~74 sor esetén 3 oldal lesz (a, b, c)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.sleep(2)

        page_index = 0
        previous_html = None

        while True:
            # Végig kell görgetni az oldalon fel-le, hogy a lusta módon betöltődő (lazy-loaded) sparkline grafikonok renderelődjenek
            driver.execute_script("window.scrollTo(0, 0);")
            driver.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            driver.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.sleep(2)

            # Várakozás, hogy a polyline-ok points attribútumai kitöltődjenek (max 10 mp)
            for _ in range(10):
                has_points = driver.execute_script("""
                    const polylines = document.querySelectorAll('polyline');
                    for (let p of polylines) {
                        if (p.getAttribute('points') && p.getAttribute('points').trim() !== '') {
                            return true;
                        }
                    }
                    return false;
                """)
                if has_points:
                    break
                driver.sleep(1)

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
            PagingException = None
            try:
                # Keresés magyar és angol aria-label alapján
                next_btn = driver.find_element("xpath", "//button[contains(@aria-label, 'következő oldalra') or contains(@aria-label, 'next page')]")

                driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                driver.sleep(1)
                driver.execute_script("arguments[0].click();", next_btn)
                driver.sleep(3) # Várás az új tartalom betöltődésére
                
                page_index += 1
            except PagingException as e:
                print(f"Hiba történt a lapozás során: {e}")
                break

    finally:
        driver.quit()

# Használati példa:
url = "https://trends.google.com/trending?geo=HU"
scrape_gtrends_with_pagination(url, headless=True)
