import pyxel
import random
import time

# taille de la fenetre 160x120 pixels
# ne pas modifier

window = [192, 108]

pyxel.init(window[0], window[1], title="Wag le wagonnet") # 128; 72

# position initiale du wagonnet
# (origine des positions : coin haut gauche)
gameplay = {"niveau": 1, "gameover": False, "score": 0, "vies": 3, "collected": [], "started": False, "scored": False, "ScoreElapsed": 0, "SpawnElapsed": 0, "TimeElapsed": time.time() + 5, "TimeStart": 0, "BestNiveau": 0, "BestScore": 0, "powers": {}} 

wagonnet = {"x": window[0] / 2 - 8, "y":window[1] - 24 , "width":24, "height":24, "speed": 2}

power_ups = {
    "Shield": {"Cost": 10, "Duration": 5, "Position": [2,30,0, 24, 8, 8, 8] }, # le boulcier permet au jouer d'être résistant au bombes pendant une durée spécifié 
    "SpeedBoost": {"Cost": 20, "Duration": 3, "Position": [2,40,0,24,16, 8, 8] }, # le speed boost permet au joueur de se déplacer plus vite pendant une durée spécifié
    "BonusLife": {"Cost": 30, "Position": [2,50,0,24,0, 8, 8] }, # la vie bonus permet au joueur de gagner une vie chaque fois que le power up est utilisé
    "TimeSlow": {"Cost": 40, "Duration": 20, "Position": [2,60,0,24,24, 8, 8] }, # le time slow permet au joueur de ralentir le temps que les ressources mettent à tomber pendant une durée spécifié
}

spawned_ressources = [] # liste des ressources qui ont déjà été spawnées

ressources = {
    "coal": { "points": 1, "niveau":1, "texture": [0,24, 8, 8] },
    "iron": { "points": 2, "niveau":2, "texture": [8,24, 8, 8] },
    "gold": { "points": 3, "niveau":4, "texture": [16,24, 8, 8]},
    "bomb": { "points": 0, "niveau":5, "texture": [24,32, 8, 8]},
    "diamond": { "points": 4, "niveau":6, "texture": [0,32, 8, 8]},
    "ruby": { "points": 5, "niveau":8, "texture": [8,32, 8, 8]},
    "sapphire": { "points": 6, "niveau":10, "texture": [16,32, 8, 8]},
    "emerald": { "points": 7, "niveau":12, "texture": [16,40, 8, 8]},         
    "topaz": { "points": 8, "niveau":15, "texture": [0,40, 8, 8]},
    "amethyst": { "points": 9, "niveau":20,  "texture": [8,40, 8, 8]},
    "aquamarine": { "points": 10, "niveau":26, "texture": [24,40, 8, 8]}
    }

def wagonnet_deplacement(x, width, speed):
    ### déplacement avec les touches de directions ###

    # logique pour avancer vers la droite
    if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
        if (x < window[0] - width) :# verifier si le wagonnet ne dépasse pas le bord droit de l'écran
            x = x + speed # avancer vers la droite en fonction de la vitesse

    # logique pour avancer vers la gauche
    if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_Q): 
        if (x > 0) : # verifier si le wagonnet ne dépasse pas le bord gauche de l'écran
            x = x - speed # avancer vers la gauche en fonction de la vitesse
    return x

def get_ressource(ressources, niveau):
 
    chosen_ressource = [] # liste des ressources qui ont un niveau inférieur ou égal à celui du niveau actuel (elle est vide au début)

    # parcourt toutes les ressources
    for ressource, ressourceData in ressources.items():
        if ressourceData["niveau"] <= niveau: # si la ressource a un niveau inférieur ou égal à celui du niveau actuel...
            chosen_ressource.append(ressource) # ... elle sera ajouté dans la liste de "chosen_ressource"
    return random.choice(chosen_ressource)  # renvoie la liste de ressource choisie aléatoirement

