import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.visualization import LogStretch, MinMaxInterval
from astropy.visualization.mpl_normalize import ImageNormalize

def afficher_image_fits(nom_fichier):
    """
    Charge et affiche une image FITS avec ajustement d'échelle et options de contraste.

    :param nom_fichier: Chemin vers le fichier FITS
    """
    # Charger le fichier FITS
    try:
        hdul = fits.open(nom_fichier)
        hdul.info()

        # Récupérer les données et le header de la première extension
        data = hdul[0].data
        header = hdul[0].header
    except Exception as e:
        print(f"Erreur lors du chargement du fichier FITS : {e}")
        return

    # Vérifier les dimensions et les valeurs des données
    print(f"Dimensions de l'image : {data.shape}")
    print(f"Valeur min : {np.min(data)}, Valeur max : {np.max(data)}")

    # Traitement des données : gérer les valeurs infinies et NaN
    data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)

    # Afficher l'image avec différents contrastes
    plt.figure(figsize=(14, 6))

    # 1. Affichage brut
    plt.subplot(1, 3, 1)
    plt.imshow(data, cmap='gray', origin='lower')
    plt.colorbar(label='Intensité')
    plt.title("Affichage brut")

    # 2. Contraste ajusté avec percentiles
    plt.subplot(1, 3, 2)
    vmin, vmax = np.percentile(data, 1), np.percentile(data, 99)
    plt.imshow(data, cmap='gray', origin='lower', vmin=vmin, vmax=vmax)
    plt.colorbar(label='Intensité')
    plt.title("Contraste ajusté (1%-99%)")

    # 3. Échelle logarithmique
    plt.subplot(1, 3, 3)
    norm = ImageNormalize(data, interval=MinMaxInterval(), stretch=LogStretch())
    plt.imshow(data, cmap='gray', origin='lower', norm=norm)
    plt.colorbar(label='Intensité (log)')
    plt.title("Échelle logarithmique")

    plt.tight_layout()
    plt.show()

    # Afficher quelques informations du header
    print("\nInformations du header (10 premières lignes) :")
    print(repr(header)[:500])  # Imprime les premières lignes du header

    # Exemple : lire une information spécifique du header
    objet = header.get('OBJECT', 'Inconnu')
    print(f"Objet observé : {objet}")

if __name__ == "__main__":
    # Chemin vers ton fichier FITS
    fichier_fits = "../Tarantula-20241216/Tarantula/Tarantula_Nebula-oiii.fit"  # Remplace par le nom de ton fichier
    afficher_image_fits(fichier_fits)
