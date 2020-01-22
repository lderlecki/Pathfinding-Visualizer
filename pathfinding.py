import pygame
import sys
import numpy as np


pygame.init()
CLOCK = pygame.time.Clock()

legal_moves = [[0, -1], [0, 1], [-1, 0], [1, 0]]
right_panel = 200
width = 800 + right_panel
height = 800
cols = 50
rows = 50
w = (width - right_panel) / rows
h = height / cols

red    = (255, 0, 0)
green  = (0, 255, 0)
black  = (0, 0, 0)
blue   = (0, 0, 255)
grey   = (220, 220, 220)
white  = (255, 255, 255)
yellow = (255,255,0)
violet = (255, 0, 255)
sys.setrecursionlimit(2500)

class Node:
    """
    Create node object with specified attributes.

    Attributes:
    pos     Node position
    parent  Node from which we came to the current node
    f       Cost function value from the start node to the current node
    g       Cost function
    h       Heuristic cost
    """
    def __init__(self, pos, parent=None, f=0, g=0, h=0):
        self.pos = pos
        self.parent = parent
        self.f = f
        self.g = g
        self.h = h
        self.v = 1
        self.closed = False
        self.wall = False
        self.displayed = False
    
    def show(self, color, st):
        """
        Showing the node on the mesh.

        parameters:
        color   Color of the node to show
        st      Determine wheter to color entire node or just borders
        """
        if self.closed == False:
            pygame.display.update(pygame.draw.rect(Globals.window, color, (self.pos[0] * w, self.pos[1] * h, w-0.5, h-0.5), st))
            pygame.display.update(pygame.draw.rect(Globals.window, white, (self.pos[0] * w, self.pos[1] * h, w-0.5, h-0.5), 1))
            CLOCK.tick(Globals.fps)
            
    def __eq__(self, dif_node):
        return self.pos == dif_node.pos


class Button:
    """
    Create a button object.

    Attributes:
        color   The color of the button
        x, y    X and Y coordinates of the button
        width   Desired width
        height  Desired height
        text    Text that will be written on the button

    """

    def __init__(self, color, x, y, width, height, text=None):
        """
        Initialize the button from the given arguments
        """
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)

    def show(self, window):
        """
        Showing the button on the pygame window.

        parameter:
        window   PyGame window on which the button will be shown
        """
        pygame.draw.rect(Globals.window, self.color, self.rect,0)

        if self.text:
            font = pygame.font.SysFont('Arial', 35)
            text = font.render(self.text, 1, black)
            Globals.window.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))
        pygame.display.update()

    def is_focus(self, pos):
        # Return True if the mouse is over the button
        return self.rect.collidepoint(pos) 


class Globals:
    """
    Storage for global variables
    """
    a_star = False
    dijkstra = False
    bfs = False
    dfs = False

    mesh = [[Node(pos=[i, j]) for j in range(cols)] for i in range(rows)]
    fps = 0
    start = mesh[0][0]
    end = mesh[rows-1][cols-1]
    open_set = []
    closed_set = []
    window = pygame.display.set_mode((width,height))

    def restart(again = False):
        """
        Function used to restart main global variables.
        It is called whenever the algorithm is restarted or the path is cleaned.
        """
        Globals.a_star = False
        Globals.dijkstra = False
        Globals.bfs = False
        Globals.dfs = False
        Globals.open_set = []
        Globals.closed_set = []
        if not again:
            Globals.mesh = [[Node(pos=[i, j]) for j in range(cols)] for i in range(rows)]


def restart():
    # Restart all the parameters, path and walls
    # Start and End nodes remain unchanged
    Globals.window = pygame.display.set_mode((width,height))
    pygame.display.update()
    CLOCK.tick(Globals.fps)
    Globals.restart(True)
    setup()
    draw_screen()


def setup():
    # Setup the mesh on the screen and show the start and end nodes
    # create 2d array with squares
    Globals.mesh = [[Node(pos=[i, j]) for j in range(cols)] for i in range(rows)]
    Globals.start.show(violet, 0)
    Globals.end.show(yellow, 0)

    # show mesh
    for i in range(rows):
        for j in range(cols):
            Globals.mesh[i][j].show(white, 1)
    pygame.display.update()



