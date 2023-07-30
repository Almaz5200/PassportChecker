import bs4
from dataclasses import dataclass
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pyvirtualdisplay import Display

# set xvfb display since there is no GUI in docker container.
display = Display(visible=0, size=(800, 600))
display.start()


@dataclass
class CrawlResult:
    status: str
    progress: str


class ParsingError(Exception):
    def __init__(self, message: str):
        self.message = message


def crawl(id: str) -> CrawlResult:
    if not id.isdigit():
        raise ValueError("id must be a number")

    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager(driver_version="114.0.5735.90").install()),
        options=options,
    )

    url = "https://info.midpass.ru/?id={}#".format(id)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "data-block-stat"))
        )
    except Exception:
        raise ParsingError("can't parse page")

    response_html = driver.page_source
    soup = bs4.BeautifulSoup(response_html, "html.parser")

    status = soup.find("span", {"class": "data-block-stat"})
    if status is None:
        raise ParsingError("status is None")
    status = status.text.strip()

    percent = soup.find("div", {"id": "progress"})
    if percent is None:
        raise ParsingError("percent is None")
    percent = percent.get("class")[1].split("-")[-1]

    return CrawlResult(status, percent)


if __name__ == "__main__":
    print(crawl("123456"))