def spawn_ball(ressources, niveau, spawnElapsed, powers):

    spawn_rate = max(2.5 -  0.3 * niveau, 0.9)   # le spawn_time est défini en fonction du niveau actuel (plus le niveau est grand, plus le spawn_rate diminue) Pour chaque niveau: soit -0.09 de valuer initiale
    speed = min(0.5 + 0.05 * niveau, 1) # la vitesse des ressources est défini en fonction du niveau actuel Pour chaque niveau: soit +0.05 de valuer initiale

    if "TimeSlow" in powers: # vérifie si le "power up" "TimeSlow" est activé, 
        speed = max(0.1, speed / 2) # ralentir la vitesse des balles  
        spawn_rate = min(spawn_rate *2, 2.5) # augmenter le spawn_rate

    if time.time() - spawnElapsed > spawn_rate: # vérifie si le temps écoulé est supérieur au spawn_time

        random_ore = get_ressource(ressources, niveau) # choisit une ressource aléatoire en fonction du niveau actuel
        spawned_ressources.append({"name": random_ore, "position_x": random.randint(26, 138), "position_y": 0, "points": ressources[random_ore]["points"], "speed": speed, "texture": ressources[random_ore]["texture"]}) # joute la ressource dans la table de resources

        return time.time() 
 

def collisions(spawned_ressources, wagonnet, window):
    if len(spawned_ressources) > 0:
        
        for ressource in spawned_ressources:
            if ressource["position_y"] + 8 <= window[1]: 
                ressource["position_y"] += ressource["speed"] # déplacement de la ressource vers le bas en fonction de son speed

                # detection de collision entre le wagonnet et une balle
                if wagonnet["x"] + wagonnet["width"] > ressource["position_x"] and wagonnet["x"] < ressource["position_x"] + 8  and (wagonnet["y"]  - wagonnet["height"]/2) + 8 < ressource["position_y"]  and (wagonnet["y"] - wagonnet["height"] /2) + 8 > ressource["position_y"]  - 3   :
                    
                    print("Récolte de la ressource", ressource["name"])
                    spawned_ressources.remove(ressource) # supprime la balle de la liste 
                    return True, ressource["name"], False

            else:
                spawned_ressources.remove(ressource) # supprime la balle de la liste lorsque la balle a dépassé le bas de l'écran
                return False, ressource["name"], True
        return False, None, False
    else:
        return False, None, False

def increase_difficulty(gameplay):

    duration =  max(5 + 1.5 * gameplay["niveau"], 5)  # définir la durée en fonction du niveau actuel (plus le niveau est grand, plus la durée est grande) Pour chaque niveau: soit +1.5 de valuer initiale

    if time.time() - gameplay["TimeElapsed"] > duration: # verifier si le temps écoulé depasse la durée spécifiée
        gameplay["niveau"] += 1 # augmenter le niveau de 1
        
        return time.time()
    return False

# =========================================================
# == UPDATE
# =========================================================

def determine_highest_score(gameplay):
  
    ### Déterminer le meilleur niveau###
    if not gameplay["BestNiveau"] or gameplay["BestNiveau"] < gameplay["niveau"]:  # si le meilleur niveau n'est pas encore défini ou si le meilleur niveau est inférieur au niveau actuel...
        gameplay["BestNiveau"] = gameplay["niveau"] # ...le meilleur niveau est égal au niveau actuel
        print("Nouveau record du meilleur niveau :", gameplay["BestNiveau"])
  
    ### Déterminer le meilleur score ###
    if not gameplay["BestScore"] or gameplay["BestScore"] < gameplay["score"]: # si le meilleur score n'est pas encore défini ou si le meilleur score est inférieur au score actuel...
        gameplay["BestScore"] = gameplay["score"] # ...le meilleur score est égal au score actuel
        print("Nouveau record du meilleur score :", gameplay["BestScore"])
    
    gameplay['TimeStart'] = time.time() - gameplay['TimeStart']