def lmb(square):
    # Left Mouse button function used when drawing the walls
    try:
        if square != Globals.start and square != Globals.end:
            if not square.wall:
                square.wall = True
                square.show(grey, 0)
    # Deal with click on the right panel
    except:
        pass


def rmb(square):
    # Left Mouse button function used for removing the walls
    try:
        if square != Globals.start and square != Globals.end:
            if square.wall:
                square.wall = False
                square.show(black, 0)
    
    # Deal with click on the right panel
    except:
        pass


def drag_and_drop(node_to_move, x, y):
    '''
    Move Start and End nodes on the screen

    node_to_move    distinguish if start or end was pressed
    x, y            mouse position on the screen
    '''
    current = Globals.mesh[x][y]
    if current == Globals.end or current == Globals.start:
        return

    elif node_to_move == Globals.end:
        Globals.end = current
        Globals.end.show(yellow, 0)
        if node_to_move.wall:
            node_to_move.show(grey, 0)
        else:
            node_to_move.show(black, 0)

    elif node_to_move == Globals.start:
        Globals.start = current
        Globals.start.show(violet, 0)
        if node_to_move.wall:
            node_to_move.show(grey, 0)
        else:
            node_to_move.show(black, 0)


def get_mouse_pos():
    #Return position of the mouse on the screen
    pos = pygame.mouse.get_pos()
    x = pos[0] // ((width - right_panel) // rows)
    y = pos[1] // (height // cols)
    return (x, y)


def draw_screen():
    # mouse events for preparing the mesh
    draw = True
    while draw:
        ev = pygame.event.get()
        pos = pygame.mouse.get_pos()
        for event in ev:
            # Quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Left Mouse Button pressed
            elif pygame.mouse.get_pressed()[0]:
                # Start djikstra search
                if djikstra_butt.is_focus(pos):
                    djikstra_butt.color = green
                    djikstra_butt.show(Globals.window)
                    Globals.dijkstra = True
                    draw = False
                    break
                # Start A* search
                elif astar_butt.is_focus(pos):
                    astar_butt.color = green
                    astar_butt.show(Globals.window)
                    Globals.a_star = True
                    draw = False
                    break
                # Start Best Fisrt Search
                elif bfs_butt.is_focus(pos):
                    bfs_butt.color = green
                    bfs_butt.show(Globals.window)
                    Globals.bfs = True
                    draw = False
                    break
                # Start Depth Fisrt Search
                elif dfs_butt.is_focus(pos):
                    dfs_butt.color = green
                    dfs_butt.show(Globals.window)
                    Globals.dfs = True
                    draw = False
                    break
                # Remove all the walls
                elif redraw_butt.is_focus(pos):
                    restart()
                    return True
                else:
                    # Check if Start, End or normal node was pressed
                    try:
                        x, y = get_mouse_pos()
                        square = Globals.mesh[x][y]
                        # Move end node
                        if square == Globals.end:
                            move = True
                            if pygame.mouse.get_pressed()[0] == 1:
                                while move:
                                    x, y = get_mouse_pos()
                                    drag_and_drop(square, x, y)
                                    square = Globals.end
                                    # check if left mouse button is released
                                    event = pygame.event.poll()
                                    if event.type == pygame.MOUSEBUTTONUP:
                                        move = False
                                        break

                        # Move start node
                        elif square == Globals.start:
                            move = True
                            if pygame.mouse.get_pressed()[0] == 1:
                                while move:
                                    x, y = get_mouse_pos()
                                    drag_and_drop(square, x, y)
                                    square = Globals.start
                                    # check if left mouse button is released
                                    event = pygame.event.poll()
                                    if event.type == pygame.MOUSEBUTTONUP:
                                        move = False
                                        break

                        # Draw walls
                        else:
                            while True:
                                try:
                                    x, y = get_mouse_pos()
                                    square = Globals.mesh[x][y]
                                    event = pygame.event.poll()
                                    lmb(square)
                                    if event.type == pygame.MOUSEBUTTONUP:
                                        break
                                except:
                                    event = pygame.event.poll()
                                    if event.type == pygame.MOUSEBUTTONUP:
                                        break
                    except :
                        pass
            # Right Mouse Button pressed
            # Remove walls from the mesh
            elif pygame.mouse.get_pressed()[2]:
                try:
                    x, y = get_mouse_pos()
                    square = Globals.mesh[x][y]
                    rmb(square)
                except AttributeError:
                    pass

            # Mouse over buttons
            elif event.type == pygame.MOUSEMOTION:
                for button in buttons:
                    if button.is_focus(pos):
                        button.color = red
                        button.show(Globals.window)
                    else:
                        button.color = green
                        button.show(Globals.window)


