#             __                  __         _            __     __          
#   ___  ___ / /__    _____  ____/ /__  ___ (_)_ _  __ __/ /__ _/ /____  ____
#  / _ \/ -_) __/ |/|/ / _ \/ __/  '_/ (_-</ /  ' \/ // / / _ `/ __/ _ \/ __/
# /_//_/\__/\__/|__,__/\___/_/ /_/\_\ /___/_/_/_/_/\_,_/_/\_,_/\__/\___/_/   
#
# Version 1.0 - Johan Ledoux
# 26.05.2023 - 08h45

import pyxel
import random
import heapq
import math
import time

class Server:
    COLOR_GREEN = 0
    COLOR_ORANGE = 16
    COLOR_RED = 32
    COMPUTER_1 = (0, 0, 14, 16, (6, 8))
    COMPUTER_2 = (0, 16, 14, 16, (6, 8))
    COMPUTER_3 = (0, 32, 14, 16, (6, 8))
    ROUTER_1 = (16, 0, 14, 16, (6, 8))
    ROUTER_2 = (16, 16, 14, 16, (6, 8))
    ROUTER_3 = (16, 32, 14, 16, (6, 8))
    
    def __init__(self, name, server_type, x, y, color=COLOR_GREEN):
        self.name = name
        self.server_type = server_type
        self.x = x
        self.y = y
        self.color = color
        self.neighbors = {}
        
    def add_neighbors(self, server, cost):
        """Ajouter un serveur voisin

        Args:
            server (_type_): Serveur à lier
            cost (_type_): Coût de la liaison
        """
        self.neighbors[server] = cost
        
    def get_neighbors(self):
        """Récupérer les voisins

        Returns:
            dict: Dictionnaire des serveurs voisins
        """
        return self.neighbors
    
    def draw(self):
        """Dessiner le serveur
        """
        pyxel.blt(self.x, self.y, 0, self.server_type[0], self.color, self.server_type[2], self.server_type[3], 7)
    
    def __lt__(self, other):
        return False


class Link:
    COLOR_DEFAULT = 13
    COLOR_YELLOW = 10
    def __init__(self, server1, server2, color=COLOR_DEFAULT):
        self.servers = (server1, server2)
        self.start_x = server1.x + server1.server_type[4][0] 
        self.start_y = server1.y + server1.server_type[4][1]
        self.end_x = server2.x + server2.server_type[4][0]
        self.end_y = server2.y + server2.server_type[4][1]
        self.color = self.COLOR_DEFAULT
    
    def draw(self):
        """Dessiner la liaison
        """
        pyxel.line(self.start_x, self.start_y, self.end_x, self.end_y , self.color)


class Network:
    def __init__(self):
        self.servers = {}
        self.offline = None
        self.links = []
    
    def add_server(self, server):
        """Ajouter un serveur au réseau

        Args:
            server (Server): Nouveau serveur 
        """
        self.servers[server.name] = server
        
    def del_server(self, server):
        """Supprimer un serveur du réseau

        Args:
            server (Server): Serveur à supprimer
        """
        self.offline = server
        self.servers.pop(server.name)

    def add_link(self, server1, server2, cost):
        """Ajouter les voisins et la liaison

        Args:
            server1 (Server): Serveur
            server2 (Server): Serveur
            cost (int): Coût de la liaison
        """
        server1.add_neighbors(server2, cost)
        server2.add_neighbors(server1, cost)
        self.links.append(Link(server1, server2))
    
    def del_links(self, server):
        """Supprimer les voisins et la liaison

        Args:
            server (Serveur): Serveur à supprimer
        """
        queue = list()
        for serv in self.servers.values():
            for neighbor in serv.neighbors:
                if neighbor == server:
                    queue.append(serv)
                    
        for serv in queue:
            serv.neighbors.pop(server)
            link = self.get_link(serv, server)
            self.links.remove(link)

    def get_server(self, server_name):
        """Récupérer un serveur

        Args:
            server_name (str): Nom du serveur à récupérer

        Returns:
            (Server): Serveur récupéré
        """
        return self.servers.get(server_name)
    
    def get_link(self, server1, server2):
        """Récupérer une liaison

        Args:
            server1 (Server): Serveur relié
            server2 (Server): Serveur relié

        Returns:
            (Link): Liaison trouvé
        """
        for link in self.links:
            if (server1 == link.servers[0] and server2 == link.servers[1]) or (server1 == link.servers[1] and server2 == link.servers[0]):
                return link
        return None
    
    def find_shortest_path(self, start_server, end_server):
        """Rechercher le chemin le plus cours entre 2 serveurs

        Args:
            start_server (Server): Serveur de départ
            end_server (Server): Serveur d'arrivé

        Returns:
            (dict): Dictionnaire du chemin à parcourir
        """
        distances = {}  # Dictionnaire des distances depuis le serveur de départ jusqu'à chaque serveur
        previous = {}  # Dictionnaire des précédents serveurs sur le chemin le plus court
        heap = []  # Tas binaire pour trouver le serveur le plus proche

        # Initialisation des distances
        for server in self.servers.values():
            if server == start_server:
                distances[server] = 0
                heapq.heappush(heap, (0, server))
            else:
                distances[server] = float('inf')
            previous[server] = None

        while heap:
            current_distance, current_server = heapq.heappop(heap)

            if current_server == end_server:
                # On a atteint le serveur de destination, donc on a trouvé le chemin le plus court
                path = []
                while current_server:
                    path.insert(0, current_server)
                    current_server = previous[current_server]
                return path

            if current_distance > distances[current_server]:
                # Ignore les mises à jour de distance qui ne sont plus optimales
                continue

            for neighbor, cost in current_server.get_neighbors().items():
                distance = current_distance + cost

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_server
                    heapq.heappush(heap, (distance, neighbor))

        # Si on arrive ici, il n'y a pas de chemin possible entre les serveurs
        return None
    
    def get_route(self):
        """Dessiner une route aléatoire et mettre en panne un serveur aléatoirement
        """  
        broken_probably = random.randint(1, 5)
        if broken_probably == 1:
            routers_name = ('R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7')
            broken_router = self.get_server(random.choice(routers_name))
            self.del_links(broken_router)
            self.del_server(broken_router)
            self.offline.color = Server.COLOR_RED
            
        
        servers = ['C1', "C2", "C3", "C4"]
        start_server = self.get_server(random.choice(servers))
        end_server = self.get_server(random.choice(servers))
        
        while end_server == start_server:
            end_server = self.get_server(random.choice(servers))
        
        shortest_path = self.find_shortest_path(start_server, end_server)
        
        if shortest_path:
            for i in range(len(shortest_path)):
                shortest_path[i].color = Server.COLOR_ORANGE
                if i < len(shortest_path)-1:
                    link = self.get_link(shortest_path[i], shortest_path[i+1])
                    link.color = Link.COLOR_YELLOW
            
            for server in shortest_path:
                server.color = Server.COLOR_ORANGE
                
        else:
            start_server.color, end_server.color = Server.COLOR_RED, Server.COLOR_RED


