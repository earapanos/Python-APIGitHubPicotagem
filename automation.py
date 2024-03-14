import psycopg2
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from ftplib import FTP

class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            host='locates.cxq8janeztvw.us-east-2.rds.amazonaws.com',
            port=5432,
            dbname='locates',
            user='postgres',
            password='LocatesAPI789'
        )

    def get_all_centroid_coordinates(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT ST_X(ST_Centroid(geom)), ST_Y(ST_Centroid(geom)), gid FROM esteira.imoveis where geom is not null and gid >345")
            results = cur.fetchall()
            return results

class URLGenerator:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def generate_url(self):
        return f"https://earapanos.github.io/GoogleHybridWebSearch/#15/{self.latitude:.4f}/{self.longitude:.4f}"

class ScreenshotTaker:
    def __init__(self, url, gid):
        self.url = url
        self.gid = gid
        chrome_options = Options()
        chrome_options.add_argument("--window-size=316,538") # change the resolution
        self.driver = webdriver.Chrome(options=chrome_options)  # Use the appropriate driver (e.g., ChromeDriver)

    def take_screenshot(self):
        self.driver.get(self.url)
        time.sleep(2)  # Wait for the page to load
        screenshot_name = f"C:\\locates\\img_automation\\img\\{self.gid}_screenshot.jpg"
        self.driver.save_screenshot(screenshot_name)
        print(f"Screenshot saved: {screenshot_name}")
        return screenshot_name

class FTPUploader:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def upload_file(self, local_path, remote_path):
        with FTP(self.host) as ftp:
            ftp.login(self.user, self.password)
            with open(local_path, 'rb') as file:
                ftp.storbinary(f"STOR {remote_path}", file)
            print(f"File uploaded: {local_path} -> {remote_path}")

class AutomacaoLocates:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.url_gen = None
        self.screenshot_taker = None
        self.ftp_uploader = FTPUploader("ftp.locates.com.br", "admin@locates.com.br", "LocatesAPI789")

    def run(self):
        coordinates = self.db_manager.get_all_centroid_coordinates()
        for coordinate in coordinates:
            gid = coordinate[2]
            latitude = round(coordinate[1], 3)
            longitude = round(coordinate[0], 4)
            self.url_gen = URLGenerator(latitude, longitude)
            url = self.url_gen.generate_url()
            self.screenshot_taker = ScreenshotTaker(url, gid)
            screenshot_path = self.screenshot_taker.take_screenshot()
        self.upload_images_to_ftp()

    def upload_images_to_ftp(self):
        local_image_dir = "C:\\locates\\img_automation\\img\\"
        remote_image_dir = "/bis/automacao/"
        for filename in os.listdir(local_image_dir):
            if filename.endswith(".jpg"):
                local_path = os.path.join(local_image_dir, filename)
                remote_path = os.path.join(remote_image_dir, filename)
                self.ftp_uploader.upload_file(local_path, remote_path)
        print('All images uploaded to FTP successfully!')

if __name__ == "__main__":
    automacao = AutomacaoLocates()
    automacao.run()