def end_screen():
    # Screen which is shown to the user after search
    buttons = [clear_butt, redraw_butt]
    CLOCK.tick(0)
    while True:
        pos = pygame.mouse.get_pos()
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.QUIT:
                pygame.quit()
                return (False, False)
            elif event.type == pygame.MOUSEMOTION:
                for button in buttons:
                    if button.is_focus(pos):
                        button.color = red
                        button.show(Globals.window)
                    else:
                        button.color = green
                        button.show(Globals.window)
            elif pygame.mouse.get_pressed()[0]:
                if redraw_butt.is_focus(pos):
                    return (True, False)
                
                elif clear_butt.is_focus(pos):
                    Globals.restart(True)
                    for i in range(rows):
                        for j in range(cols):
                            # redraw nodes that are not walls or end or start 
                            square = Globals.mesh[i][j]
                            if square != Globals.start and square != Globals.end and not square.wall:
                                square.displayed = False
                                square.show(black, 0)
                    clear_butt.color = black
                    clear_butt.show(Globals.window)
                    draw_screen()
                    return (True, True)


def heuristic(p1, p2):
    # heuristic function for search algorithms

    # Manhatan Distance
    # return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) 

    # Euclidean Distance
    # High alpha to prioritize "diagonal" moves
    return 1.41 * np.linalg.norm(np.array(p1) - np.array(p2)) # 


def find_neighbors(pos):
    # Return all neighbors of the current node (up, down, left, right)
    x, y = pos[0], pos[1]
    neighbors = []
    if x < rows-1 and Globals.mesh[x + 1][y].wall == False:
        neighbors.append(Globals.mesh[x + 1][y])
    if x > 0 and Globals.mesh[x - 1][y].wall == False:
        neighbors.append(Globals.mesh[x - 1][y])
    if y < cols-1 and Globals.mesh[x][y + 1].wall == False:
        neighbors.append(Globals.mesh[x][y + 1])
    if y > 0 and Globals.mesh[x][y - 1].wall == False:
        neighbors.append(Globals.mesh[x][y - 1])
    return neighbors


def draw_path(node):
    path = []
    print('SEARCH FINISHED')
    # generate path
    while node.parent:
        print
        if node != Globals.end:
            path.append(node)
        node = node.parent
    # draw path
    for node in path[::-1]:
        pygame.event.get()
        CLOCK.tick(360)
        node.show(blue, 0)
    # Display final path until Globals.window is closed
    while True:
        return end_screen()


def unweighted_algorithms():
    Globals.fps = 0
    Globals.open_set = [Globals.start]
    queue = []
    def dfs():
        while Globals.open_set:
            pygame.event.get()
            current = Globals.open_set.pop(0)
            # show current node as a blue square
            if current != Globals.start and current != Globals.end:
                current.show(blue, 0)
                current.displayed = False

            elif current == Globals.end:
                # End node reached. Draw path on the screen.
                return draw_path(current)

            for node in Globals.closed_set:
                if node != Globals.start and node != Globals.end and not node.displayed:
                    node.displayed = True
                    node.show(red, 0)

            if current not in Globals.closed_set:
                Globals.closed_set.append(current)
                neighbors = find_neighbors(current.pos)
                for i, ng in enumerate(neighbors):
                    if ng not in Globals.closed_set:
                        if i == 0:
                            Globals.open_set.append(ng)
                        else:
                            # Queue of nodes to search if the first neighbor will fail
                            queue.append(ng)
                        ng.parent = current
            
            if not Globals.open_set:
                # If open_set is empty take last element from the queue
                Globals.open_set.append(queue.pop(-1))

        return (None, True)
    
    if Globals.dfs:
        return dfs()


