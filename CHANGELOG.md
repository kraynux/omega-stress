# Changelog

Format inspiré de [Keep a Changelog](https://keepachangelog.com/).

## [1.6.0] — non publiée (2026-11-09)

### Ajouté

- **Aide → « Contact et support »** (repris d'omega-serv et d'omega-log), depuis l'aide (touche `a`) :
  payer un café (page PayPal), contacter le support (mail et formulaire de contact du site, affichés en
  clair ; aucun formulaire dans l'outil, aucun mail envoyé), se déclarer utilisateur anonyme, vérifier les
  mises à jour. Sans session graphique (SSH), l'adresse s'affiche au lieu d'ouvrir le navigateur.
- **Déclaration anonyme, une seule fois** (omega-stress n'a pas de service qui enverrait chaque jour) : clé
  tirée au hasard, nom et version de l'outil, continent et pays facultatifs (listes fermées, jamais de
  texte libre) ; le message exact est affiché avant l'envoi. Rien n'est enregistré si la réception est
  injoignable. « Ne plus me déclarer » supprime l'entrée à la réception et la clé locale
  (`var/declaration.json`, jamais livrée dans l'archive).
- **Vérifier les mises à jour** : compare la version installée à la liste publiée sur le site
  (`download/sha.txt`), seulement sur clic ; « Voir les nouveautés » ouvre le fichier de la dernière
  version.
- README ×17 : section « Contact et support ».
- README ×17 : captures A-D (accueil, menu, détail d'un run, historique) dans chaque langue ; site en 17 langues (index et readme.html).

### Modifié

- Écrans « Contact et support » et « Se déclarer » partagés dans omega-lib, avec leurs traductions
  (17 langues) : le même écran dans tous les outils omega.

### Corrigé

- **Débit mesuré honnête** : le débit observé (runs et calibrage) est maintenant divisé par la durée
  **réelle** de chaque seconde de mesure. Avant, il valait toujours le débit demandé : quand le générateur
  ne suivait pas (une « seconde » qui dure 1,6 s), le décrochage restait invisible dans les écrans, les
  rapports et l'enveloppe de calibrage. La progression du run reste en temps logique (inchangé).
- **Test connexions : nombre en parallèle réel** : le générateur garde au plus 200 requêtes en vol (garde-fou
  du 2026-09-01 contre le gel de l'interface). Le tableau de référence et les échantillons enregistrés
  affichent désormais ce nombre réel, et non le niveau annoncé (jusqu'à 5000).
- Réglages : l'écran est centré comme dans le reste de la suite (le bloc « Langue / Language » prenait
  toute la largeur et repoussait tout à gauche).
- Réglages : plus de notification à l'ouverture de l'écran (« Comme l'interface », profil de rendu) ;
  seul un vrai changement est enregistré et annoncé.
- Langues : les 16 traductions sont validées, la mention « en test » disparaît du sélecteur.

## [1.5.0] — 2026-10-29

### Ajouté

- Interface en 17 langues (français, anglais, espagnol, portugais (Brésil), italien, allemand, néerlandais, polonais, russe, chinois simplifié, vietnamien, thaï, indonésien, japonais, coréen, hindi et arabe) : Réglages → « Langue / Language », appliquée après un redémarrage de l'interface ; variable `OMEGA_STRESS_LANG` pour forcer une langue le temps d'une session. Lancé depuis omega-suite, l'outil prend la langue de la suite.
- Réglage « Langue des exports » (« Comme l'interface » par défaut) : les rapports HTML et texte s'écrivent dans la langue choisie ; en arabe, le rapport HTML se lit de droite à gauche. Les exports JSON et CSV restent des données (clés et valeurs inchangées).

### Modifié

- Accents rétablis dans tous les textes français de l'interface et des rapports.
- Les résultats enregistrés en français sont retraduits à l'affichage et dans les exports.
- La ligne de commande reste en français.
