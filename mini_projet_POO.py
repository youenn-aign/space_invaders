import pyxel
from csv import writer, reader
from datetime import datetime
from typing import Tuple, List, Tuple
from random import randint

fps = 50
liste_cord_monstre = [(0,24),(0,32),(8,32),(16,24),(16,32),(24,24),(24,32)] # coordonné des images de monstres

liste_nb_ennemis = 				 [   (2,2)  , (3,3)  , (4,4)  , (4,5)  , (5,6)  , (5,8)         ] # (lignes, colonnes)
liste_vitesse_ennemis = 		 [    0.4   ,  0.6   ,  0.8   ,   1    ,  1.2   ,  1.4   ,  0.8 ] # x ou y
liste_vitesse_missiles_ennemis = [    0.8   ,   1    ,  1.2   ,  1.4   ,  1.6   ,  1.8   ,  1.2 ] # x ou y
liste_temps_vague =    			 [	 (1,0)  , (1,15) , (1,30) , (1,45) , (2,0)  , (2,0)  , (3,0)] # (minutes, secondes)

#états :    neuf / peu endommagé / endommagé / bcp endommagé
cord_boss = [(117,64),(117,104),(117,144),(117,184)]

def creation_vague_ennemi(level : int) -> (List, List) :
	"""
	créé 2 listes, une avec tous les ennemis, une autre avec leur texture de monstre associé
	"""
	liste_ennemis = []
	liste_monstres = []
	
	for i in range(liste_nb_ennemis[level][0]) :
			for j in range(liste_nb_ennemis[level][1]) :
				liste_ennemis.append(Ennemi(10+j*11, 50+i*11)) # crée les ennemis
				liste_monstres.append(liste_cord_monstre[pyxel.rndi(0,len(liste_cord_monstre)-1)]) # donne la texture de monstre aux ennemis
				
	return liste_ennemis, liste_monstres

def ennemi_en_vie(liste_ennemis : List) -> bool :
	"""
	regarde si des ennemis sont toujour en vie, si ou retourne False, sinon return True
	"""
	for ennemi in liste_ennemis :
		if ennemi.en_vie :
			return False
	return True

