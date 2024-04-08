# Projet : Système d'exploitation
# Realisation : 
#                NOM : TOUATI         PRÉNOM : MOUNIA           N° Etudiant : 20225680           GROUPE : L3CILS         
#                NOM : OUAFI          PRÉNOM : RABAH            N° Etudiant : 20223502           GROUPE : L3CILS
# _______________________________________________________________________________________________________________________

import threading
import time
from time import sleep
import graphviz
import random


#_________________________________________________Class-Task__________________________________________________
class Task:
    def __init__(self, name, reads=None, writes=None, run=None):
        self.name = name
        self.reads = reads if reads is not None else []
        self.writes = writes if writes is not None else []
        self.run = run

    def runtask(self):
        if callable(self.run):
            self.run()
        else:
            raise RuntimeError("la fonction de la Tache {self.name} n'est pas executable")

 #______________________________________________Class-TaskSystem________________________________________________
 
class TaskSystem:
    def __init__(self, tasks, dependences):
        self.listtask = tasks
        self.precedences = dependences

    def getDependencies(self, nomtask):
        if nomtask in self.precedences:
            return self.precedences[nomtask]
        else:
            return "la tache n'existe pas"

    # methode execution sequentielle
    def runSeq(self):
        executed_tasks = set()
        task_executed = False
        while len(executed_tasks) < len(self.listtask):
            for t in self.listtask:
                if t.name not in executed_tasks:
                    dependencies_met = True  # On suppose d'abord que toutes les dépendances ont été executer

                    # Vérifie chaque dépendance individuellement
                    for dep in self.getDependencies(t.name):
                        if dep not in executed_tasks:
                            dependencies_met = False  # Une dépendance n'est pas satisfaite
                            break  # on sort de la boucle pas besoin de verifier les autres (tant que une dependance n'a pas été  executé la tache courante ne peut pas etre executer)

                    # Si toutes les dépendances sont satisfaites, exécute la tâche
                    if dependencies_met:
                        t.runtask()
                        executed_tasks.add(t.name)
                        task_executed = True
                        break  # Sort de la boucle for et recommence le while pour vérifier les autres tâches

        if not task_executed:
            # Si aucune tâche n'a été exécutée dans ce cycle, il y a une erreur dans les dépendances
            raise RuntimeError("Certaines tâches ne peuvent pas être exécutées à cause de dépendances non résolues.")
        



    #Methode run paralléle
    def run(self):
        global executed_task
        executed_task = set()  # un set des taches términées
        launched_task = set()  # un set des taches en cours d'execution

        #on parcours les liste des taches totale
        while len(executed_task) < len(self.listtask):
            for t in self.listtask:
                if t.name not in launched_task:
                    if self.stats_dep(t):
                        launched_task.add(t.name)
                        threading.Thread(name=t.name, target=self.run_task, daemon=True, args=(t,)).start()

    # fonction pour exécuter les taches et lister les taches términées
    def run_task(self, t):
        t.runtask()
        executed_task.add(t.name)  # ajout de la tache à la liste des terminée après la fin de son execution

    def stats_dep(self, t):
        if len(self.getDependencies(t.name)) == 0:
            etat = True
        else:
            etat = True
            for dep in self.getDependencies(t.name):
                if dep not in executed_task:
                    etat = False
        return etat

    
    #  Methodes Validation du système
    def verification(self):
        # on verifie s'il y a des taches dupliquées dans notre systéme
        Tdup = set()
        valide = True
        for task in self.listtask:
            if self.listtask.count(task) > 1:
                Tdup.add(task)
                valide = False
        for t in Tdup: print(t.name, ' est dupliquée')

        # on verifie si le dictionnaire de precedence contient des taches cles inexistantes
        noms_des_taches = [task.name for task in self.listtask]
        for nom_tache in self.precedences:
            if nom_tache not in noms_des_taches:
                print(f"Erreur : La tâche '{nom_tache}' n'exite pas (dans le dictionnaire).")
                valide = False

            for taskd in self.getDependencies(nom_tache):
                if taskd not in noms_des_taches:
                    print(
                        f"Erreur : la tache :' {taskd} ' n'existe pas dans la liste des precedances de la tache  {nom_tache} ")
                    valide = False

        # on verifie  si task1 dépend de task2 et vice-versa (-> <-)
        for i in range(len(self.listtask)):
            for j in range(i + 1, len(self.listtask)):
                task1 = self.listtask[i]
                task2 = self.listtask[j]
                if task1.name in self.getDependencies(task2.name) and task2.name in self.getDependencies(task1.name):
                    print(f"Les deux tâches {task1.name} et {task2.name} dépendent l'une de l'autre.")
                    valide = False
        if not self.conditionBernstein():
            valide = False
        return valide

   

    # Methode draw  : on a utiliser Graphviz
    def draw(self):
        Graphe = graphviz.Digraph(comment="Graphe d'exécution en parallèle", strict=True)  # intialisation du graphe
        taskwithnodep = []  # liste pour les taches qui n'ont pas de dependance
        taskwithdep = []  # list pour les tache qui ont des dependances
        if self.verification():

            for task in self.listtask:  # on cherche les taches sans dependence et on les stock dans la listwithnoddep
                if self.getDependencies(task.name) == []: taskwithnodep.append(task)

            for task in self.listtask:  # on stock les taches qui on au moin une dependence
                if task not in taskwithnodep:
                    taskwithdep.append(task)

            for task in taskwithnodep:  # boucle pour créé les noeuds des taches independente
                Graphe.node(task.name)

            drawn = taskwithnodep  # stock drawn tasks kwithout dependencies in drawn list

            while taskwithdep:  # boucle utilisée pour dessiner les taches qui ne sont pas encore dessinées tq il reste au moins une tache dans taskwithdep ()
                # chaque fois qu'on en dessine une, on la retire de la liste et on la deplace vers la liste des taches dessinées

                todraw = taskwithdep  # Met la liste taskwithdep en attente de dessin

                for task in todraw:  # Pour chaque tâche, on vérifie si ses dépendances sont déjà dessinées pour pouvoir la dessiner
                    if all(elem in list(map(lambda x: x.name, drawn)) for elem in self.getDependencies(task.name)):
                        for elem2 in self.getDependencies(
                                task.name):  # Durant cette boucle, on vérifie pour chaque élément (type Tâche) des dépendances de la tâche
                            # si elle est liée à un autre élément pour ne pas ajouter des arêtes inutiles
                            if len(self.getDependencies(task.name)) > 1:
                                for elem3 in list(filter(lambda x: x != elem2, self.getDependencies(task.name))):
                                    if elem2 in self.getDependencies(elem3):
                                        pass  # Si les dépendances de la tâche sont liées, on ne crée pas d'arête
                                    else:  # else on les relie
                                        Graphe.node(task.name)
                                        Graphe.edge(elem2, task.name)
                                        drawn.append(task)
                                        if task in taskwithdep: taskwithdep.remove(task)
                            else:
                                Graphe.node(task.name)
                                Graphe.edge(elem2, task.name)
                                drawn.append(task)
                                if task in taskwithdep: taskwithdep.remove(task)

                todraw = []  # reinitialiser todraw pour le prochain passage

            Graphe.format = 'png'
            Graphe.render('my_graph', view=True)  # genere et affiche le graphe




    def parCost(self):
        temps_seq = []
        temps_par = []
        global M1, M2, M3, M4, M5, task_order
        m1, m2, m3, m4, m5 = 5, 4, 6, 7, 9    

        if self.verification():
            print("Calcul du coût des systèmes en cours...")
            for i in range(1, 4):
                print("\033[0m --- Tour",i,"---")
                M1, M2, M3, M4, M5 = m1, m2, m3, m4, m5
                startseq = time.perf_counter() 
                self.runSeq()
                finishseq = time.perf_counter() 
                temps_seq.append(round(finishseq - startseq, 4))
                print("\033[0m Ordre d'execution des tâches système séquetiel: \033[94m", task_order)
                task_order = []

                M1, M2, M3, M4, M5 = m1, m2, m3, m4, m5

                startpar = time.perf_counter()
                self.run()
                finishpar = time.perf_counter()
                temps_par.append(round(finishpar - startpar, 4))
                print("\033[0m Ordre d'execution des tâches système parallèl: \033[94m", task_order)
                task_order = []

            print("\033[92m", "liste des temps du système séquentiel :", temps_seq)
            print("\033[92m", "Temps moyen d'execution du run séquentiel :", sum(temps_seq) / len(temps_seq))

            print("\033[93m", "liste des temps du système parallèl:", temps_par)
            print("\033[93m", "Temps moyen d'execution du run parallèl :", sum(temps_par) / len(temps_par))

    


    def detTestRnd(self):
        global M1, M2, M3, M4, M5, task_order

        print("\033[0m Test du système avec des jeux de valeurs en cours..")
        m1, m2, m3, m4, m5 = (random.randint(0, 10), random.randint(0, 10),
                              random.randint(0, 10), random.randint(0, 10), random.randint(0, 10))

        M1, M2, M3, M4, M5 = m1, m2, m3, m4, m5
        print(f"Voici les valeurs de départ à chaque boucle de teste pour les variable:\n M1={M1} M2={M2} M3={M3} M4={M4} M5={M5}")

        for i in range(1, 5):
            print("\033[92m", "Test", i,"sur 4 :")
            M1, M2, M3, M4, M5 = m1, m2, m3, m4, m5

            #self.runSeq()
            #print("\033[92m", f"Les Valeurs des variables après execution du séquentiel\n M1={M1} M2={M2} M3={M3} M4={M4} M5={M5}")

            M1, M2, M3, M4, M5 = m1, m2, m3, m4, m5
            self.run()
            print("\033[93m", f"Les Valeurs des variables après execution du parallèl\n M1={M1} M2={M2} M3={M3} M4={M4} M5={M5}")
            print("\033[0m Ordre d'execution des tâches :\033[94m ", task_order)
            task_order = []



    # Cette fonction est uniquement utilisée pour savoir si le système
    # respecte les condition de Bernstein et qu'il est détérministe
    def conditionBernstein(self):
        check = True
        for task in self.listtask:
            if check:
                for task2 in self.listtask:
                    if task != task2:
                        if (set(task.writes) & set(task2.writes) != set()) and (
                                set(task.reads) & set(task2.writes) != set()) and (
                                set(task2.reads) & set(task.writes) != set()):
                            print("Ce système n'est pas détérministe car par exemple les tâches ", task.name, " et ",
                                  task2.name, " sont intérferantes.")
                            check = False
                            break
            else:
                break
        return check




