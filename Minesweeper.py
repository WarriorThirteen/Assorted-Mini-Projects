# is minesweeper
# by Jad


##The algorithm will store a seperate grid with numbers, flags, hidden and revealed
##spaces. The flag's numbers will be independently edited and decrement when
##neighbouring spaces are flagged. There will be a function that returns how many
##unrevealed tiles are bordering a given space and a second which returns their addresses
##
##Based on this, if the number is equal to the number of unseen squares bordering,
##they will all be flagged






import tkinter as tk
import tkinter.scrolledtext as tkst
from random import randint


class make_map:

    class dot:

        def __init__(self, owner, x, y, name):
            self.btn = tk.Button(owner.root, bg='black', text='   ')
            self.btn.bind('<Button-1>', self.update_btn)
            self.btn.bind('<Button-3>', self.flag)
            
            self.x = x
            self.y = y

            self.btn.grid(column=x, row=y, ipadx=5, sticky='nesw')

            self.name = name
            self.count = 0

            self.is_mine = False
            self.flagged = False

            self.owner = owner
            # this allows editing of the enclosing 'map''s variables within the button's function call as it has a reference point to call attributes from

        def flag(self, y):
            if not self.flagged:
                self.flagged = True
                self.btn.config(text=u'\u2690', bg='#d3d3d3')
                self.owner.flagged += 1
                self.owner.remaining -= 1

                if self.is_mine:
                    self.is_found = True

                self.owner.check_win()

            else:
                self.flagged = False
                self.owner.flagged -= 1
                self.owner.remaining += 1

                if self.is_mine:
                    self.is_found = False
                
                self.update_btn(0)

            self.owner.update_status()

        def update_btn(self, _):
            if self.is_mine:
                self.owner.end()
            else:
                self.reveal()

        def reveal(self):
            self.btn.config(bg='white', fg=self.owner.num_colours[self.count])
            self.owner.searched_nodes.append(self.name)

            self.owner.remaining -= 1

            if self.count:
                self.btn.config(text=self.count)
            
            else:

                for dx in (-1, 0, 1):

                    target_x = self.x + dx
                    if target_x >= self.owner.width or target_x < 0:
                        continue

                    for dy in (-1, 0, 1):

                        target_y = self.y + dy
                        if target_y >= self.owner.height or target_y < 0:
                            continue

                        target_name = str(target_x) + ',' + str(target_y)
                        if target_name in self.owner.searched_nodes or target_name == self.name:
                            continue

                        if not self.owner.dot_grid[target_name].is_mine:
                            self.owner.dot_grid[target_name].reveal()

            self.owner.update_status()

        def trigger(self):
            if self.is_mine:
                if self.is_found:
                    self.btn.config(bg='#ffa500') # orange
                else:
                    self.btn.config(bg='red')

                self.btn.config(text=u'\u2055')

        def increment(self):
            if not self.is_mine:
                self.count += 1
                self.btn.config(text=self.count)

        def make_mine(self):
            if self.is_mine:
                raise TypeError

            self.is_mine = True
            self.is_found = False
            self.count = 0

    def __init__(self, width=10, height=10):

        # control panel
        self.ctrl = tk.Tk()
        self.ctrl.title("Controls")

        self.ctrl_frame = tk.Frame(self.ctrl)

        self.num_colours = ['black', 'blue', 'green', 'red', '#00008b', '#800000', 'cyan', 'black', '#808080']

        self.flagged = 0
        self.remaining = 0

        # control buttons
        reset_btn = tk.Button(self.ctrl_frame, text='Reset', command=self.reset, bg='red')
        reset_btn.grid(column=0, row=0, sticky='nsew')

        debug_btn = tk.Button(self.ctrl_frame, text='End', command=self.end)
        debug_btn.grid(column=0, row=1, sticky='nsew')

        # allow users to input new width
        dimension_label = tk.Label(self.ctrl_frame, text='Dimensions')
        dimension_label.grid(column=1, row=0, sticky='nsew', ipadx=5, ipady=5)

        self.dimension_input = tk.Entry(self.ctrl_frame, width=3, justify='center')
        self.dimension_input.grid(column=1, row=1, sticky='nsew')
        self.dimension_input.insert(0, '10x10')

        # allow users to change mine count
        mine_label = tk.Label(self.ctrl_frame, text='No. Mines')
        mine_label.grid(column=2, row=0, sticky='nsew', ipadx=5, ipady=5)

        self.mine_input = tk.Entry(self.ctrl_frame, width=3, justify='center')
        self.mine_input.grid(column=2, row=1, sticky='nsew')
        self.mine_input.insert(0, '20')


        self.flagged_label = tk.Label(self.ctrl_frame, text='{} places flagged'.format(self.flagged))
        self.flagged_label.grid(column=3, row=0, sticky='nsew')

        self.remaining_label = tk.Label(self.ctrl_frame, text='{} places remaining'.format(self.remaining))
        self.remaining_label.grid(column=3, row=1, sticky='nsew')


        self.ctrl_frame.pack(anchor='w')

        self.log_panel = tkst.ScrolledText(self.ctrl, width=30, height=2)
        self.log_panel.pack()




        self.setup_main() # initialise map itself - seperate function for reset button

        self.ctrl.mainloop()

    def setup_main(self):

        self.root = tk.Frame(self.ctrl)

        # for node searching - when clicked, non mines expose surrounding non mines
        # this is done in a way that will cause infinite recursion if nodes not recorded
        self.searched_nodes = []


        # get new dimensions from input
        try:
            new = self.dimension_input.get()
            new = new.split('x')
            width = int(new[0])
            height = int(new[1])

        except:
            self.log("Not valid dimensions, defaulted to 10x10")
            width = 10
            height = 10
        
        self.width = width
        self.height = height

        # get new bomb count
        try:
            self.mine_count = int(self.mine_input.get())
            assert self.mine_count < width * height

        except:
            self.log("Invalid mine count entered, defaulted to 20")
            self.mine_count = 20

        self.remaining = height * width

        self.dot_grid = {}      # this is the grid of buttons to be interacted with.
        self.ended = False


        # create the button grid
        for y in range(height):
            for x in range(width):
                name = str(x) + ',' + str(y)
                self.dot_grid[name] = self.dot(self, x, y, name)

        # populate the grid with mines
        placed_mines = 0
        self.mine_locs = [] # to be triggered after game over

        while placed_mines < self.mine_count:
            bomb_target_x = randint(0, width)
            bomb_target_y = randint(0, height)
            bomb_target_name = str(bomb_target_x) + ',' + str(bomb_target_y)
            try:
                self.dot_grid[bomb_target_name].make_mine()
            except:
                continue

            placed_mines += 1
            self.mine_locs.append(bomb_target_name)

            # increment surrounding tiles
            for dx in (-1, 0, 1):

                target_x = bomb_target_x + dx
                if target_x >= width or target_x < 0:
                    continue

                for dy in (-1, 0, 1):

                    target_y = bomb_target_y + dy
                    if target_y >= height or target_y < 0:
                        continue

                    target_name = str(target_x) + ',' + str(target_y)
                    if target_name == bomb_target_name:
                        continue
                    self.dot_grid[target_name].increment()

        self.update_status()
        self.root.pack(anchor='n')

    def reset(self):
        self.root.destroy()

        self.flagged = 0
        self.remaining = 0

        self.setup_main()

    def log(self, message):
        message = str(message)
        message += '\n'
        self.log_panel.insert(tk.INSERT, message)

    def update_status(self):
        self.flagged_label.config(text='{} places flagged'.format(self.flagged))
        self.remaining_label.config(text='{} places remaining'.format(self.remaining))

    def check_win(self):
        if self.flagged == self.mine_count:
            self.win()

    def win(self):
        self.log("You WON!!")
        self.end()

    def end(self):
        if not self.ended:
            self.log('Game Over')
            self.ended = True
            for place in self.mine_locs:
                #self.log(place)
                self.dot_grid[place].trigger()


f = make_map()
