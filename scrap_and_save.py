from playwright.sync_api import sync_playwright

def fetch_and_save(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.screenshot(path="screenshot.png", full_page=True)
        content = page.inner_html("div#bodyContent")
        with open("chapter_raw.html", "w", encoding="utf-8") as f:
            f.write(content)
        browser.close()

if __name__ == "__main__":
    fetch_and_save("https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1")