#____________________________________________________________MAIN________________________________________________________




M1, M2, M3, M4, M5 = 0, 0, 0, 0, 0
task_order = []

#on utilise time.sleep pour simuler la durée d'une tache qui peut varier d'une utilisation a une autre

def runT1():
    global M3
    task_order.append("début T1")
    random.seed(M2)
    sleep(random.randint(0, 3))
    M3 += M1 - M2
    task_order.append("fin T1")


def runT2():
    global M4
    task_order.append("début T2")
    M4 *= M1
    random.seed(M1)
    time.sleep(random.randint(0, 3))
    task_order.append("fin T2")


def runT3():
    global M1
    task_order.append("début T3")
    random.seed(M4)
    time.sleep(random.randint(0, 3))
    M1 = M3 - M4 + 2
    task_order.append("fin T3")

def runT4():
    global M5
    task_order.append("début T4")
    random.seed(M3)
    time.sleep(random.randint(0, 3))
    M5 += 2 * (M3 + M4)
    task_order.append("fin T4")

def runT5():
    global M2
    task_order.append("début T5")
    random.seed(M4)
    time.sleep(random.randint(0, 3))
    M2 += 5 * M4
    task_order.append("fin T5")

def runT6():
    global M5
    task_order.append("début T6")
    random.seed(M5)
    time.sleep(random.randint(0, 3))
    M5 -= 50
    task_order.append("fin T6")

