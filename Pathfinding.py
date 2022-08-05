# you can now click and drag to place multiple walls simultaneously
# also prevents errors if you click buttons after closing the toplevel window widget


import threading

import tkinter as tk
import tkinter.scrolledtext as tkst

from time import sleep




class dot:

    def __init__(self, owner, x, y, name):
        self.btn = tk.Button(owner.root, command=self.update_btn, bg='white', width=1)

        if owner.debug_mode:
            self.btn.config(text=name)

        self.btn.grid(column=x, row=y, ipadx=5)

        # store coords for use in changing the grid
        self.x = x
        self.y = y
        self.name = name

        self.status = 'free'


        self.owner = owner
        # this allows editing of the enclosing 'map''s variables within the button's function call as it has a reference point to call attributes from

    def update_btn(self):


        if self.owner.mouse_dragging:           # to prevent rapid flashing, mouse drag is exclusively used to make walls
            if self.status == 'free':
                self.btn.configure(bg = 'black')
                self.status = 'wall'
                self.owner.updated.set()

        else:
            if self.status == 'free' and self.owner.start == False:       # no start point so set one
                self.btn.configure(bg = 'yellow')

                self.status = 'start'
                self.owner.start = self.name

            elif self.status == 'free' and self.owner.end == False:       # no end point so set one
                self.btn.configure(bg = 'blue')

                self.status = 'end'
                self.owner.end = self.name


            elif self.status == 'start':                            # remove start point
                self.btn.configure(bg = 'white')

                self.status = 'free'
                self.owner.start = False

            elif self.status == 'end':                              # remove end point
                self.btn.configure(bg = 'white')

                self.status = 'free'
                self.owner.end = False


            elif self.status == 'free':
                self.btn.configure(bg = 'black')
                self.status = 'wall'

            elif self.status == 'wall' and not self.owner.mouse_dragging:
                self.btn.configure(bg = 'white')
                self.status = 'free'

            self.owner.updated.set()

    def become_path(self):
        self.btn.configure(bg='green')

    def was_tested(self):
        self.btn.configure(bg='#F08080')



