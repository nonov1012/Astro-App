from astroquery.skyview import SkyView
from astropy.coordinates import SkyCoord
import astropy.units as u
from astroquery.simbad import Simbad

# Demander à l'utilisateur d'entrer le nom de l'objet céleste
object_name = input("Entrez le nom de l'objet céleste (par exemple 'Orion') : ")

# Utilisation de SIMBAD pour obtenir les coordonnées de l'objet
simbad = Simbad()
simbad.TIMEOUT = 500  # Augmenter le délai d'attente si nécessaire

# Récupérer les informations de l'objet à partir de SIMBAD
result = simbad.query_object(object_name)

if result is None:
    print(f"L'objet '{object_name}' n'a pas été trouvé dans la base de données SIMBAD.")
else:
    # Extraire les coordonnées RA et Dec depuis le résultat
    ra = result['RA'][0]  # Coordonnée RA
    dec = result['DEC'][0]  # Coordonnée Dec
    
    # Convertir les coordonnées RA et Dec en un objet SkyCoord
    coord = SkyCoord(ra=ra, dec=dec, unit=(u.hourangle, u.deg), frame='icrs')
    
    print(f"Coordonnées de l'objet {object_name} : RA = {ra}, Dec = {dec}")

    # Créer une instance de SkyView pour obtenir les images
    skyview = SkyView()

    # Liste des relevés fixes
    surveys = ['DSS2 Blue', 'DSS2 Red', 'DSS2 IR']  # Les relevés par défaut

    # Liste pour stocker les images téléchargées
    images = []

    # Télécharger les images pour chaque survey
    for survey in surveys:
        try:
            # Demander l'image depuis SkyView avec les coordonnées spécifiées
            image = skyview.get_images(position=coord, survey=survey, pixels=(800, 800))
            images.append(image[0])  # Ajouter la première image de la liste à la variable images
            print(f"Image pour {survey} téléchargée avec succès.")
        except Exception as e:
            print(f"Erreur lors du téléchargement de l'image pour le relevé {survey}: {e}")

    # Sauvegarder les images FITS téléchargées sous des noms différents
    for i, image in enumerate(images):
        image.writeto(f'image_{surveys[i]}.fits', overwrite=True)
        print(f"Fichier FITS {surveys[i]} sauvegardé.")

    print("Téléchargement et sauvegarde des fichiers FITS réussis.")