def power_up_click(power_ups):
    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT): # verifier si le click gauche est activé
        mouse_x, mouse_y = pyxel.mouse_x , pyxel.mouse_y # définir la position x et y du click
       
        for nom, data in power_ups.items(): # looper dans toutes le data des power ups
            pos_x, pos_y = data["Position"][0], data["Position"][1] # définir la position x et y du power up

            if pos_x <= mouse_x <= pos_x + 8 and pos_y <= mouse_y <= pos_y + 8: # si la position du click est dans la zone du power up...
                return nom # ...retourner le nom du power up
    return None 

def activer_power_up(power_up, gameplay,wagonnet): # activer le "power up"

    if power_up not in gameplay["powers"] and gameplay["score"] >= power_ups[power_up]["Cost"]: # si le "power up" n'est pas déjà activé et si le score est suffisant pour activer le "power up"
        gameplay["score"] -= power_ups[power_up]["Cost"] # soustraire coût du score

        # ajouter le "power up" à la liste des "powers" activés (pour que le même power up ne puisse pas être activé plusieurs fois en même temps):
        if "Duration" in power_ups[power_up]:
            gameplay["powers"][power_up] = time.time() # ajouter le "power up" à la liste des "powers" que le jouer a activés

        if power_up == "BonusLife":
            gameplay["vies"] += 1 # ajouter une vie
        elif power_up == "SpeedBoost":
            if "SpeedInitial" not in wagonnet: # verifier si la vitesse initial n'est pas déjà enregistré
                wagonnet["SpeedInitial"] = wagonnet["speed"] # enregistrer la vitesse initial pour pouvoir la réinitialiser après 
            wagonnet["speed"] = 3 # nouvelle vitesse

def verifier_duré_power_up(gameplay, power_ups, wagonnet):
    if len(gameplay["powers"]) > 0:
        power_ups_à_enlever = [] # liste des "power ups" à enlever

        for power_up, temps in gameplay["powers"].items():
            if "Duration" in power_ups[power_up]: # verifier si la duration du "power up" est définit
                if time.time() - temps >= power_ups[power_up]["Duration"]: # verifier si la duration du "power up" est écoulé 
                    if power_up == "SpeedBoost": # si le "power up" "SpeedBoost" est terminé...
                        wagonnet["speed"] = wagonnet["SpeedInitial"] or 2 # ...la vitesse du wagonnet est réinitialisé

                    power_ups_à_enlever.append(power_up) # ajouter les power ups dans une nouvelle liste pour les enlver apres (je pas pu le faire directement car cela baggait)

        ### Enlever les "power ups" de la liste des "powers" activés ###
        for power_up in power_ups_à_enlever: 
            gameplay["powers"].pop(power_up) # enlever le "power up" de la liste 
    
def set_game_over(gameplay):
    gameplay["gameover"] = True # définir la partie comme terminée
    determine_highest_score(gameplay) # déterminer le meilleur score
    print("Game Over!")

def check_collision(collected, ore, touched_ground, gameplay):
    if touched_ground == True and ore and ore != "bomb" :
            gameplay["vies"] = max(gameplay["vies"] - 1, 0) # si une balle touche le sol, on diminue le nombre de vies de 1
            if gameplay["vies"] == 0: # vérifier si le nombre de vies est égal à 0
                set_game_over(gameplay) # finir la partie si la condition est vraie

    if collected == True and ore and ore != "bomb": # si une ressource est collectée et que ce n'est pas une bombe...
            gameplay["score"] += ressources[ore]["points"] # ajouter le nombre de points selon la ressource au score du joueur
            gameplay["collected"].append(ore) # ajouter la ressource à la liste des ressources collectées
            gameplay["scored"] = True # marquer un point

    elif collected == True and ore == "bomb" and not "Shield" in gameplay["powers"]: # si une bombe est collectée et que le "power up" "Shield" n'est pas activé...
            
            gameplay["vies"] = max(gameplay["vies"] - 1, 0) # enlver une vie du joueur
            if gameplay["vies"] == 0: # vérifier si le nombre de vies est égal à 0
                set_game_over(gameplay) # finir la partie si la condition est vraie