class make_map:

    def __init__(self, width=10):

        # control panel

        self.time_tick = 0.1

        self.mouse_dragging = False

        self.ctrl = tk.Tk()
        self.debug_mode = False
        self.ctrl.title("Controls")

        self.ctrl_frame = tk.Frame(self.ctrl)


        # control buttons
        reset_btn = tk.Button(self.ctrl_frame, text='Reset', command=self.reset, bg='red')
        reset_btn.grid(column=0, row=0, sticky='nsew')
        AStar_btn = tk.Button(self.ctrl_frame, text='AStar', command=self.AStar_function)
        AStar_btn.grid(column=1, row=0, sticky='nsew')
        debug_btn = tk.Button(self.ctrl_frame, text='Debug', command=self.debug_toggle)
        debug_btn.grid(column=0, row=1, sticky='nsew')

        # allow users to input new dimensions
        dimension_label = tk.Label(self.ctrl_frame, text='Dimensions')
        dimension_label.grid(column=1, row=1, sticky='nsew', ipadx=5, ipady=5)


        self.dimension_input = tk.Entry(self.ctrl_frame, width=3)
        self.dimension_input.grid(column=1, row=1, sticky='nsew')
        self.dimension_input.insert(0, "15x15")


        legend_text = "KEY:\nYellow: start\nBlue:   end\nwhite:  empty space\nblack:  wall\ngreen:  discovered path"
        legend = tk.Label(self.ctrl_frame, text=legend_text)
        legend.grid(column=5, row=0, columnspan=3, rowspan=2, sticky = 'w')


        # toggle autoplay
        autoplay_label = tk.Label(self.ctrl_frame, text='Autoplay')
        autoplay_label.grid(column=2, row=1, sticky='nsew', ipadx=5, ipady=5)

        self.play_btn = tk.Button(self.ctrl_frame, text='\u25B6', command=self.play)
        self.play_btn.grid(column=3, row=1, sticky='nsew')


        self.is_playing = threading.Event()
        self.updated = threading.Event()
        self.algorithm = self.AStar



        self.ctrl_frame.pack(anchor='w')

        self.log_panel = tkst.ScrolledText(self.ctrl, width=30, height=15)
        self.log_panel.pack()
        self.log("Click two squares to place start and end, then further squares to place walls")

        self.setup_main(width) # initialise map itself - seperate function for reset button

        self.ctrl.mainloop()

    def setup_main(self, width):


        self.is_playing.clear()
        self.updated.clear()
        self.play_btn.config(text='\u25B6')



        self.root = tk.Toplevel()
        self.open_map = True
        self.root.protocol("WM_DELETE_WINDOW", self.close_map)


        self.root.bind("<B1-Motion>", self.mouse_drag)


        try:
            new = self.dimension_input.get()
            new = new.split('x')
            self.width = int(new[0])
            self.height = int(new[1])

        except:
            self.log("Not valid dimensions, defaulted to 15x15")
            self.width = 15
            self.height = 15


        self.dot_grid = {}      # this is the grid of buttons to be interacted with. it is a dictnionary to later change the nodes on the path
        self.start = False
        self.end = False

        self.root.title("Map")

        # populate the button grid
        for y in range(self.height):
            for x in range(self.width):
                name = str(x) + ',' + str(y)
                self.dot_grid[name] = dot(self, x, y, name)

    def close_map(self):
        '''
        handler if the user closes the map window
        '''
        if self.debug_mode:
            self.log("Map window closed")

        self.open_map = False
        self.root.destroy()

    def mouse_drag(self, drag_event):
        '''
        Allows the user to click and drag to trigger multiple walls at once
        '''
        self.mouse_dragging = True # flag to prevent rapid toggling of buttons
        self.root.winfo_containing(drag_event.x_root, drag_event.y_root).invoke()
        self.mouse_dragging = False

    def reset(self):
        self.root.destroy()
        self.setup_main(self.width)

    def log(self, message):
        message = str(message)
        message += '\n'
        self.log_panel.insert(tk.INSERT, message)

    def debug_toggle(self):

        if self.debug_mode:
            self.debug_mode = False
            self.log("Debug mode disabled")
        else:
            self.debug_mode = True
            self.log("Debug mode enabled")
            self.log("Debug mode needs restart to take effect!")

    def make_graph(self):
        '''
        sets self.graph to a graph of the map
        '''
        outGraph = graph(self)
        assert self.start and self.end


        for item in self.dot_grid:

            # gather node data and add to graph node
            current = self.dot_grid[item]

            if current.status == 'wall':
                continue
            elif current.status in ('start', 'end'):
                name = current.status
            else:
                name = current.name

            x = current.x
            y = current.y

            outGraph.add_node(name, x, y)

            # connect to neighboring nodes

            
            for dy in (-1, 1):
                target_y = y + dy
                target_x = x
                target_name = str(target_x) + ',' + str(target_y)

                try:
                    target = self.dot_grid[target_name]
                except:                                     # the target is off the edge of the map
                    continue

                if target.status == 'wall':
                    continue
                elif target.status in ('start', 'end'):
                    target_name = target.status

                outGraph.connect(name, target_name)

            for dx in (-1, 1):
                target_y = y
                target_x = x + dx
                target_name = str(target_x) + ',' + str(target_y)

                try:
                    target = self.dot_grid[target_name]
                except:                                     # the target is off the edge of the map
                    continue

                if target.status == 'wall':
                    continue
                elif target.status in ('start', 'end'):
                    target_name = target.status

                outGraph.connect(name, target_name)

        self.graph = outGraph

    def show_path(self, path):
        for i in path:
            if i == 'start':        # the name of the start and end points within the graph are 'start' and 'end'
                name = self.start   # this code retrieves the names these nodes are stored as within the map node list
            elif i == 'end':
                name = self.end
            else:
                name = i

            self.dot_grid[name].become_path()


    def AStar_function(self):
        self.algorithm = self.AStar
        self.tick()

    def AStar(self):
        try:
            self.make_graph()
        except:
            self.log("Start/End node not set!")
        else:
            path = self.graph.AStar('start', 'end')

            if path == False:
                self.log("Impossible path requested")
            else:
                self.show_path(path)

            if self.debug_mode:
                self.log(path)


    def play(self):
        '''
        Function to create a thread to run the autoplay function.
        This allows the play button to toggle autopla
        '''
        if not self.is_playing.is_set():

            play_thread = threading.Thread(target=self.auto_play, daemon=True)
            play_thread.start()
            self.is_playing.set()

            self.play_btn.config(text='\u23F8')

            if self.debug_mode:
                self.log(f"autoplay enabled with time tick {self.time_tick}s and algorithm {self.algorithm}")

        else:
            self.is_playing.clear()
            self.play_btn.config(text='\u25B6')
            
    def auto_play(self):
        '''
        Continuously re detect a path at a constant speed using the most recently used algorithm defaulting to AStar.
        '''

        while True:
            if self.updated.is_set():    # this prevents the screen from flashing every self.time_tick seconds as it re finds a path that hasn't changed
                self.tick()
                self.updated.clear()

            sleep(self.time_tick)

            if not self.is_playing.is_set():
                break

    def tick(self):
        '''
        Find a path using the algorithm stored in 'most recently used'
        In newer versions of this program, all pathfinding is done through this function to allow for the removal of previous paths
        '''

        # prevent errors if the user closes the button window
        if self.open_map:

            # remove any "debris" from previous paths
            for cell in self.dot_grid:
                if self.dot_grid[cell].status == "free":
                    self.dot_grid[cell].btn.configure(bg="white")


            # use the algorithm
            self.algorithm()

        else:
            self.log("No open map window!")






