import sys
import numpy as np
from astropy.io import fits
from astroquery.skyview import SkyView
from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery.simbad import Simbad
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QGroupBox, QWidget, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class AstroApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AstroApp - Visualisation FITS")
        self.setGeometry(100, 100, 1000, 700)

        # Menu bar
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("Fichier")
        themes_menu = self.menu_bar.addMenu("Thèmes")

        # Ouvrir image
        self.load_button_action = file_menu.addAction("Charger des images FIT")
        self.load_button_action.triggered.connect(self.load_images)

        # Fermer les images
        self.close_button_action = file_menu.addAction("Fermer les images")
        self.close_button_action.triggered.connect(self.close_images)

        # Télécharger une image
        self.download_button_action = file_menu.addAction("Télécharger l'image")
        self.download_button_action.triggered.connect(self.download_image)

        # Thèmes
        self.load_button_action = themes_menu.addAction("Adaptic.qss")
        self.load_button_action = themes_menu.addAction("Darkeum.qss")
        self.load_button_action = themes_menu.addAction("Hookmark.qss")
        self.load_button_action = themes_menu.addAction("Takezo.qss")
        self.load_button_action = themes_menu.addAction("Combinear.qss")
        self.load_button_action = themes_menu.addAction("Diffnes.qss")
        self.load_button_action = themes_menu.addAction("Irrorater.qss")

        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Section gauche pour les images individuelles
        left_layout = QVBoxLayout()
        left_layout.setSpacing(5)

        self.image_canvases = []
        for _ in range(3):  # Un canvas pour chaque canal
            canvas = FigureCanvas()
            canvas.setFixedSize(300, 200)
            self.image_canvases.append(canvas)
            left_layout.addWidget(canvas)
        main_layout.addLayout(left_layout)

        # Section droite pour l'image combinée et les curseurs
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Image combinée
        self.combined_canvas = FigureCanvas()
        self.combined_canvas.setFixedHeight(500)  # Plus grande hauteur pour l'image
        right_layout.addWidget(self.combined_canvas, stretch=4)

        # GroupBox pour les curseurs
        sliders_groupbox = QGroupBox("Ajuster les intensités RGB")
        sliders_layout = QHBoxLayout()
        self.sliders = {}
        for color in ['Rouge', 'Vert', 'Bleu']:
            slider_box = QVBoxLayout()
            label = QLabel(color)
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(50)  # Minimum 0.5
            slider.setMaximum(200)  # Maximum 2.0
            slider.setValue(100)  # Valeur par défaut 1.0
            slider.sliderReleased.connect(self.update_combined_image)  # Mise à jour après relâchement
            slider_box.addWidget(label)
            slider_box.addWidget(slider)
            sliders_layout.addLayout(slider_box)
            self.sliders[color] = slider
        sliders_groupbox.setLayout(sliders_layout)
        right_layout.addWidget(sliders_groupbox, stretch=1)

        main_layout.addLayout(right_layout)

        # Données des images
        self.image_data_list = []

    def load_images(self):
        """Charge les fichiers FITS et affiche les canaux individuels et l'image RGB combinée."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Sélectionnez des fichiers FITS", "", "FITS Files (*.fit *.fits)"
        )

        if len(file_paths) != 3:
            print("Veuillez sélectionner exactement 3 fichiers FITS (Rouge, Vert, Bleu).")
            return

        # Charger et normaliser les données FITS
        self.image_data_list = []
        for file_path in file_paths:
            data = self.load_and_normalize_fits(file_path)
            if data is not None:
                self.image_data_list.append(data)

        if len(self.image_data_list) == 3:
            print("Fichiers FITS chargés avec succès.")
            self.update_individual_images()
            self.update_combined_image()

    def load_and_normalize_fits(self, file_path):
        """Charge un fichier FITS et le normalise."""
        try:
            with fits.open(file_path) as hdul:
                data = hdul[0].data
                vmin, vmax = np.percentile(data, (1, 99))  # Contraste basé sur les percentiles
                return np.clip((data - vmin) / (vmax - vmin), 0, 1)
        except Exception as e:
            print(f"Erreur lors du chargement du fichier FITS {file_path}: {e}")
            return None

    def update_individual_images(self):
        """Affiche les canaux individuels dans les canvases."""
        for i, canvas in enumerate(self.image_canvases):
            if i < len(self.image_data_list):
                canvas.figure.clear()
                ax = canvas.figure.add_subplot(111)
                ax.imshow(self.image_data_list[i], origin="lower", cmap="gray")
                ax.set_title(f"Canal {['Rouge', 'Vert', 'Bleu'][i]}")
                ax.axis("off")
                canvas.draw()

    def update_combined_image(self):
        """Crée et affiche l'image RGB combinée."""
        if len(self.image_data_list) == 3:
            factors = (
                self.sliders['Rouge'].value() / 100.0,
                self.sliders['Vert'].value() / 100.0,
                self.sliders['Bleu'].value() / 100.0,
            )
            rgb_image = self.create_rgb_image(
                self.image_data_list[0],  # Rouge
                self.image_data_list[1],  # Vert
                self.image_data_list[2],  # Bleu
                factors=factors
            )
            self.display_combined_image(rgb_image)

    def create_rgb_image(self, red, green, blue, factors=(1.0, 1.0, 1.0)):
        """Crée une image RGB à partir des données normalisées."""
        rgb = np.zeros((red.shape[0], red.shape[1], 3))
        rgb[:, :, 0] = red * factors[0]
        rgb[:, :, 1] = green * factors[1]
        rgb[:, :, 2] = blue * factors[2]
        return np.clip(rgb, 0, 1)

    def display_combined_image(self, combined_image):
        """Affiche l'image RGB combinée."""
        self.combined_canvas.figure.clear()
        ax = self.combined_canvas.figure.add_subplot(111)
        ax.imshow(combined_image, origin="lower")
        ax.set_title("Image RGB combinée")
        ax.axis("off")
        self.combined_canvas.draw()

    def close_images(self):
        """Réinitialise les images et rétablit l'interface."""
        self.image_data_list = []
        for canvas in self.image_canvases:
            canvas.figure.clear()
            canvas.draw()
        self.combined_canvas.figure.clear()
        self.combined_canvas.draw()

    def download_image(self):
        """Télécharge les images FITS (R, G, B) à partir du nom de l'astre."""
        # Demander à l'utilisateur le nom de l'astre via une boîte de dialogue
        object_name, ok = QInputDialog.getText(self, "Nom de l'astre", "Entrez le nom de l'astre :")
        
        if ok and object_name:
            try:
                # Utilisation de SIMBAD pour obtenir les coordonnées de l'objet
                simbad = Simbad()
                simbad.TIMEOUT = 500  # Augmenter le délai d'attente si nécessaire
                result = simbad.query_object(object_name)
                
                if result is None:
                    print(f"L'objet '{object_name}' n'a pas été trouvé dans la base de données SIMBAD.")
                    return
                
                # Extraire les coordonnées RA et Dec depuis le résultat
                ra = result['RA'][0]  # Coordonnée RA
                dec = result['DEC'][0]  # Coordonnée Dec
                
                # Convertir les coordonnées RA et Dec en un objet SkyCoord
                coord = SkyCoord(ra=ra, dec=dec, unit=(u.hourangle, u.deg), frame='icrs')
                
                print(f"Coordonnées de l'objet {object_name} : RA = {ra}, Dec = {dec}")

                # Créer une instance de SkyView pour obtenir les images
                skyview = SkyView()

                # Lister les surveys disponibles
                available_surveys = skyview.list_surveys()
                print("Surveys disponibles:", available_surveys)

                # Liste des relevés spécifiques pour chaque canal RGB
                surveys = ['DSS2 Blue', 'DSS2 Green', 'DSS2 Red']  # Les relevés DSS2 par défaut pour RGB

                # Liste pour stocker les images téléchargées
                images = []

                # Télécharger les images pour chaque survey
                for survey in surveys:
                    if survey not in available_surveys:
                        print(f"Le relevé {survey} n'est pas disponible. Vous pouvez essayer un autre survey.")
                        continue  # Passer au survey suivant si celui-ci n'est pas disponible
                    try:
                        # Demander l'image depuis SkyView avec les coordonnées spécifiées
                        image = skyview.get_images(position=coord, survey=survey, pixels=(800, 800))
                        images.append(image[0])  # Ajouter la première image de la liste à la variable images
                        print(f"Image pour {survey} téléchargée avec succès.")
                    except Exception as e:
                        print(f"Erreur lors du téléchargement de l'image pour le relevé {survey}: {e}")

                # Sauvegarder les images FITS téléchargées sous des noms différents
                for i, image in enumerate(images):
                    filename = f"{object_name}_{surveys[i]}.fits"
                    image.writeto(filename, overwrite=True)
                    print(f"Fichier FITS {filename} sauvegardé.")

                print("Téléchargement et sauvegarde des fichiers FITS réussis.")

                # Vous pouvez ensuite mettre à jour les images dans l'interface si nécessaire
                self.update_individual_images()  # Afficher les canaux individuels dans l'interface
                self.update_combined_image()    # Afficher l'image combinée RGB

            except Exception as e:
                print(f"Erreur lors du téléchargement de l'image: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = AstroApp()
    viewer.show()
    sys.exit(app.exec())