def restart_game(gameplay, wagonnet):
    ### Reinitialisation des variables nécessaires pour relancer la partie ###
    gameplay["started"] = False
    gameplay["gameover"] = False
    gameplay["score"] = 0
    gameplay["collected"] = []
    gameplay["scored"] = False
    gameplay["vies"] =  gameplay["ViesInitiales"]
    gameplay["niveau"] = 1
    gameplay["TimeStart"] = time.time()
    gameplay["TimeElapsed"] = time.time() + 5
    wagonnet["x"] = 64
    


def update():
    """mise à jour des variables (30 fois par seconde)"""

    global wagonnet, gameplay, ressources, spawned_ressources, window

    if gameplay["gameover"] == False and gameplay["started"] == True : # condition: si la partie n'est pas finie
        wagonnet["x"] = wagonnet_deplacement(wagonnet["x"], wagonnet["width"], wagonnet["speed"])

        
        power_up = power_up_click(power_ups) # cette fonction détecte la position et les clicks de souris
        if power_up:
            activer_power_up(power_up, gameplay, wagonnet)  # activer le "power up"
        verifier_duré_power_up(gameplay, power_ups, wagonnet) # vérifier la durée du "power up"

        ### faire apparaitre des ressources aléatoirement ###
        spawnElapsed = spawn_ball(ressources, gameplay["niveau"], gameplay["SpawnElapsed"], gameplay["powers"]) # faire apparaitre des ressources aléatoirement
        if spawnElapsed != None:  
            gameplay["SpawnElapsed"] = spawnElapsed # mise à jour du temps écoulé de temps pour spawn de ressource 

        ### mise en jour les positions des balles et détection si une balle touche le sol ###
        collected, ore, touched_ground = collisions(spawned_ressources,wagonnet, window)
        check_collision(collected, ore, touched_ground, gameplay) # vérifier si une balle touche le sol ou si une balle est collectée

        ### augmentation de niveau apres un temps spécifier ###
        timeElapsed = increase_difficulty(gameplay) # augmente le niveau après un temps spécifier
        if timeElapsed!= False:
            gameplay["TimeElapsed"] = timeElapsed # mise à jour du temps écoulé de niveau

         


def start_game(gameplay, spawned_ressources): 
    gameplay["started"] = True # définir le jeu comme commencé
    gameplay["TimeStart"] = time.time() # mettre à jour le temps de début de la partie

    if "ViesInitiales" not in gameplay: # si le nombre de vies initiales n'est pas encore défini...
        gameplay["ViesInitiales"] = gameplay["vies"] # ...sauvegarde le nombre de vies initiales

    if len(spawned_ressources) > 0: # si il y a des ressources dans la liste...
        for ressource in spawned_ressources: # ...on loop dans toutes les resources
            spawned_ressources.remove(ressource) # supprimer le ressource de la list


