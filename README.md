# Visualisation d'Images Astronomiques FITS avec Python

Ce projet permet de charger, traiter et visualiser des images astronomiques FITS provenant de différentes bandes spectrales (Hα, [O III], [S II]). Il inclut une interface interactive pour ajuster des paramètres tels que le gamma et explorer les détails des images.

---

## 🪐 **Fonctionnalités**
- Chargement et normalisation des fichiers FITS.
- Visualisation des images Hα, [O III], [S II] en niveaux de gris.
- Génération d'une image RGB combinée.
- Ajustement interactif des paramètres de gamma pour chaque canal avec des sliders.

---

## 🛠️ **Prérequis**

### Logiciels et Librairies nécessaires :
- Python 3.8+
- `numpy` : Manipulation des tableaux de données.
- `matplotlib` : Visualisation des données.
- `astropy` : Lecture et manipulation des fichiers FITS.
- `astroquery` : Téléchargement de photo astronomique.

### Installation des dépendances :
Exécutez la commande suivante pour installer toutes les bibliothèques nécessaires :
```bash
pip install numpy matplotlib astropy astroquery
```
---

## ▶️ Comment exécuter le projet ?

```bash
python visualisation_fits.py
```

Une fois l'application lancé, vous pouvez soit ouvrir des fichiers FTIS déjà télécharger ou alors en télécharger directement depuis l'appli.

---

## 🧑‍💻 Crédit 

- VOTURIER Noa
- NOËL Clément

## 📄 Licence

Ce projet est sous licence MIT. Vous pouvez l'utiliser librement à condition de mentionner l'auteur.