def weighted_algorithms():
    # Finding the path with chosen algorithm

    # Start searching
    Globals.fps = 0
    Globals.open_set.append(Globals.start)
    while len(Globals.open_set) > 0:
        best_index = 0
        current = Globals.open_set[0]
        pygame.event.get()
        
        # Find node with lowest cost function
        for i, node in enumerate(Globals.open_set):
            if node.f < current.f:
                best_index = i
                current = node
        
        # show current node as a blue square
        if current != Globals.start and current != Globals.end:
            current.show(blue, 0)
            current.displayed = False
        
        # goal node reached. Draw path.
        elif current == Globals.end:
            # End node reached. Draw path on the screen.
            return draw_path(current)

        # pop current node from open set and append it to closed set
        Globals.open_set.pop(best_index)
        Globals.closed_set.append(current)

        # find all possible adjacent squares
        neighbors = find_neighbors(current.pos)

        # evaluate neighbors
        for neighbor in neighbors:
            if neighbor not in Globals.closed_set:
                temp_g = current.g + neighbor.v
                if neighbor in Globals.open_set:
                    if neighbor.g > temp_g:
                        neighbor.g = temp_g
                        neighbor.parent = current
                else:
                    neighbor.g = temp_g
                    neighbor.parent = current
                    Globals.open_set.append(neighbor)
            else:
                continue

            if Globals.a_star:
                neighbor.h = heuristic(neighbor.pos, Globals.end.pos) 
                neighbor.f = neighbor.h + neighbor.g
            
            elif Globals.dijkstra:
                neighbor.f = neighbor.g
            
            elif Globals.bfs:
                neighbor.f = heuristic(neighbor.pos, Globals.end.pos)
            
        for node in Globals.open_set:
            if node != Globals.start and node != Globals.end and not node.displayed:
                node.displayed = True
                node.show(green, 0)
        for node in Globals.closed_set:
            if node != Globals.start and node != Globals.end and not node.displayed:
                node.displayed = True
                node.show(red, 0)
    return (None, False)
# Create buttons
djikstra_butt = Button(green, width - right_panel / 2 - 80, 40        , 160, 80, text='Dijkstra')
astar_butt    = Button(green, width - right_panel / 2 - 80, 150       , 160, 80, text='A*')
bfs_butt      = Button(green, width - right_panel / 2 - 80, 260       , 160, 80, text='Best First')
dfs_butt      = Button(green, width - right_panel / 2 - 80, 370       , 160, 80, text='Depth First')
clear_butt    = Button(green, width - right_panel / 2 - 80, height-240, 160, 80, text='Clear Path')
redraw_butt   = Button(green, width - right_panel / 2 - 80, height-130, 160, 80, text='Redraw')

buttons = [djikstra_butt, astar_butt, redraw_butt, bfs_butt, dfs_butt]
for button in buttons:
    button.show(Globals.window)


def main():
    play = True
    clear_path = False
    while play:
        if not clear_path:
            Globals.fps = 0
            restart()
        # make sure start and end are not walls
        Globals.start.wall = False
        Globals.end.wall = False
        
        if Globals.dfs:
            play, clear_path = unweighted_algorithms()

        elif Globals.a_star or Globals.dijkstra or Globals.bfs:
            play, clear_path = weighted_algorithms()
        
        if play == None and clear_path:
            play, clear_path = end_screen()

        elif play == None and not clear_path:
            print('No path!')
            play, clear_path = end_screen()

if __name__ == '__main__':
    main()