class graph:
    '''
    A graph class, stores nodes in a dictionary
    The nodes suport x/y coordinates and can be weighted for connections, once connected
    A* algorithm support for finding shortest route between two nodes
    '''

    # SETUP a new graph
    def __init__(self, owner):
        self.nodes = {}
        self.owner = owner

    def add_node(self, name, x=0, y=0):
        self.nodes[name] = node(name, x, y)
        
    def connect(self, a, b, weight=0):
        #if not a in self.nodes or not b in self.nodes:
        #    raise Exception
        self.nodes[a].connect(b, weight)
        #self.nodes[b].connect(a, weight)

    def find_heuristic(self, start, stop):
        # this finds objective distance for use as a heuristic

        start = self.nodes[start]
        stop  = self.nodes[stop]

        if not isinstance(start, node) or not isinstance(stop, node):
            raise TypeError

        d_x = stop.x_coord - start.x_coord
        d_y = stop.y_coord - start.y_coord

        d_squared = d_x ** 2 + d_y ** 2

        dist = d_squared ** 0.5

        return dist
    # No more new graph functions

    # Find path with A* algorithm
    def AStar(self, start, end):
        '''
        Applies AStar to the graph.
        When a path is found returns the path as an array of names of crossed nodes in order.
        If no path is possible, returns false.
        '''

        try:
            _ = self.nodes[start]
            _ = self.nodes[end]

        except Exception as e:
            raise type(e)("The provided start and end nodes are invalid")

        open_list     = {}
        closed_list   = {}
        checked_names = []

        # format = (node name, distance from start, parent node)
        open_list[start] =  (0, None)

        while open_list: # still unvisited nodes
            #print(open_list)
            #print(checked_names)

            # find shortest distance unvisited node

            closest = 999999999
            for node in open_list:
                if open_list[node][0] < closest:
                    current = node
                    closest = open_list[node][0]


            closed_list[current] = open_list[current]



            # this is unique to this implementation
            if current == 'start':
                name = self.owner.start
            elif current == 'end':
                name = self.owner.end
            else:
                name = current

            self.owner.dot_grid[name].was_tested()        # this is to highlight the tested nodes to visualise the algorithm



            # have we found it?
            if current == end:
                #print('DONE ALGORITHM NOW FIND PATH')
                break

            #print("SEARCHING: {}".format(current))

            # add children to open_list
            for connected in self.nodes[current].connections:

                # have we visited this node yet?
                if connected in checked_names:
                    continue

                # find weight for A*
                #       |            HEURISTIC                  | |         WEIGHT OF CONNECTING EDGE         |
                weight = int(self.find_heuristic(connected, end) + self.nodes[current].connections[connected])

                sum_w  = weight + open_list[current][0]

                # do we have a route to the target?
                try:
                    _ = open_list[connected]

                except:     # unseen node
                    open_list[connected] = (sum_w, current)
                    continue

                # is the new path shorter?
                if open_list[connected][0] < sum_w:
                    pass
                else:
                    open_list[connected] = (sum_w, current)




            checked_names.append(current)
            del open_list[current]


        # find path based on parent

        parent = current
        path = []
        #print(closed_list)

        while parent:
            path.append(parent)

            parent_node = closed_list[parent]
            parent = parent_node[1]

        path.reverse()

        if path[-1] != end:
            path = False

        return path

    # display info about graph
    def __repr__(self):
        string = "A graph containing {} nodes:".format(len(self.nodes))
        for i in self.nodes:
            string += "\n{} at ({},{})".format(i, self.nodes[i].x_coord, self.nodes[i].y_coord)

        return string


class node:
    def __init__(self, name, x, y):
        self.x_coord = x
        self.y_coord = y
        self.connections = {}
        self.name = name    

    def __repr__(self):
        string = "Graph node called {} ({},{})\nConnected to the following nodes:".format(self.name, self.x_coord, self.y_coord)
        for i in self.connections:
            string += "\n{}, weight: {} ".format(i, self.connections[i])
        
        return string

    def connect(self, target, weight):
        self.connections[target] = weight



f = make_map()