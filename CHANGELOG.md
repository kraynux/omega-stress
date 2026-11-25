# Changelog

Format inspiré de [Keep a Changelog](https://keepachangelog.com/).

## [2.0.0] — construite le 2026-11-21, reconstruite le 2026-11-22 (reprend aussi le contenu de la 1.6.0)

### Ajouté

- La version affichée (accueil, en-tête, aide) est lue dans `pyproject.toml`, seule source (même source que
  « Contact et support ») : plus de copie à tenir à jour (2026-11-22).
- **omega-stress embarqué par omega-suite** (décision, 2026-11-22 : omega-stress fait partie
  d'omega-suite) : dans `<suite>/vendor/omega-stress`, `omega-stress.sh` prend le `.venv` de la suite et son
  `var/stress` (le même état que l'onglet omega-stress de la suite). omega-connect le reconnaît, le met à jour avec
  omega-suite, et il aide à la charge distribuée comme un omega-stress autonome. Autonome, rien ne change.
- **Nouveau moteur de charge en boucle ouverte, multiprocessus** (Phase 0 et Phase 1 du plan de charge
  distribuée, `STRESS/ETUDE_VERIFICATION_CODE_CHARGE_DISTRIBUEE.md` §10, 2026-11-21) :
  - l'émission ne tourne plus dans la boucle de l'interface : des processus d'émission séparés (un par part de
    la charge, au plus cœurs − 1) ; l'interface ne fait que lire leurs comptes, elle ne peut plus geler ;
  - **boucle ouverte** : chaque requête part à l'instant prévu, sans attendre les réponses précédentes ; une
    cible qui ralentit fait monter les latences au lieu d'être masquée (omission coordonnée corrigée : la
    latence est mesurée depuis l'instant prévu) ;
  - garde-fou mémoire de 5 000 requêtes en vol par processus : au-delà, la requête est comptée **« non
    émise »**, jamais retardée en silence ; une requête partie en retard sur son instant prévu est comptée
    aussi ; ces deux comptes, et non plus le débit terminé, décident de la notification « goulot local »
    (une cible qui sature n'accuse plus la machine) ;
  - **Test connexions, lecture B** : N connexions réellement ouvertes et tenues (keep-alive), chacune envoie
    une requête toutes les ~10 s, décalées ; avant, un pool partagé n'ouvrait que ce que le débit demandait ;
  - **percentiles exacts** : chaque seconde porte son histogramme de latences (précision ~1,6 %), fusionné
    pour le run entier ; avant, p95/p99 du run étaient le maximum des secondes et p50 leur moyenne ;
  - la mesure CPU/mémoire du générateur (garde de sécurité) inclut les processus d'émission.
  - **client HTTP/1.1 léger** sur des connexions réutilisées (500 au plus par processus) au lieu de httpx :
    mesure du 2026-11-21 sur 4 cœurs, ~150 req/s par processus avec httpx contre 2 000 avec ce client ;
    5 000 req/s tenues à l'heure avec 3 processus (le niveau Maximum, 833 req/s, tient sur une machine) ;
  - **calibrage sur le même moteur** : les paliers émettent avec les processus des runs, et le débit atteint
    est le débit émis À L'HEURE (la capacité de la machine) ; le serveur de boucle locale tourne dans son
    propre processus (asyncio, keep-alive) au lieu d'un fil par connexion dans celui de l'interface, qui
    s'effondrait sous la charge (30 req/s terminées pour 1 000 demandées) et faussait la mesure.

- **Charge distribuée en réseau local, sans rien taper** (parcours simple, 2026-11-21, étude
  `STRESS/ETUDE_PARCOURS_CHARGE_DISTRIBUEE_SIMPLE.md`) :
  - les machines se relient une seule fois dans **omega-connect** (Synchronisation → Charge distribuée) : accès
    transmis par SSH (secret par l'entrée standard, rien à recopier), accord choisi (« demander pour chaque
    nouvelle cible » ou « tout accepter de ce pilote »), limites pré-remplies d'après chaque machine ;
  - écrans de test : ligne **« Machines qui chargent la cible »** (absente tant que rien n'est relié) ; les
    machines qui aident sont cochées, « cette machine » ne l'est pas (elle pilote et mesure) ; omega-stress les
    démarre lui-même par SSH à chaque test et les arrête à la fin ;
  - accord « demander » : la question s'affiche pendant le test, la réponse est écrite sur la machine qui aide ;
  - écran **« Charge distribuée »** (bouton « Machines… ») : état de chaque machine et pare-feu de cette machine,
    « Ouvrir le pare-feu » / « Refermer » : omega-fire s'il est relié (`port ouvrir|fermer`), sinon ufw ou
    firewalld, seul le port d'omega-stress pour les réseaux privés de la machine ; un mot de passe sudo tapé dans
    le terminal (`sudo -v`, puis `sudo -n`), jamais de sudo sans terminal ; nftables seul sans omega-fire : rien
    n'est touché ;
  - aide F1, textes des 17 langues ; commandes `coordinateur …` / `worker …` en JSON pour omega-connect.
  - retours d'utilisation après le premier essai réel : menu principal « Charge distribuée » (sous Calibrage ;
    « Quitter » retiré du menu, touches `q` / `Échap` inchangées) : machines reliées, case « Participe » par
    machine et pour « cette machine » (choix gardé), « Supprimer la machine », compte rendu du pare-feu
    (gestionnaire, port, réseaux, qui l'a ouvert et quand, règles posées avec leur numéro chez omega-fire) ;
    écrans de test : case « Mode charge distribuée » sous « Mode sécurité », qui affiche la ligne des machines
    pré-cochée ; cases à cocher bien plus visibles partout (case pleine colorée quand cochée, vide sinon,
    libellé en gras).
  - à la fin d'un test distribué, le bilan par machine s'affiche aussi sous « Lancer » (en plus du détail du run).
- **Captures (README ×17, site)** : A (accueil 2.0.0) et B (nouveau menu) refaites ; E (écran Charge distribuée)
  et F (test en « Mode charge distribuée ») ajoutées, avec des machines de démonstration ; galerie française :
  accueil et menu remplacés, cartes 17 et 18 ajoutées.
- **Charge distribuée en réseau local, en ligne de commande** (Phase 2 du plan, 2026-11-21) : un run
  `request`, `connection` ou `ramp` lancé avec `--distribue N` répartit la charge sur N machines « workers » ;
  la machine qui lance coordonne et mesure, sans émettre. Même déroulé qu'un run local (gardes, historique,
  exports, profils D1-D6) :
  - **appairage** : `coordinateur code` donne un code à usage unique (10 min) et l'empreinte du coordinateur ;
    `worker appairer HÔTE:PORT --empreinte … --code …` sur le worker. Canal de contrôle chiffré (TLS, certificat
    auto-signé du coordinateur dont le worker épingle l'empreinte) ; le worker reçoit un secret propre, le
    coordinateur n'en garde que l'empreinte ; fichiers sous `var/distributed/` en 0600, exclus de l'archive ;
  - **autorisation du propriétaire du worker** (`worker autoriser --cible URL --debit-max N --duree-max M`) :
    cibles permises, débit, durée et connexions maximum, coordinateurs acceptés ; vérifiée par le worker à
    chaque campagne et le débit bridé chaque seconde, quoi que demande le coordinateur ;
  - **deux façons de lancer un worker** : il compose lui-même vers le coordinateur (`worker rejoindre`, aucune
    écoute sur le worker, il attend que le coordinateur démarre, puis reste disponible pour les campagnes
    suivantes, sauf avec `--une-fois`) ou le coordinateur le lance par SSH
    (`--ssh utilisateur@hôte:/chemin --annonce <adresse du coordinateur>`) ;
  - phrase exacte `--confirmation-distribuee "CHARGE DISTRIBUEE N WORKERS"` exigée pour tout run distribué ;
  - répartition proportionnelle à la capacité de chaque worker ; au-delà de leur somme, la campagne est
    refusée et le maximum annoncé ; un worker qui refuse est écarté et signalé (sa part reprise par les
    autres) ; un worker perdu en cours de route est signalé (« perdu à la seconde J ») et le run continue ;
  - histogrammes de latence fusionnés : percentiles exacts sur l'ensemble des machines.

### Corrigé

- **Charge distribuée : machine qui aide « non joignable, non reliée »** (essai réel, craftdark, 2026-11-21) : sur
  certaines machines (Archcraft), une connexion SSH sans terminal n'a presque rien dans son PATH ; le PATH standard
  ne s'appliquait qu'au `cd` qui précède le lanceur (« env: bash: No such file or directory »). Il est maintenant
  rétabli pour toute la commande (état, démarrage de la machine, accord) ; les tests imitent ce PATH presque vide.
- **Charge distribuée : liaison écrite au mauvais endroit** (essai réel, 2026-11-21) : lancées par
  omega-connect ou par SSH, les commandes `worker` et `coordinateur` rangeaient leurs fichiers dans le `var/` du
  dossier courant (celui d'omega-connect, ou le dossier personnel sur la machine qui aide) ; omega-stress ne voyait
  alors aucune machine reliée et le test restait local. Le lanceur se place toujours dans le dossier d'omega-stress,
  et le pilote lance les machines qui aident depuis le leur.
- **Bilan par machine** d'un test distribué : « X a rejoint le pilote », « Départ — machines qui chargent : … »
  pendant le test ; à la fin, requêtes émises / terminées / erreurs de chaque machine, gardé avec le run (détail du
  run, ligne dédiée ; exports).
- **Aucun test ni calibrage ne partait depuis l'interface** (moteur 2.0.0, essai réel, 2026-11-21) :
  « Erreur inattendue — ValueError: bad value(s) in fds_to_keep ». Sous Textual, la sortie d'erreur est une capture
  sans descripteur, que multiprocessing transmettait aux processus d'émission. Les vrais flux sont remis en place le
  temps du démarrage (`infrastructure/process_start.py`). La ligne de commande n'était pas touchée.
- **Connexions fermées par la cible comptées comme des erreurs** (moteur 2.0.0, trouvé le 2026-11-21 pendant
  les essais de la charge distribuée) : une connexion réutilisée que la cible avait refermée (serveur HTTP/1.0,
  ou délai d'inactivité : 5 s chez Apache, plus court que les 10 s du Test connexions) faisait échouer la
  requête suivante. Elle est maintenant rouverte et la requête renvoyée une fois.

### Modifié

- **Niveaux de débit** (décision, 2026-11-21) : Test requêtes et pics du Test charge, Haut 3 000,
  Agressif 12 000, Violent 25 000, Maximum 50 000 req/min (avant : 2 000 / 10 000 / 15 000 / 20 000). Violent
  et Maximum visent la charge distribuée à venir ; une machine seule va où elle peut, et la notification
  « goulot local » le dit. Tableau de référence : « en continu » au lieu de « en rafale ».
- **Version 2.0.0** affichée aux trois endroits de l'interface (écran d'accueil — il affichait encore « v1.5 »,
  en-tête, aide), depuis une seule constante vérifiée contre `pyproject.toml`. omega-connect : première version
  d'omega-stress à contrats = 2.0.0.

### Ajouté (suite)

- **Carte d'identité pour omega-connect** (contrats d'interconnexion, 2026-11-21) : `./omega-stress.sh synchro
  jeton` écrit `var/omega-jeton.json` (même format que les autres outils omega, omega-lib), sans bannière ni
  interface ; `install.sh` la crée. omega-connect reconnaît désormais omega-stress (lanceur ajouté à omega-lib,
  version 1.6.0 dans ses versions à contrats). Jamais écrite en root, exclue de l'archive. Première étape de la
  charge distribuée (plan `STRESS/plan-omega-stress-charge-distribué.md`) : la fiche des capacités viendra avec
  elle.
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
