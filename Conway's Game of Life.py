# Conway's Game of life
# by Jad



import tkinter as tk
import tkinter.scrolledtext as tkst
import threading

from time import sleep
from random import randint





class dot:

    def __init__(self, owner, x, y, name):
        self.btn = tk.Button(owner.dot_frame, text='  ', command=self.update_btn, bg='white')
        
        self.x = x
        self.y = y

        self.btn.grid(column=x, row=y, ipadx=5, sticky='nesw')

        self.is_alive = False
        self.count = 0
        self.name = name

        self.owner = owner

    def find_neighbours(self):
        # find neighbours

        self.neighbours = []

        if not self.owner.solid_walls.get():
            if self.x == 0:
                dx = [self.owner.width - 1, 0, 1]
            elif self.x == self.owner.width - 1:
                dx = [-1, 0, -self.x]
            else:
                dx = [-1, 0, 1]


            if self.y == 0:
                dy = [self.owner.height - 1, 0, 1]
            elif self.y == self.owner.height - 1:
                dy = [-1, 0, -self.y]
            else:
                dy = [-1, 0, 1]

        else:
            if self.x == 0:
                dx = [0, 1]
            elif self.x == self.owner.width - 1:
                dx = [-1, 0]
            else:
                dx = [-1, 0, 1]


            if self.y == 0:
                dy = [0, 1]
            elif self.y == self.owner.height - 1:
                dy = [-1, 0]
            else:
                dy = [-1, 0, 1]



        for i in dx:
            target_x = self.x + i

            for l in dy:
                if l == 0 and i == 0:
                    continue

                target_y = self.y + l

                self.neighbours.append(self.owner.dot_grid[f'{target_x},{target_y}'])


        self.find_count()

    def find_count(self):
        '''
        seperate function as count of live neighbours would change mid game tick producing undesirable results
        '''
        self.count = sum([1 for i in self.neighbours if i.is_alive])

        #self.btn.config(text=self.count)


    def update_btn(self):
        if self.is_alive and not self.owner.mouse_dragging:
            self.die()

        else:
            self.live()


    def die(self):
        self.is_alive = False
        self.btn.config(bg='white')


    def live(self):
        self.is_alive = True
        self.btn.config(bg='black')


    def tick(self):
        '''
        iterate though one tick of the game of life.
        '''
        if self.is_alive:
            if self.count == 2 or self.count == 3:
                pass
            else:
                self.die()

        else:
            if self.count == 3:
                self.live()