def runT7():
    global M4
    task_order.append("début T7")
    random.seed(M2)
    time.sleep(random.randint(0, 3))
    M4 = M1 * M2 + M4
    task_order.append("fin T7")

def runT8():
    global M5
    task_order.append("début T8")
    random.seed(M1)
    time.sleep(random.randint(0, 3))
    M5 = M1 * M3 + 5
    task_order.append("fin T8")

t1 = Task("T1", ["M1", "M2"], ["M3"], runT1)

t2 = Task("T2", ["M1"], ["M4"], runT2)

t3 = Task("T3", ["M3", "M4"], ["M1"], runT3)

t4 = Task("T4", ["M3", "M4"], ["M5"], runT4)

t5 = Task("T5", ["M4"], ["M2"], runT5)

t6 = Task("T6", ["M5"], ["M5"], runT6)

t7 = Task("T7", ["M1", "M2", "M4"], ["M4"], runT7)

t8 = Task("T8", ["M1", "M3"], ["M5"], runT8)

sys = TaskSystem([t1, t2, t3, t4, t5, t6, t7, t8], {'T1': [], 'T2': ["T1"], 'T3': ["T2"], 'T4': ["T2"],
                                                  'T5': ["T3", "T4"], 'T6': ["T4"], 'T7': ["T5", "T6"], 'T8': ["T7"]})
print("Comparaison entre le temps moyen d'execution paralléle et sequentielles du système de taches sur 3 tours - parCost ")
sys.parCost()
print ("\033[91m____________________________________________________________________________________________________________________________________________________________________\033[0m")
sys.detTestRnd() 
sys.draw()


