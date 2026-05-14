# Explication : Fonctionnement de `select` avec un timeout de 0

Voici une explication sur la façon dont la capture des touches fonctionne pendant l'animation, même sans bloquer le programme avec un temps d'attente (timeout à 0).

Quand on appelle `select.select` avec un timeout de `0`, cela signifie **"vérifie l'entrée standard instantanément et n'attends pas"**. 

Voici comment le programme réussit à capturer les touches malgré ce timeout de 0 :

1. **Le Buffer (mémoire tampon) du système :** 
   Quand on appuie sur une touche du clavier (même pendant que le programme fait un `time.sleep` ou dessine le labyrinthe), la touche n'est pas perdue. Le système d'exploitation la stocke dans une petite salle d'attente appelée "buffer" liée à l'entrée standard (`sys.stdin`).

2. **La vérification éclair :** 
   À chaque image de l'animation (à chaque tour de boucle), le programme appelle `_get_key_or_timeout(0.0)`.

3. **Le rôle de select :** 
   `select` va jeter un coup d'œil très rapide dans ce fameux buffer.
   * S'il est vide (aucune touche n'a été pressée), il rend la main tout de suite et l'animation continue de façon fluide, sans marquer de pause.
   * S'il y a une touche en attente dans le buffer (parce qu'elle a été pressée pendant le `time.sleep` précédent par exemple), `select` la voit. Il signale que `sys.stdin` est prêt, et `sys.stdin.read(1)` récupère la fameuse touche pour changer la couleur ou la vitesse.

**En résumé :** 
Le programme ne passe pas son temps à "attendre" le joueur. Cependant, comme la boucle d'animation tourne très vite et qu'elle "vérifie" à chaque tour, toute touche gardée en réserve par l'ordinateur sera récupérée dès le premier passage de la boucle (polling non bloquant) !