def explosion(x : float, y : float, etat_explosion : int) -> int :
	"""
	créé un explosion au cordonné (x,y)
	"""
	if etat_explosion >= 0 :
		pyxel.blt(x, y, 0, 96 + 16*(etat_explosion//2) , 0, 16,16,0)
		if etat_explosion <= 20:
			etat_explosion += 1
	return etat_explosion

def explosion_pt_vie(x : float, y : float, etat_explosion_pt_vie : int) -> int :
	"""
	créé un explosion du point de vie perdu
	"""
	if etat_explosion_pt_vie >= 0 :
		pyxel.blt(x, y, 0, 96 + 16*(etat_explosion_pt_vie//2) , 16, 16,16,0)
		if etat_explosion_pt_vie <= 20:
			etat_explosion_pt_vie += 1
	return etat_explosion_pt_vie

def deplacement_vaisseau (vaisseau, cheat, boss):
	x , y = 0,0
	if (pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT)) and vaisseau.x < pyxel.width - vaisseau.w : # Déplacement à droite
		x += 1
		
	if (pyxel.btn(pyxel.KEY_Q) or pyxel.btn(pyxel.KEY_LEFT)) and vaisseau.x > 0 : # Déplacement à gauche
		x += -1

	if cheat or boss:
		if (pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.KEY_UP)) and vaisseau.y > 0 : # Déplacement en haut
			y += -1
					
		if (pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN)) and vaisseau.y < pyxel.height - vaisseau.h : # Déplacement en bas
			y += 1
	
	return x , y

def deplacement_ennemi (liste_des_ennemis : List, level : int, boss : bool, mouvement_precedent : str):
	if not boss :
		if liste_des_ennemis[0].x > 10 and liste_des_ennemis[0].y <= 50 : # déplacement des ennemis gauche haut
			x , y = -liste_vitesse_ennemis[level] , 0
						
		elif liste_des_ennemis[0].x <= 10 and liste_des_ennemis[-1].y < 140 - liste_des_ennemis[-1].h: # déplacement des ennemis bas gauche
			x , y = 0 , liste_vitesse_ennemis[level]
							
		elif liste_des_ennemis[-1].x < 110 - liste_des_ennemis[-1].w  and liste_des_ennemis[-1].y >= 140 - liste_des_ennemis[-1].h : # déplacement des ennemis droite bas
			x , y = liste_vitesse_ennemis[level] , 0
						
		elif liste_des_ennemis[-1].x >= 110 - liste_des_ennemis[-1].w and liste_des_ennemis[0].y > 50 : # déplacement des ennemis haut droite
			x , y = 0 , -liste_vitesse_ennemis[level]


			
	elif boss :
		
		if liste_des_ennemis[0].x > 5 and liste_des_ennemis[0].y <= 69 and mouvement_precedent == "diag_gauche_droite": # déplacement des ennemis gauche haut
			x , y = -liste_vitesse_ennemis[level] , liste_vitesse_ennemis[level]/2
						
		elif liste_des_ennemis[0].x <= 5 and liste_des_ennemis[0].y > 69 - liste_des_ennemis[0].h : # déplacement des ennemis bas gauche
			x , y = 0 , -liste_vitesse_ennemis[level]
			if liste_des_ennemis[0].y + y <= 69 - liste_des_ennemis[0].h :
				mouvement_precedent = "diag_droite_gauche"
							
		elif liste_des_ennemis[0].x < 115 - liste_des_ennemis[0].w  and liste_des_ennemis[0].y <= 69  and mouvement_precedent == "diag_droite_gauche": # déplacement des ennemis droite bas
			x , y = liste_vitesse_ennemis[level] , liste_vitesse_ennemis[level]/2
						
		elif liste_des_ennemis[0].x >= 115 - liste_des_ennemis[0].w and liste_des_ennemis[0].y > 69 - liste_des_ennemis[0].h : # déplacement des ennemis haut droite
			x , y = 0 , -liste_vitesse_ennemis[level]
			if liste_des_ennemis[0].y + y <= 69 - liste_des_ennemis[0].h :
				mouvement_precedent = "diag_gauche_droite"
		
	return x , y, mouvement_precedent

def timer(frames : int, temps : int, temps_ajoute : int) :
	"""
	fait écoulé le temps du timer d'une seconde à chaque seconde
	"""
	if frames % fps == 0 :
		temps.avance(temps_ajoute)
	return temps

def saisie_clavier() -> str:
	"""
	fonction de saisie au clavier revoyant le caractère saisi
	"""
	lettre = ""
	if pyxel.btnp(pyxel.KEY_A) :
		lettre = "a"
	elif pyxel.btnp(pyxel.KEY_B) :
		lettre = "b"
	elif pyxel.btnp(pyxel.KEY_C) :
		lettre = "c"
	elif pyxel.btnp(pyxel.KEY_D) :
		lettre = "d"
	elif pyxel.btnp(pyxel.KEY_E) :
		lettre = "e"
	elif pyxel.btnp(pyxel.KEY_F) :
		lettre = "f"
	elif pyxel.btnp(pyxel.KEY_G) :
		lettre = "g"
	elif pyxel.btnp(pyxel.KEY_H) :
		lettre = "h"
	elif pyxel.btnp(pyxel.KEY_I) :
		lettre = "i"
	elif pyxel.btnp(pyxel.KEY_J) :
		lettre = "j"
	elif pyxel.btnp(pyxel.KEY_K) :
		lettre = "k"
	elif pyxel.btnp(pyxel.KEY_L) :
		lettre = "l"
	elif pyxel.btnp(pyxel.KEY_M) :
		lettre = "m"
	elif pyxel.btnp(pyxel.KEY_N) :
		lettre = "n"
	elif pyxel.btnp(pyxel.KEY_O) :
		lettre = "o"
	elif pyxel.btnp(pyxel.KEY_P) :
		lettre = "p"
	elif pyxel.btnp(pyxel.KEY_Q) :
		lettre = "q"
	elif pyxel.btnp(pyxel.KEY_R) :
		lettre = "r"
	elif pyxel.btnp(pyxel.KEY_S) :
		lettre = "s"
	elif pyxel.btnp(pyxel.KEY_T) :
		lettre = "t"
	elif pyxel.btnp(pyxel.KEY_U) :
		lettre = "u"
	elif pyxel.btnp(pyxel.KEY_V) :
		lettre = "v"
	elif pyxel.btnp(pyxel.KEY_W) :
		lettre = "w"
	elif pyxel.btnp(pyxel.KEY_X) :
		lettre = "x"
	elif pyxel.btnp(pyxel.KEY_Y) :
		lettre = "y"
	elif pyxel.btnp(pyxel.KEY_Z) :
		lettre = "z"
		
	elif pyxel.btnp(pyxel.KEY_SPACE) :
		lettre = " "
		
	elif pyxel.btnp(pyxel.KEY_0) :
		lettre = "0"
	elif pyxel.btnp(pyxel.KEY_1) :
		lettre = "1"
	elif pyxel.btnp(pyxel.KEY_2) :
		lettre = "2"
	elif pyxel.btnp(pyxel.KEY_3) :
		lettre = "3"
	elif pyxel.btnp(pyxel.KEY_4) :
		lettre = "4"
	elif pyxel.btnp(pyxel.KEY_5) :
		lettre = "5"
	elif pyxel.btnp(pyxel.KEY_6) :
		lettre = "6"
	elif pyxel.btnp(pyxel.KEY_7) :
		lettre = "7"
	elif pyxel.btnp(pyxel.KEY_8) :
		lettre = "8"
	elif pyxel.btnp(pyxel.KEY_9) :
		lettre = "9"

	if len(lettre) != 0 :
		if (pyxel.btn(pyxel.KEY_LSHIFT) or pyxel.btn(pyxel.KEY_RSHIFT))and 97 <= ord(lettre) <= 122 :
			lettre = chr(ord(lettre)-32)
		
	return lettre

def tri_classement():
	score_joueur = []
	with open("score_space_invaders.csv", "r") as csv_file :
		csv_reader = reader(csv_file)
		for line in csv_reader :
			score_joueur.append(line)
			
		en_tete = score_joueur[0]
		
		classement = tri_insertion(score_joueur[1:])
		csv_file.close()
	return en_tete, classement
	
def tri_insertion(liste_tri : List) -> List:
	"""
	fonction tri par insertion
	"""
	for i, x in enumerate(liste_tri):
		
		while i and int(liste_tri[i-1][1]) < int(x[1]):
			liste_tri[i] = liste_tri[i-1]
			i -= 1 
		liste_tri[i] = x
	return liste_tri

class Ennemi:
	"""
	Vaisseau ennemi
	attribut :
	@x position x de l'ennemi
	@y position y de l'ennemi
	
	méthodes :
	draw -> Affichage de l'ennemi
	move -> Déplacement de l'ennemi
	blesseure -> Perte des points de vie de l'ennemi
	tir_missile -> Création des missiles ennemi
	"""
	
	def __init__(self, x : float, y : float):
		
		"""
		Caractéristiques de l'ennemi.
		"""
		self.x = x
		self.y = y
		self.h = 8
		self.w = 8
		self.en_vie = True
		self.explosion = -1
		self.energie = 1
	
	def draw(self, cord_monstre : Tuple):
		"""
		Affichage de l'ennemi
		"""
		if self.en_vie :
			pyxel.blt(self.x , self.y, 0, cord_monstre[0], cord_monstre[1], self.w, self.h, 0)

		else :
			self.explosion = explosion(self.x - 4 , self.y - 4 , self.explosion)
			
	def move(self, dx : float, dy : float):
		"""
		Déplacement de l'ennemi
		"""
		self.x += dx
		self.y += dy

	def blessure(self):
		"""
		Perte des points de vie de l'ennemi
		"""
		if self.en_vie :
			self.energie -= 1
			self.explosion_pt_vie = 0
			if self.energie <= 0:
				self.en_vie = False
				self.explosion = 0
		return self.energie

	def tir_missile(self) :
		"""
		Création des missiles ennemi
		"""
		if self.en_vie :					
			return (Missile(self.x + 3, self.y - 8, 8))

class Ship:
	"""
	Vaisseau principal
	attribut :
	@x position x du vaisseau
	@y position y du vaisseau
	
	méthodes :
	draw -> Affichage du vaisseau
	draw_pt_vie -> Affiche les points de vie
	move -> Déplacement du vaisseau
	blessure -> Perte des points de vie du vaisseau
	soin -> Soigne le vaisseau
	tir_missile -> Création des missiles 
	"""
	
	def __init__(self, x : float, y : float):
		
		"""
		Caractéristiques du vaisseau.
		"""
		self.x = x
		self.y = y
		self.h = 8
		self.w = 8
		
		self.energie = 3	
		self.en_vie = True
		self.explosion = -1
		self.explosion_pt_vie = -1
		self.compteur_attaque = 30
		
		
	def draw(self):
		"""
		Affichage du vaisseau
		"""
		if self.en_vie :
			pyxel.blt(self.x , self.y, 0, 8, 16, self.w, self.h, 0)
			
		else :
			self.explosion = explosion(self.x - 4, self.y - 4, self.explosion)
			

	def draw_pt_vie(self):
		"""
		affiche les points de vie
		"""
		for i in range(self.energie):
			pyxel.blt(115 - (self.energie-i)*10 , 9, 0, 0, 48, 8, 8, 0)

		self.explosion_pt_vie = explosion_pt_vie(115 - (self.energie + 1)*10 -4, 9 - 4, self.explosion_pt_vie)

		if self.explosion_pt_vie == 21 :
			self.explosion_pt_vien = -1
					
		
	def move(self, dx : int, dy : int):
		"""
		Déplacement du vaisseau
		"""
		if self.en_vie :
			self.x += dx
			self.y += dy
		
	def blessure(self):
		"""
		Perte des points de vie du vaisseau
		"""
		if self.en_vie :
			self.energie -= 1
			self.explosion_pt_vie = 0
			if self.energie <= 0:
				self.en_vie = False
				self.explosion = 0
		return self.energie

	def soin(self):
		"""
		Soigne le vaisseau 
		"""
		if self.en_vie : 
			self.energie += 1

	def tir_missile(self, cheat : bool) :
		"""
		Création des missiles
		"""
		self.compteur_attaque += 1  # pour réguler l'envoie de missile du joueur
							
		if pyxel.btnp(pyxel.KEY_SPACE) and self.en_vie and self.compteur_attaque > 40 and not cheat: 
			self.compteur_attaque = 0 # pour réguler l'envoie de missile du joueur
			return (Missile(self.x + 3, self.y - 8, 3))
				
		elif pyxel.btn(pyxel.KEY_SPACE) and self.en_vie and self.compteur_attaque > 2 and cheat:  # missile cheat
			self.compteur_attaque = 0 # pour réguler l'envoie de missile du joueur
			return (Missile(self.x + 3, self.y - 8, 3))

class Boss_final:
	"""
	Vaisseau du boss final
	attributs :
	@x position x du boss
	@y position y du boss
	
	méthodes :
	draw -> Affichage du boss
	move -> Déplacement du boss
	blessure -> Perte des points de vie du boss
	soin -> Soigne le boss
	barre_vie -> Affiche la barre de vie du boss
	tir_misssile -> Création des missiles
	"""
	
	def __init__(self, x : float, y : float):
		
		"""
		Caractéristiques du boss.
		"""
		self.x = x
		self.y = y
		self.h = 31
		self.w = 53
		self.en_vie = True
		self.energie = 37
		self.explosion = -1
		
		self.indice_affichage_boss = 4
	
	def draw(self):
		"""
		Affichage du boss
		"""
		
		if self.en_vie :
			pyxel.blt(self.x , self.y, 0, cord_boss[-self.indice_affichage_boss][0], cord_boss[-self.indice_affichage_boss][1], self.w, self.h, 0)
			self.barre_vie()
		else :
			self.explosion+=1
			for i in range(0,25,5) :
				explosion(self.x + 10+i , self.y - 15 , self.explosion)
				explosion(self.x + 10+i , self.y - 25 , self.explosion)
			
	def move(self, dx : float, dy : float):
		"""
		Déplacement du boss
		"""
		if self.en_vie :
			self.x += dx
			self.y += dy

	def blessure(self):
		"""
		Perte des points de vie du boss
		"""
		if self.en_vie :
			self.indice_affichage_boss = pyxel.ceil(self.energie / 10)
			self.energie -= 1
			if self.energie <= 0:
				self.en_vie = False
				self.explosion = 0

	def soin(self):
		"""
		Soigne le boss 
		"""
		if self.en_vie : 
			self.energie += 1

	def barre_vie(self) :
		"""
		Affiche la barre de vie du boss
		"""
		pyxel.blt(self.x + 7 , self.y - 5, 0, 0, 140 + 8, 39, 3, 0)
		for i in range(self.energie) :
			pyxel.pset(self.x + 8 + i, self.y - 4, 8)
			
			
	def tir_missile(self) :
		"""
		Création des missiles
		"""
		x = pyxel.rndi(1,3)
		if self.en_vie and pyxel.frame_count%2 == 0: #lanceur gauche					
			if x == 1 :
				return (Missile(self.x + 18, self.y + 31, 8))
			elif x == 2 :
				return (Missile_diago(self.x + 18, self.y + 31, 8, "d"))
			elif x == 3 :
				return (Missile_diago(self.x + 18, self.y + 31, 8, "g"))
		else : # lanceur droit
			if x == 1 :
				return (Missile(self.x + 34, self.y + 31, 8))
			elif x == 2 :
				return (Missile_diago(self.x + 34, self.y + 31, 8, "d"))
			elif x == 3 :
				return (Missile_diago(self.x + 34, self.y + 31, 8, "g"))

class Missile:
	"""
	missil envoyé
	attribut :
	@x position x du missile
	@y position y du missile
	@col couleur du missile
	
	méthodes :
	draw -> Affichage du missile
	move -> Déplacement du missile
	"""
	def __init__(self, x : float, y : float, col : int):
		
		"""
		Caractéristiques du missile
		"""
		self.col = col
		self.x = x
		self.y = y
		self.h = 6
		self.w = 2
		
	
	def draw(self):
		"""
		Affichage des missiles
		"""
		pyxel.rect(self.x, self.y, self.w, self.h, self.col)
		
	def move(self, dy : float ):
		"""
		Déplacement des missiles et mise à jour de l'affichage du missile
		"""
		if pyxel.height + 8 > self.y > 0 - 8 :
			self.y += dy

class Missile_diago:
	"""
	missil envoyé en diagonal
	attribut :
	@x  position x du missile
	@y  position y du missile
	@col  couleur du missile
	@direction  droite ou gauche (d ou g)
	
	méthodes :
	draw -> Affichage du missile
	move -> Déplacement du missile
	"""
	
	def __init__(self, x : float, y : float, col : int, direction : str):
		"""
		Caractéristiques du missile
		"""
		self.direction = direction
		self.col = col
		self.x = x
		self.y = y
		self.h = 6
		self.w = 6
		
	
	def draw(self):
		"""
		Affichage des missiles
		"""
		if self.direction == "d" :
			pyxel.line(self.x+1, self.y+1, self.x+6, self.y+6, self.col) #crée des lignes en diagonal
			pyxel.line(self.x, self.y+1, self.x+6, self.y+7, self.col)
			pyxel.line(self.x, self.y+2, self.x+5, self.y+7, self.col)
			
		elif self.direction == "g" :
			pyxel.line(self.x-1, self.y+1, self.x-6, self.y+6, self.col) #crée des lignes en diagonal
			pyxel.line(self.x, self.y+1, self.x-6, self.y+7, self.col)
			pyxel.line(self.x, self.y+2, self.x-5, self.y+7, self.col)
		
	def move(self, dx_y : float):
		"""
		Déplacement des missiles et mise à jour de l'affichage du missile
		"""
		if self.direction == "g":
			if pyxel.height + 8 > self.y > - 8 and pyxel.width >= self.x >= 6 : # fait avancer le missile tant qu'il ne touche pas un bord
				self.y += dx_y
				self.x -= dx_y
			
			elif pyxel.height + 8 > self.y > - 8 and self.x <= 6 :
				self.direction = "d" # change la direction du missile si il touche le bord gauche
		
		elif self.direction == "d":
			if pyxel.height + 8 > self.y > - 8 and pyxel.width - 6 >= self.x >= 0 : # fait avancer le missile tant qu'il ne touche pas un bord
				self.y += dx_y
				self.x += dx_y
			
			elif pyxel.height + 8 > self.y > - 8 and self.x >= pyxel.width - 6 :
				self.direction = "g" # change la direction du missile si il touche le bord droit

class Chrono :
	"""
	chronomètre la vague en cour
	attribut :
	@minutes   nb de minutes
	@secondes  nb de secondes
	
	méthodes :
	avance -> avance le chronomètre d'un temps donné en secondes
	"""
    
	def __init__(self, minutes : int, secondes : int):
		self.minutes, self.secondes = minutes, secondes


	def avance(self, temps : int) :
	   
		if temps + self.secondes == 60 :
			self.secondes = 0
			self.minutes += 1

		elif temps + self.secondes < 0 and self.minutes > 0 :
			self.secondes = 59
			self.minutes -= 1

		elif  0 <= temps + self.secondes < 60:
			self.secondes += temps

class Background:
	"""
	dessine et anime l'arrière plan
	attribut :
	aucun
	
	méthodes :
	update -> déplace les étoiles en fonction de leur vitesse
	draw -> affiche les étoiles
	"""
			
	def __init__(self):
		self.stars = []
		for i in range(80):
			self.stars.append( ( pyxel.rndi(0, pyxel.width), pyxel.rndi(0, pyxel.height), pyxel.rndf(1, 1.5), ) )

	def update(self):
		"""
		déplace les étoiles en fonction de leur vitesse
		"""
		for i, (x, y, speed) in enumerate(self.stars):
			y += speed
			if y >= pyxel.height:
				y -= pyxel.height
			self.stars[i] = (x, y, speed)

	def draw(self):
		"""
		affiche les étoiles
		"""
		for x, y, speed in self.stars:
			pyxel.pset(x, y, 12 if speed > 1.1 else 5)


class App:
	
	def __init__(self):
		"""
		Initialisation de la fenêtre et des éléments
		"""
		
		pyxel.init(120, 200, title="Envahisseurs", fps=50, quit_key=pyxel.KEY_ESCAPE, display_scale=3) # Fenêtre de 120 par 200 pyxels
		pyxel.load("visu.pyxres")

		self.ship = Ship(pyxel.width // 2 - 4, pyxel.height - 20) # créé un vaisseau 

		self.num_level = 0 # par défault 0
		
		self.liste_ennemis, self.liste_monstres = creation_vague_ennemi(self.num_level)
		self.background = Background()
		self.temps_vague = Chrono(liste_temps_vague[self.num_level][0],liste_temps_vague[self.num_level][1])
		self.temps_tot_joue = Chrono(0,0)
		self.temps_tot = Chrono(0,0)

		self.cheat_deplacement = False
		self.cheat_missile = False
		self.cheat_vie = False
		
		self.liste_missile = []
		self.missile_ennemis = []
		self.score = 0
		self.score_vague = 0
		self.explosion_collision_missile = -1
		self.num_ecran = 1
		self.game = True
		self.afficher_info = False
		self.vague_gagne = False # par défault False
		self.vague_boss = False
		self.partie_gagne = False 
		self.ecrir = True
		self.zero_affichage = ""
		self.username = ""
		self.mouvement_precedent_boss = ""
		self.en_tete, self.classement = tri_classement()

		
		
		pyxel.run(self.update, self.draw) # On lance le moteur du jeu
		
	def update(self):
		"""
		Mise à jour des positions et des états.
		Pas d'affichage ici !
		"""
		self.temps_tot = timer(pyxel.frame_count, self.temps_tot, 1)
		if self.num_ecran == 0 and self.game and not self.vague_gagne and not self.partie_gagne :
			self.background.update()
			
			self.temps_vague = timer(pyxel.frame_count, self.temps_vague, -1)
			self.temps_tot_joue = timer(pyxel.frame_count, self.temps_tot_joue, 1)
			
			# déplacement du joueur + cheat
			dx, dy = deplacement_vaisseau(self.ship, self.cheat_deplacement, self.vague_boss) #déplacement du vaisseau
			self.ship.move(dx, dy)

			if pyxel.btnp(pyxel.KEY_EQUALS) : # active ou désactive le cheat de deplacement et de tire
				self.cheat_deplacement = not self.cheat_deplacement
				self.cheat_missile = not self.cheat_missile
				self.cheat_vie = not self.cheat_vie
			#------------------------------------------------


			# déplacement de tous les ennemis
			dx_enmi, dy_enmi, self.mouvement_precedent_boss = deplacement_ennemi(self.liste_ennemis, self.num_level, self.vague_boss, self.mouvement_precedent_boss)
			for i in range(len(self.liste_ennemis)): 
					self.liste_ennemis[i].move(dx_enmi,dy_enmi)
			#-----------------------------------

			
			# créé un missile du vaisseau
			missile = self.ship.tir_missile(self.cheat_missile)
			if missile != None :
				self.liste_missile.append(missile)  # crée un missile
			#-----------------------------------


			# créé un missile ennemi
			if pyxel.rndi(0, 50) == 0 : # active le code random
				num_ennemi = pyxel.rndi(0, len(self.liste_ennemis)-1) # choisi un ennemi au hasard
				if self.liste_ennemis[num_ennemi].en_vie :	
					self.missile_ennemis.append(self.liste_ennemis[num_ennemi].tir_missile()) # crée un missile ennemi
			#-----------------------------------


			# vérifie si la vague est gagné
			if self.num_level < len(liste_nb_ennemis) :
				self.vague_gagne = ennemi_en_vie(self.liste_ennemis)
			elif self.boss.explosion == 21:
				self.vague_gagne = True
			#-----------------------------------

	
			# déplace les missiles du vaisseau
			for missile in self.liste_missile:
				self.missile_deplacement = missile.move(-1) # fait avancer le missile du vaisseau
				if missile.y <= - missile.h :
					self.liste_missile.remove(missile) # supprime le missile du vaisseau si il sort de l'écran
			#-----------------------------------


			# déplace les missiles ennemis
			for missile_enmi in self.missile_ennemis:
				missile_enmi.move(liste_vitesse_missiles_ennemis[self.num_level]) # fait avancer le missile ennemi
				if missile_enmi.y >=  200:
					self.missile_ennemis.remove(missile_enmi) # supprime le missile ennemi quand il sort de l'écran
			#-----------------------------------

			
			for ennemi in self.liste_ennemis:
				# vérifie si le vaisseau a un contact avec un ennemi
				if (
					self.ship.x + self.ship.w > ennemi.x
					and ennemi.x + ennemi.w > self.ship.x
					and self.ship.y + self.ship.h > ennemi.y
					and ennemi.y + ennemi.h > self.ship.y
					and self.ship.en_vie
					and ennemi.en_vie
				) :
					ennemi.blessure() # blesse l'ennemi
					self.ship.blessure() # inflige un dégat au vaisseau
				# ----------------------------------------------------
				
				for missile in self.liste_missile:
					# vérifie si un ennemi se prend un missile du vaisseau
					if (
						ennemi.x + ennemi.w > missile.x
						and missile.x + missile.w > ennemi.x
						and ennemi.y + ennemi.h > missile.y
						and missile.y + missile.h > ennemi.y
						and ennemi.en_vie
						
					):
						ennemi.blessure() # blesse l'ennemi
						self.liste_missile.remove(missile) # suprime le missile de la liste
						self.score += 50
						self.score_vague += 50
					#-----------------------------------------------------

			
			for missile_enmi in self.missile_ennemis:
				# vérifie si le vaisseau est touché par un missile ennemi
				if (
					self.ship.x + self.ship.w > missile_enmi.x
					and missile_enmi.x + missile_enmi.w > self.ship.x
					and self.ship.y + self.ship.h > missile_enmi.y
					and missile_enmi.y + missile_enmi.h > self.ship.y
					and self.ship.en_vie
				) :
					self.ship.blessure() # inflige un dégat au vaiseau
					self.missile_ennemis.remove(missile_enmi) # suprime le missile_enmi de la liste
				#------------------------------------------------------

			
			for missile in self.liste_missile :
				for missile_enmi in self.missile_ennemis :
					# vérifie si 2 missiles ennemi-vaisseau se rencontre
					if (
						missile.x + missile.w > missile_enmi.x
						and missile_enmi.x + missile_enmi.w > missile.x
						and missile.y + missile.h > missile_enmi.y
						and missile_enmi.y + missile_enmi.h > missile.y
						and self.ship.en_vie
					) :
						self.missile_ennemis.remove(missile_enmi) # suprime le missile_enmi de la liste
						self.liste_missile.remove(missile) # suprime le missile de la liste
						self.cord_explo_x, self.cord_explo_y = missile.x - 7, missile.y - 7
						self.explosion_collision_missile = 0
					#--------------------------------------------------------

			
			if self.temps_vague.secondes == 0 and self.temps_vague.minutes == 0: # regarde si le temps est écoulé
				self.game = False		

			if  self.ship.explosion == 21 and not self.ship.en_vie : # regarde si le vaisseau meurt
				self.game = False
				

			if (pyxel.btnp(pyxel.KEY_KP_ENTER) or pyxel.btnp(pyxel.KEY_PAGEUP)) and self.cheat_vie:
				self.ship.soin() #soigne le joueur 

			# règle l'affichage du timer en rajoutant un 0 si nécessaire
			if	self.temps_vague.secondes <= 9 :
				self.zero_affichage = "0"
			else :
				self.zero_affichage	= ""
			#-----------------------------------------------------------
			
		else :
			
			
						
			if  self.num_ecran == 1: # lance le jeu ou passe à la vague d'ennemi suivante
				
				if pyxel.btnp(pyxel.KEY_I): # affiche les informations sur l'écran de démarrage
					if self.afficher_info :
						self.afficher_info = False
					else :
						self.afficher_info = True
					

				if pyxel.btnp(pyxel.KEY_RETURN) : # lance la partie
					self.num_ecran = 0

				if pyxel.btnp(pyxel.KEY_C): # va sur l'écran du classement
					self.num_ecran = 2

			elif self.num_ecran == 0 :
				
				if self.num_level == len(liste_nb_ennemis) and self.vague_gagne: # regarde si la partie est gagnée
					self.partie_gagne = True
					self.score += self.score_vague*self.temps_vague.secondes // 80 # ajoute quelque points en fonction du temps de la dernière vague			
					self.num_level += 1 
					
					

				elif pyxel.btnp(pyxel.KEY_RETURN) and self.vague_gagne and not self.partie_gagne: # passe à la vague suivante
						
					self.missile_ennemis.clear()
					self.liste_missile.clear() 		# clear les liste d'objets
					self.liste_ennemis.clear()

					self.score += self.score_vague*self.temps_vague.secondes // 120 # ajoute quelques points en fonction du temps passé sur la vague précédente	
					self.num_level += 1 # passe au niveau suivant
					
					if self.num_level <= len(liste_nb_ennemis) -1 : 
						self.liste_ennemis, self.liste_monstres = creation_vague_ennemi(self.num_level) # créé la prochaine vague d'ennemis

					elif self.num_level == len(liste_nb_ennemis) : # créé le vague du boss
						self.boss = Boss_final(pyxel.width -53-5, 40)
						self.mouvement_precedent_boss = "diag_gauche_droite"
						self.liste_ennemis.append(self.boss)
						self.vague_boss = True
						
					self.vague_gagne = False
					self.temps_vague.__init__(liste_temps_vague[self.num_level][0],liste_temps_vague[self.num_level][1]) # remet le décompte du temps au temps correspondant au niveau
					self.score_vague = 0 # initialise le score de la prochaine vague à 0
					

				elif self.partie_gagne or not self.game: # regarde si la partie est gagné
					
					self.missile_ennemis.clear()
					self.liste_missile.clear() 		# clear les liste d'objets
					self.liste_ennemis.clear()
					
					# Permet d'écrir un pseudo jusqu'à 14 lettres
					if self.ecrir :
						if len(self.username) < 14:
							lettre = saisie_clavier()
							if lettre != "" :
								self.username += lettre

						if pyxel.btnp(pyxel.KEY_BACKSPACE) and len(self.username) > 0:
							name_liste = list(self.username)
							name_liste.pop(-1)
							self.username = "".join(name_liste)
					#------------------------------------------------------------------
					# Permet d'enregistrer le score de la partie dans un csv et de pouvoir refaire une nouvelle partie
					if pyxel.btnp(pyxel.KEY_RETURN) and len(self.username) >= 2:
						self.ecrir = False
						with open("score_space_invaders.csv", "a", newline="") as csv_file :
							csv_writer = writer(csv_file, delimiter=",")
							
							csv_writer.writerow([self.username, self.score, self.temps_tot_joue.minutes , self.temps_tot_joue.secondes,datetime.today().strftime("%Y-%m-%d %H:%M")])

							csv_file.close()

						
						self.num_ecran = 2
						self.en_tete, self.classement = tri_classement()
						
						self.cheat_deplacement = False
						self.cheat_missile = False
						self.cheat_vie = False
						
						self.score = 0
						self.score_vague = 0
						self.explosion_collision_missile = -1
						self.game = True
						self.afficher_info = False
						self.vague_gagne = False
						self.vague_boss = False
						self.partie_gagne = False
						self.ecrir = True
						self.zero_affichage = ""
						self.username = ""
						self.mouvement_precedent_boss = ""
						
						self.num_level = 0

						self.ship = Ship(pyxel.width // 2 - 4, pyxel.height - 20)
						self.liste_ennemis, self.liste_monstres = creation_vague_ennemi(self.num_level)
						self.temps_vague = Chrono(liste_temps_vague[self.num_level][0],liste_temps_vague[self.num_level][1])
						self.temps_tot_joue = Chrono(0,0)
						self.temps_tot = Chrono(0,0)
						
					#-------------------------------------------------------------------
			elif self.num_ecran == 2 :
				if pyxel.btnp(pyxel.KEY_RETURN) :
					self.num_ecran = 1

						
	def draw(self):
		"""
		On affiche les éléments
		"""
		
		if self.num_ecran == 1 :
			pyxel.cls(0)# On rempli le fond avec une couleur
			
			self.background.draw()
			pyxel.blt(pyxel.width//2 - 33, 15, 0, 38, 48, 67, 33, 0) # affiche "SPACE INVADERS"
			pyxel.blt(pyxel.width // 2 - 4, pyxel.height - 20,  0,  8,16,  8,8) # affiche le vaisseau
			
			pyxel.blt(42,170,  0,  36,9,  7,7) # affiche "Q"
			pyxel.blt(70,170,  0,  52,9,  7,7) # affiche "D"
			pyxel.blt(42,190,  0,  36,25,  7,7) # affiche "<-"
			pyxel.blt(70,190,  0,  52,25,  7,7) # affiche "->"
			pyxel.text(42, 181 , "OR", 7) # affiche "OR"
			pyxel.text(70, 181 , "OR", 7) # affiche "OR"
			pyxel.text(60 - len("ATQ")*2, 142 , "ATQ", 7) # affiche "ATT"
			pyxel.blt(48,150,  0,  	68,9,  23,7) # affiche "SPACE"
			pyxel.text(60 - len("COMMENCER LA PARTIE")*2, 110 , "COMMENCER LA PARTIE", 7) # affiche "COMMENCER LA PARTIE"
			pyxel.blt(54,120,  0,  	67,19,  11,13) # affiche "Entré"

			
			if self.afficher_info :
				pyxel.text(60 - len("Une invasion extraterrestre")*2, 58 , "Une invasion extraterrestre", 7) # affiche le synopsis
				pyxel.text(60 - len("menace le monde, vous etes")*2, 58+7*1 , "menace le monde, vous etes", 7) # affiche le synopsis
				pyxel.text(60 - len("le seul a pouvoir nous sortir")*2, 58+7*2 , "le seul a pouvoir nous sortir", 7) # affiche le synopsis
				pyxel.text(60 - len("de cette situation avec votre")*2, 58+7*3 , "de cette situation avec votre", 7) # affiche le synopsis
				pyxel.text(60 - len("technologie de pointe,")*2, 58+7*4 , "technologie de pointe,", 7) # affiche le synopsis
				pyxel.text(60 - len("alors TUEZ LES TOUS !!!")*2, 58+7*5 , "alors TUEZ LES TOUS !!!", pyxel.frame_count  %  16) # affiche le synopsis en multi color
			else :
				pyxel.text(60 - len("INFOS [I]")*2, 58+7*2 , "INFOS [I]", 7)
				pyxel.text(60 - len("CLASSEMENT [C]")*2, 58+7*3 , "CLASSEMENT [C]", 7)
				
				
		elif self.num_ecran == 0 :
			
			pyxel.cls(0)
			self.background.draw()

			if not self.vague_boss :
				for i in range(len(self.liste_ennemis)): # on affiche les ennemis
					self.liste_ennemis[i].draw(self.liste_monstres[i])
			elif self.vague_boss:
				self.boss.draw()

			self.ship.draw()# On affiche le vaisseau

			self.ship.draw_pt_vie()# On affiche les points de vie
				
			
			for missile in self.liste_missile: # affiche les missiles du vaisseau
				missile.draw()
			
			for missile_enmi in self.missile_ennemis: # affiche les missiles ennemis
				missile_enmi.draw()

			if self.explosion_collision_missile != -1: # affiche l'explosion des impactes entre 2 missiles
				self.explosion_collision_missile = explosion(self.cord_explo_x, self.cord_explo_y, self.explosion_collision_missile)


			
			if self.partie_gagne or not self.game : # affichage de fin de partie
				if not self.game : # affichage perdant
					pyxel.rect(0, pyxel.height // 2 - 25, 120, 20, 7)
					pyxel.text(60 - len("GAME OVER")*2, pyxel.height // 2 -17, "GAME OVER", 0)
					
				elif self.partie_gagne : #affichage gagnant
					pyxel.rect(60 - len("CONGRATULATION")*3, pyxel.height // 2 - 15, len("CONGRATULATION")*6, 50, 0)
					pyxel.text(60 - len("CONGRATULATION")*2, pyxel.height // 2 -6 , "CONGRATULATION", pyxel . frame_count  %  16)
					
				pyxel.text(60 - len("SCORE FINAL : ____")*2, pyxel.height // 2 , f"SCORE FINAL : {self.score}",7) # affiche le score finale
				
				pyxel.blt(28,pyxel.height // 2 + 12,  0,  0,120,  63,10) # affiche l'encadrement pour écrire
				pyxel.text(60 - len(self.username)*2, pyxel.height // 2 + 14 , self.username ,7) # affiche ce que l'utilisateur écrit

				if self.temps_tot.secondes % 2 == 0 and len(self.username) < 14: # permet l'affichage du "_" 1s/2
					pyxel.text(60 + len(self.username)*2 , pyxel.height // 2 + 15 , "_" ,7)
				
			elif self.vague_gagne : # écran de fin de vague gagnante
				pyxel.text(60 - len("BRAVO")*2, (pyxel.height ) // 2 -4 , "BRAVO", pyxel . frame_count  %  16)
				pyxel.text(60 - len("Vague suivante")*2, (pyxel.height ) // 2 +2, "Vague suivante", 7)

			pyxel.text(10, 10, f"SCORE : {self.score}",7) # affiche le score
			pyxel.text(10, 20, f"TIMER : 0{str(self.temps_vague.minutes)}:{self.zero_affichage}{str(self.temps_vague.secondes)}" , 7) # affiche le timer

		elif self.num_ecran == 2 :
			pyxel.bltm(0, 0, 0, 0, 0, 120, 200)
			pyxel.text(32, 188, f"ecran d'accueil" , 7)
			for i, player in enumerate(self.classement) :
				if i < 9 :
					if int(player[3]) < 10 :
						zero_affichage = "0"
					else :
						zero_affichage = ""
					pyxel.text(65 - len(player[0])*2, 10+ 20*i, f"{player[0]}" , 10 if i==0 else 7)
					pyxel.text(30 - len(player[1])*2, 18+ 20*i, f"{player[1]}" , pyxel . frame_count  %  16 if i==0 else 7)
					pyxel.text(75 - len(f"points en {player[2]}.{zero_affichage}{player[3]}min")*2, 18+ 20*i, f"points en {player[2]}.{zero_affichage}{player[3]}min" , 7)
App()