class life_map:


    def __init__(self, width=15, height=15):

        # control panel
        self.root = tk.Tk()
        self.root.title("Controls")

        self.ctrl_frame = tk.Frame(self.root)

        self.root.protocol("WM_DELETE_WINDOW", self.close_map)

        self.root.bind("<B1-Motion>", self.mouse_drag)


        # control buttons
        reset_btn = tk.Button(self.ctrl_frame, text='Reset', command=self.reset, bg='red')
        reset_btn.grid(column=0, row=0, sticky='nsew')

        tick_btn = tk.Button(self.ctrl_frame, text='Tick', command=self.tick)
        tick_btn.grid(column=0, row=1, sticky='nsew')


        # allow user to change speed of autoplay
        speed_label = tk.Label(self.ctrl_frame, text='Tick delay')
        speed_label.grid(column=2, row=0, sticky='nsew', ipadx=5, ipady=5)

        self.speed_input = tk.Entry(self.ctrl_frame, width=3, justify='center')
        self.speed_input.grid(column=2, row=1, sticky='nsew')
        self.speed_input.insert(0, '0.25')

        # toggle autoplay
        autoplay_label = tk.Label(self.ctrl_frame, text='Autoplay')
        autoplay_label.grid(column=3, row=0, sticky='nsew', ipadx=5, ipady=5)

        self.play_btn = tk.Button(self.ctrl_frame, text='\u25B6', command=self.play)
        self.play_btn.grid(column=3, row=1, sticky='nsew')


        self.is_playing = threading.Event()


        # toggle edge walls
        self.solid_walls = tk.IntVar()
        solid_walls_toggle = tk.Checkbutton(self.ctrl_frame, text='Toggle Edge walls', variable=self.solid_walls)
        solid_walls_toggle.grid(column=4, row=0, sticky='nsew')

        info_label = tk.Label(self.ctrl_frame, text='Dimensions and edge walls require restart to take effect!')
        info_label.grid(column=4, row=1, sticky='nsew', ipadx=5, ipady=5)


        # allow users to input new width
        dimension_label = tk.Label(self.ctrl_frame, text='Dimensions')
        dimension_label.grid(column=1, row=0, sticky='nsew', ipadx=5, ipady=5)

        self.dimension_input = tk.Entry(self.ctrl_frame, width=3, justify='center')
        self.dimension_input.grid(column=1, row=1, sticky='nsew')
        self.dimension_input.insert(0, '15x15')



        self.ctrl_frame.pack(anchor='w')

        self.log_panel = tkst.ScrolledText(self.root, width=30, height=2)
        self.log_panel.pack()


        self.setup_main() # initialise map itself - seperate function for reset button

        self.root.mainloop()


    def setup_main(self):

        self.dot_frame = tk.Frame(self.root)
        self.open_map = True


        # get new dimensions from input
        try:
            new = self.dimension_input.get()
            new = new.split('x')
            self.width = int(new[0])
            self.height = int(new[1])

        except:
            self.log("Not valid dimensions, defaulted to 15x15")
            self.width = 15
            self.height = 15


        self.dot_grid = {}      # this is the grid of buttons to be interacted with.
        self.ended = False


        # create the button grid
        for y in range(self.height):
            for x in range(self.width):
                name = str(x) + ',' + str(y)
                self.dot_grid[name] = dot(self, x, y, name)


        # introduce dots to their neighbours
        for y in range(self.height):
            for x in range(self.width):
                name = str(x) + ',' + str(y)
                self.dot_grid[name].find_neighbours()

        self.dot_frame.pack(anchor='n')

    def close_map(self):
        '''
        handler if the user closes the map window
        '''

        self.open_map = False
        self.root.destroy()


    def mouse_drag(self, drag_event):
        '''
        Allows the user to click and drag to trigger multiple walls at once
        '''
        self.mouse_dragging = True # flag to prevent rapid toggling of buttons
        self.root.winfo_containing(drag_event.x_root, drag_event.y_root).invoke()
        self.mouse_dragging = False



    def tick(self):
        '''
        update the living neighbour count for each cell then perform one tick
        this is done in this order because otherwise it breaks
        '''
        for y in range(self.height):
            for x in range(self.width):
                name = str(x) + ',' + str(y)
                self.dot_grid[name].find_count()

        for y in range(self.height):
            for x in range(self.width):
                name = str(x) + ',' + str(y)
                self.dot_grid[name].tick()

        #self.log(self.solid_walls.get())



    def play(self):
        '''
        Function to create a thread to run the autoplay function.
        This allows the play button to toggle autoplay
        '''
        if not self.is_playing.is_set():

            # get new dimensions from input
            try:
                new = self.speed_input.get()
                self.time_tick = float(new)

            except Exception as e:
                self.log("Not valid speed, defaulted to 0.25s")
                self.time_tick = 0.25
                raise e

            play_thread = threading.Thread(target=self.auto_play, daemon=True)
            play_thread.start()
            self.is_playing.set()

            self.play_btn.config(text='\u23F8')

        else:
            self.is_playing.clear()
            self.play_btn.config(text='\u25B6')
            


    def auto_play(self):
        '''
        Continuously iterate through at a constant speed.
        '''

        while True:
            self.tick()
            sleep(self.time_tick)

            if not self.is_playing.is_set():
                break



    def reset(self):
        self.dot_frame.destroy()

        self.setup_main()



    def log(self, message):
        message = str(message)
        message += '\n'
        self.log_panel.insert(tk.INSERT, message)


f = life_map()