# =========================================================
# == DRAW
# =========================================================
def draw():
    
    # vide la fenetre
    pyxel.cls(0)

    if gameplay["gameover"] == False and gameplay["started"] == True: # condition: si la partie n'est pas finie

        pyxel.blt(wagonnet["x"], wagonnet["y"], 0, 0,0, wagonnet["width"], wagonnet["height"]) # création du wagonnet 
        
        for name, data in power_ups.items():
            pyxel.blt(data["Position"][0], data["Position"][1], data["Position"][2], data["Position"][3], data["Position"][4], data["Position"][5], data["Position"][6]) # affiche le power-up sur l'écran dépuis sa donné
            color = 11 # définir la couleur initiale du texte de power up en vert
            if gameplay["score"] < data["Cost"] or name in gameplay["powers"]: # si le score est inférieur au coût du power up ou si le power up est déjà activé...
                color = 4 #... mettre à jour la couleur en tant que rouge 
            pyxel.text(data["Position"][0]  + 9, data["Position"][1], str(data["Cost"]), color) # afficher le texte du power up sur l'écran
            

        # affichage des ressources
        if len(spawned_ressources) > 0:
            for ressource in spawned_ressources:
            
                pyxel.blt(ressource["position_x"],ressource["position_y"],0,ressource["texture"][0],ressource["texture"][1],ressource["texture"][2],ressource["texture"][3])
              #  pyxel.circ(ressource["position_x"], ressource["position_y"], ressources[ressource["name"]]["rayon"], ressources[ressource["name"]]["couleur"]) # affiche le ressource sur l'écran dépuis sa donné


    elif gameplay["gameover"] == True:
        gameplay["started"] = False

       # print("Game Over!", 'stats =', {"score": gameplay['score'], "niveau": gameplay['niveau'], "time": gameplay['TimeStart'], "collected": gameplay['collected'], "Best Score": gameplay['BestScore'], "Best Level": gameplay['BestNiveau']})
        ### Affichage du gameover menu sur l'ecran ###
    
        pyxel.text(window[0] /2 -19, 8, "Game Over", 4) # affiche le message "Game Over" sur l'écran
        pyxel.text(window[0] /2 - 38 ,38, f"Meuilleur Niveau: {gameplay['BestNiveau']}", 9) # affiche le niveau meuilleur de toutes les parties
        pyxel.text(window[0] /2 - 16 ,48, f"Niveau: {str(gameplay['niveau'])}", 10)  # affiche le niveau de la dernière partie
        pyxel.text(window[0] /2 - 30, 58, f"Temps Jeu: {round(gameplay['TimeStart'])} s", 7) # affiche le temps de la partie

        pyxel.text(window[0] /2 - 38, window[1] - 20, f"Press R to Restart", 15) # affichage du texte avec une instructions pour recommencer la partie
        input =  pyxel.btnp(pyxel.KEY_R) # verifier si la touche "R" est appuyé
        if input:
            restart_game(gameplay, wagonnet) # recommencer la partie

   # gère toute la logique du score lorqsue la partie est en cours
    if gameplay["started"] == True: 

        # affichage du score
        if gameplay["scored"] == True: # si un nouveau point est marqué...
            pyxel.text(4,5, str(gameplay["score"]), 11) # ...émet le score en vert lorsque 
            if time.time() - gameplay["ScoreElapsed"] > 0.4: # on attend 0.4 secondes...
                gameplay["scored"] = False #...pour que le score redevienne blanc on met gameplay["scored"] = False
                
        else:
            pyxel.text(4,5, str(gameplay["score"]), 7) #affiche le score en blanc 
            gameplay["ScoreElapsed"] = time.time() # mise à jour de temps écoulé
            
        # définition de niveau et score en string dans une variable : 
        niveau_string = f"niveau: {str(gameplay['niveau'])}" # définit le variable niveau
        vies_string = f"vies: {str(gameplay['vies'])}" # définit le variable vies
        # affichage de niveau et vies :
        pyxel.text(window[0] - 20 - len(niveau_string) * 2.1,5, niveau_string , 15) # affiche le niveau et calcule sa position 
        pyxel.text(window[0] - 20 - len(vies_string) * 2.1,13, vies_string , 4) # affiche le vies et calcule sa position

    elif gameplay["started"] == False and gameplay["gameover"] == False:
        pyxel.text(window[0] /4 -5, 34, "Appuyez sur SPACE pour jouer", 15) # affiche un message d'information pour commencer la partie
        input = pyxel.btnp(pyxel.KEY_SPACE) # "attend" pour que jouer appui sur la touche "espace"
        if input:
            start_game(gameplay, spawned_ressources)
            

pyxel.load("wagon.pyxres") # charge le sprite de wagon 
pyxel.mouse(True) # active la souris
pyxel.run(update, draw) 