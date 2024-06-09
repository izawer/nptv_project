import tkinter as tk  # Tkinter mooduli importimine graafilise kasutajaliidese loomiseks.
from tkinter import filedialog, messagebox  # Filedialogi ja messageboxi importimine tkinterist failide valimiseks ja teadete jaoks.
from PIL import Image, ImageTk  # Image ja ImageTk importimine PIL-ist piltidega töötamiseks.
import requests  # Requests mooduli importimine HTTP-päringute jaoks.
from io import BytesIO  # BytesIO importimine mälu binaarvoogudega töötamiseks.
import random  # Random mooduli importimine juhuslike stringide genereerimiseks.
import csv  # CSV mooduli importimine CSV-failidega töötamiseks.
import os  # OS mooduli importimine operatsioonisüsteemist sõltuvate funktsioonide jaoks.
from tqdm import tqdm  # Tqdm importimine edenemisnäidikute kuvamiseks.
from selenium import webdriver  # Webdriveri importimine seleniumist brauseri automatiseerimiseks.
from selenium.webdriver.common.by import By  # By importimine elementide leidmise strateegia jaoks.
from selenium.webdriver.edge.service import Service as EdgeService  # EdgeService'i importimine Edge WebDriveri haldamiseks.
from webdriver_manager.microsoft import EdgeChromiumDriverManager  # EdgeChromiumDriverManageri importimine Edge WebDriveri paigaldamise haldamiseks.

class LightshotDownloader:
    def __init__(self, root):
        self.root = root  # Peamise akna määramine.
        self.root.title("Lightshot Downloader")  # Peamise akna pealkirja määramine.

        self.url_label = tk.Label(root, text="Sisestage allalaaditavate piltide arv:")  # Sildi vidina loomine.
        self.url_label.pack()  # Sildi paigutamine aknasse.

        self.url_entry = tk.Entry(root, width=10)  # Sisendvidina loomine numbri sisestamiseks.
        self.url_entry.pack()  # Sisendvidina paigutamine aknasse.

        self.select_folder_button = tk.Button(root, text="Vali kaust", command=self.select_folder)  # Kausta valimise nupu loomine.
        self.select_folder_button.pack()  # Nupu paigutamine aknasse.

        self.download_button = tk.Button(root, text="Laadi pildid alla", command=self.download_images)  # Piltide allalaadimise nupu loomine.
        self.download_button.pack()  # Nupu paigutamine aknasse.

        self.image_label = tk.Label(root)  # Piltide kuvamise vidina loomine.
        self.image_label.pack()  # Vidina paigutamine aknasse.

        self.folder_path = ""  # Kausta tee algväärtustamine piltide salvestamiseks.
        self.csv_file = "images_data.csv"  # CSV-faili nimi piltide info salvestamiseks.

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()  # Kausta valimise dialoogi avamine.
        if self.folder_path:
            messagebox.showinfo("Tee valitud", f"Pildid salvestatakse kausta: {self.folder_path}")  # Teate kuvamine valitud tee kohta.

    def download_images(self):
        try:
            num_images = int(self.url_entry.get())  # Allalaaditavate piltide arvu saamine sisendist.
        except ValueError:
            messagebox.showerror("Viga", "Palun sisestage korrektne number")  # Veateate kuvamine, kui sisend on vale.
            return

        if not self.folder_path:
            messagebox.showerror("Viga", "Palun valige kaust piltide salvestamiseks")  # Veateate kuvamine, kui kausta pole valitud.
            return

        self.driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))  # Edge WebDriveri initsialiseerimine.
        self.driver.set_window_size(1920, 1080)  # Brauseri akna suuruse määramine.

        with open(os.path.join(self.folder_path, self.csv_file), mode='w', newline='') as file:
            writer = csv.writer(file)  # CSV-kirjutaja objekti loomine.
            writer.writerow(["Pildi number", "Faili nimi", "Suurus (KB)"])  # Päiste kirjutamine CSV-faili.

        for i in tqdm(range(num_images), desc="Piltide allalaadimine"):  # Tsükkel piltide allalaadimiseks.
            success = False
            while not success:
                try:
                    url = self.generate_random_url()  # Juhusliku pildi URL-i genereerimine.
                    self.driver.get(url)  # URL-i avamine brauseris.
                    image_element = self.driver.find_element(By.CSS_SELECTOR, "img.screenshot-image")  # Pildi elemendi leidmine lehelt.
                    image_url = image_element.get_attribute("src")  # Pildi URL-i saamine.
                    if image_url:
                        image = self.fetch_image(image_url)  # Pildi allalaadimine URL-i kaudu.
                        total_size_in_bytes = len(image.fp.getvalue())  # Pildi suuruse saamine baitides.
                        self.show_image(image)  # Pildi kuvamine liideses.
                        self.save_image(image, i, total_size_in_bytes / 1024)  # Pildi ja selle detailide salvestamine.
                        success = True
                    else:
                        print("Pildi URL-i ei leitud, uuesti proovimine...")  # Teate trükkimine, kui pildi URL-i ei leitud.
                except Exception as e:
                    print(f"Tekkis viga: {e}")  # Veateate trükkimine, kui tekib erandlik olukord.

    def show_image(self, image):
        image.thumbnail((1920, 1080))  # Pildi suuruse muutmine, et see sobiks 1920x1080 piksliga.
        photo = ImageTk.PhotoImage(image)  # Pildi teisendamine tkinterile sobivaks formaadiks.
        self.image_label.config(image=photo)  # Sildi uuendamine uue pildiga.
        self.image_label.image = photo  # Viite salvestamine pildile, et vältida selle kustutamist prügikoristajaga.

    def save_image(self, image, image_number, image_size_kb):
        filename = f"downloaded_image_{image_number}.png"  # Pildifaili nime loomine.
        image_path = os.path.join(self.folder_path, filename)  # Pildi täieliku tee loomine.
        image.save(image_path)  # Pildi salvestamine.

        # Pildi info kirjutamine CSV-faili
        csv_path = os.path.join(self.folder_path, self.csv_file)  # CSV-faili täieliku tee saamine.
        with open(csv_path, mode='a', newline='') as file:
            writer = csv.writer(file)  # CSV-kirjutaja objekti loomine.
            writer.writerow([image_number, filename, round(image_size_kb, 2)])  # Pildi detailide kirjutamine CSV-faili.

    def __del__(self):
        self.driver.quit()  # WebDriveri töö lõpetamine objekti hävitamisel.

if __name__ == "__main__":
    root = tk.Tk()  # Peamise akna loomine.
    app = LightshotDownloader(root)  # LightshotDownloader klassi eksemplari loomine.
    root.mainloop()  # Tkinteri sündmuste töötlemise tsükli käivitamine.