class App:
    def __init__(self):
        pyxel.init(128, 128, title='Simulateur de réseau', fps=30)
        pyxel.load('res.pyxres')
        
        self.paused = False
        self.init_network()
        
        pyxel.run(self.update, self.draw)
        
    def init_network(self):
        """Initialiser le réseau 
        """
        self.network = Network()
        
        computer1 = Server('C1', Server.COMPUTER_1, 5, 5)
        computer2 = Server('C2', Server.COMPUTER_1, 108, 5)
        computer3 = Server('C3', Server.COMPUTER_1, 5, 108)
        computer4 = Server('C4', Server.COMPUTER_1, 108, 108)
        
        router1 = Server('R1', Server.ROUTER_1, 50, 20)
        router2 = Server('R2', Server.ROUTER_1, 15, 50)
        router3 = Server('R3', Server.ROUTER_1, 15, 80)
        router4 = Server('R4', Server.ROUTER_1, 55, 60)
        router5 = Server('R5', Server.ROUTER_1, 90, 40)
        router6 = Server('R6', Server.ROUTER_1, 95, 75)
        router7 = Server('R7', Server.ROUTER_1, 60, 100)

        self.network.add_link(computer1, router1, 1)
        self.network.add_link(computer2, router5, 1)
        self.network.add_link(computer3, router3, 1)
        self.network.add_link(computer4, router7, 1)
        
        self.network.add_link(router1, router2, 1)
        self.network.add_link(router1, router4, 1)
        self.network.add_link(router1, router5, 1)
        self.network.add_link(router2, router3, 1)
        self.network.add_link(router3, router4, 1)
        self.network.add_link(router3, router7, 1)
        self.network.add_link(router4, router6, 1)
        self.network.add_link(router5, router7, 1)
        self.network.add_link(router6, router7, 1)
        
        self.network.add_server(computer1)
        self.network.add_server(computer2)
        self.network.add_server(computer3)
        self.network.add_server(computer4)
        
        self.network.add_server(router1)
        self.network.add_server(router2)
        self.network.add_server(router3)
        self.network.add_server(router4)
        self.network.add_server(router5)
        self.network.add_server(router6)
        self.network.add_server(router7)
        
    def fonction_delay(self, fonction, time):
        """Executer une fonction à interval régulier

        Args:
            fonction (fonction): Fonction à répéter
            time (int): Délai entre 2 répétitions
        """
        if pyxel.frame_count % (time * 30) == 0:
            fonction()
    
    def update(self):
        if not self.paused:
            self.fonction_delay(self.init_network, 2)
            self.fonction_delay(self.network.get_route, 3)
        
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.paused = not self.paused
            

    def draw(self):
        pyxel.cls(0)
        pyxel.rect(0, 0, 128, 128, 7)
        
        for link in self.network.links:
            link.draw()
        
        for server in self.network.servers.values():
            server.draw()
            
        if self.network.offline is not None:
            self.network.offline.draw()
            
        if self.paused:
            frame = pyxel.frame_count % 60
            if frame <= 30:
                pyxel.text(55, 3, 'Pause', 0)
         
if __name__ == '__main__':
    App()