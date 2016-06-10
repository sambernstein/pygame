"""
Sam Bernstein, 2015

Controls:

Use mouse to slid rows / columns, s and d to toggle
between different board sizes, a to scramble, 0 to
start and stop the AI, l to toggle between animating
and not animating the AI, and p to pause and unpause.


"""

 
import pygame
from pygame.locals import *
import random
import copy
import math
from time import sleep

 
# Define some colors
BLACK = (0, 0, 0)


PI = 3.141592653

pygame.init()
 
# Set the width and height of the screen [width, height]
size = (1000, 800)
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("Slider Puzzle")
 
# Loop until the user clicks the close button.
done = False
pause = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()

def gray(c):
    return (c, c, c)

BACKGROUND = gray(100)

# tile Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (235, 0, 0)
GREEN = (0, 204, 0)
ORANGE = (235,145,0)
BLACK_C = gray(30)
YELLOW = (255,255,0)
MAGENTA = (255,0,255)
PERU = (150,75,25)
PURPLE = (128, 0, 128)
SALMON = (255, 160, 122)
ORCHID = (218, 112, 214)
TURQUOISE = (0, 134, 139)
BANANA =  (227, 207, 87)

tile_colors = [WHITE, BLUE, ORANGE, MAGENTA, RED, BLACK_C, GREEN, YELLOW, SALMON, PURPLE, PERU, ORCHID, TURQUOISE, BANANA]


def write_text(text, length, height, x, y, text_color = WHITE, size = 40): # used for dispalying level header
    font_size = size*int(length//len(text))
    myFont = pygame.font.SysFont("Calibri", font_size)
    myText = myFont.render(text, 1, text_color)
    screen.blit(myText, ((x+length/2) - myText.get_width()/2, (y+height/2) - myText.get_height()/2))

def draw_check(x, y, size, color = (255,215,0)): # draws the checks for each level indicating completion
    angle_down = math.radians(45)
    angle_up   = math.radians(65)

    l_wid = size//2
    down_len = 1.0*size
    up_len   = 2.5*size

    bottom_x = x + math.cos(angle_down)*down_len
    bottom_y = y + math.sin(angle_down)*down_len

    pygame.draw.line(screen, color, (x, y), (bottom_x, bottom_y), l_wid)
    pygame.draw.line(screen, color, (bottom_x, bottom_y), (bottom_x + math.cos(angle_up)*up_len, bottom_y - math.sin(angle_up)*up_len), l_wid)

speed_factor = .9
speed_factor_factor = 1.1 # factor for changing the speed factor

class SlidingLine():

    def __init__(self, is_row, index, displacement, level):
        self.is_row = is_row # is a row or not - boolean
        self.index = index
        self.tiles_displacement = displacement # how many tile lengths to move

        self.speed = int(speed_factor*(level.dim[0]+level.dim[1])**1.4)
        self.velocity = self.speed*math.copysign(1.0, displacement)

        self.line = []

        if self.is_row:
            row = index
            for column in range(level.dim[1]):
                self.line.append(level.board[row][column])
        else:
            column = index
            for row in range(level.dim[0]):
                self.line.append(level.board[row][column])

        self.target_displacement = self.tiles_displacement*level.total_d
        self.displacement_achieved = 0

    def update(self):
        self.displacement_achieved += self.velocity

    def shift_line(self, disp = 1):
        dim = len(self.line)
        while disp > dim:
            disp -= dim

        line_copy = [self.line[ind] for ind in range(dim)]

        if disp > 0:
            for ind in range(dim):
                self.line[ind] = copy.deepcopy(line_copy[(ind - disp)])

        elif disp < 0:
            for ind in range(dim):
                self.line[ind] = copy.deepcopy(line_copy[(ind - disp)%dim])


tile_size = 60

outlined_squares = 0 # Boolean that determines the design denoting the solved locations of each color
animating_ai = 1 # Boolean
constant_move_time = 1 # Boolean

start_with_ai_running = False

mouse_pos = (0,0)
start_mouse_pos = (0,0)
dragging_factor = 2

class Level():

    def __init__(self, square_dim, board_square_dim, tile_size = tile_size):
        """
        square_dim: the number of squares in each same-colored square
        board_square_dim:   (n, m) where n x m is the num_rows of squares x num_columns of squares
        """
        self.board_square_dim = board_square_dim
        self.s = square_dim  # how many tiles make up each side of each square
        self.squares = board_square_dim[0]*board_square_dim[1] # total number of colors / same-colored subsquares
        self.dim = (self.s * board_square_dim[0], self.s * board_square_dim[1]) # actual row and column dimensions of board

        if self.dim[0]%2==0:
            self.row_displacement_range = [disp for disp in range(int(-.5*self.dim[0]), int(.5*self.dim[0] + 1)) if disp != 0]
        else:
            self.row_displacement_range = [disp for disp in range(int(-.5*self.dim[0]), int(.5*self.dim[0])) if disp != 0]

        if self.dim[1]%2==0:
            self.col_displacement_range = [disp for disp in range(int(-.5*self.dim[1]), int(.5*self.dim[1] + 1)) if disp != 0]
        else:
            self.col_displacement_range = [disp for disp in range(int(-.5*self.dim[1]), int(.5*self.dim[1])) if disp != 0]

        self.tile_size = tile_size
        self.margin = (tile_size)//4
        self.haf_mar = self.margin//2
        self.total_d = self.tile_size + self.margin
        self.haf_total_d = self.total_d * 0.5

        self.outline_width = int(.4*self.margin)
        self.outline_length = self.s*self.total_d

        self.level_colors = []
        num_tiles_per_sqr = self.s**2
        for f in range(self.squares):
            self.level_colors.extend([tile_colors[f]]*num_tiles_per_sqr) # make a list of the right number of each color

        self.board = []
        all_colors = self.level_colors
        for row in range(self.dim[0]):
            self.board.append([])
            for col in range(self.dim[1]):
                self.board[row].append(all_colors.pop(random.randint(0, len(all_colors) - 1))) # randomly assign colors to tiles


        self.x = .5*(size[0] - len(self.board[0])*(self.total_d))
        self.y = .5*(size[1] - len(self.board[0])*(self.total_d))

        self.ai_running = start_with_ai_running

        self.connectedness = 0
        self.temporary_connectedness = 0
        self.max_connectedness = 0 # connectedness value when solved

        corner_conn = 2*4*self.squares
        if self.board_square_dim[0] == 1:
            corner_conn = 3*4*self.squares

        edge_conn = 0
        internal_conn = 0
        if self.s > 2:
            edges_per_side = self.s - 2
            edge_conn = 3*4*edges_per_side*self.squares
            if self.board_square_dim[0] == 1:
                edge_conn = 3*edges_per_side*2*self.squares + 4*edges_per_side*2*self.squares
            internal_conn = 4*(edges_per_side**2)*self.squares

        self.max_connectedness = (corner_conn + edge_conn + internal_conn)/2

        self.sliding = [] # an ordered list of all SlidingLine objects

        self.click_tile = None # (row, col)
        self.dragging = False
        self.moving_row = None # int
        self.moving_col = None # int

        self.moving_row_disp = 0
        self.moving_col_disp = 0

        self.aligning_rows = None # list of ints
        self.aligning_cols = None # list of ints

        self.moves = 0
        self.moves_per_decision = 1
        self.last_move = {'row': False, 'index': 0}
        self.past_moves = []

        self.row_streak = 0
        self.col_streak = 0

        self.max_consecutive_row_moves = self.dim[0] - 1
        self.max_consecutive_column_moves = self.dim[1] - 1

        self.puzzle_solved = False

    def mouse_col(self, x):
        return int((x - self.x)//self.total_d)

    def mouse_row(self, y):
        return int((y - self.y)//self.total_d)

    def set_click_tile(self, mouse_pos):
        x, y = mouse_pos[0], mouse_pos[1]

        if self.x <= x <= self.x + self.dim[1]*self.total_d - self.margin and self.y <= y <= self.y + self.dim[0]*self.total_d - self.margin:
            levels[current].click_tile = (self.mouse_row(y), self.mouse_col(x))

    def collapse_click_tile(self):
        if self.click_tile != None:
            if mouse_pos != start_mouse_pos:
                x_dist = abs(mouse_pos[0] - start_mouse_pos[0])
                y_dist = abs(mouse_pos[1] - start_mouse_pos[1])
                if x_dist > y_dist:
                    self.moving_row = self.click_tile[0]
                else:
                    self.moving_col = self.click_tile[1]
                self.click_tile = None
                self.dragging = True

    def reset_dragging(self):
        self.click_tile = None
        self.dragging = False
        self.moving_row = None
        self.moving_col = None
        self.moving_row_disp = 0
        self.moving_col_disp = 0

    def align_nearest(self):

        if self.moving_row != None:
            horiz_displacement = dragging_factor*(mouse_pos[0] - start_mouse_pos[0]) + self.moving_row_disp

            if horiz_displacement > self.haf_total_d:
                self.shift_row(self.moving_row, 1)
            if horiz_displacement < -self.haf_total_d:
                self.shift_row(self.moving_row, -1)
            
        elif self.moving_col != None:
            vert_displacement = dragging_factor*(mouse_pos[1] - start_mouse_pos[1]) + self.moving_col_disp

            if vert_displacement > self.haf_total_d:
                self.shift_column(self.moving_col, 1)
            elif vert_displacement < -self.haf_total_d:
                self.shift_column(self.moving_col, -1)

    def scramble(self):
        self.moves = 0

        self.level_colors = []
        num_tiles_per_sqr = self.s**2
        for f in range(self.squares):
            self.level_colors.extend([tile_colors[f]]*num_tiles_per_sqr)

        self.board = []
        all_colors = self.level_colors
        for row in range(self.dim[0]):
            self.board.append([])
            for col in range(self.dim[1]):
                self.board[row].append(all_colors.pop(random.randint(0, len(all_colors) - 1)))


    def shift_column(self, column, disp = 1):

        if self.last_move['row'] or not(self.last_move['row']) and self.last_move['index'] != column: # move counter
            self.moves += 1
            self.last_move = {'row': False, 'index': column}
            self.past_moves.append(self.last_move)

        while disp > self.dim[0]:
            disp -= self.dim[0]

        column_copy = [self.board[row][column] for row in range(self.dim[0])]

        if disp > 0:
            for row in range(self.dim[0]):
                self.board[row][column] = copy.deepcopy(column_copy[(row - disp)])

        elif disp < 0:
            for row in range(self.dim[0]):
                self.board[row][column] = copy.deepcopy(column_copy[(row - disp)%self.dim[0]])

    def shift_row(self, row, disp = 1):
        if not(self.last_move['row']) or self.last_move['row'] and self.last_move['index'] != row: # move counter
            self.moves += 1
            self.last_move = {'row': True, 'index': row}
            self.past_moves.append(self.last_move)

        while disp > self.dim[1]:
            disp -= self.dim[1]

        row_copy = [self.board[row][column] for column in range(self.dim[1])]

        if disp > 0:
            for column in range(self.dim[1]):
                self.board[row][column] = copy.deepcopy(row_copy[(column - disp)])

        elif disp < 0:
            for column in range(self.dim[1]):
                self.board[row][column] = copy.deepcopy(row_copy[(column - disp)%self.dim[1]])

    def pretend_shift_column(self, column, disp = 1):
        new_board = copy.deepcopy(self.board)

        while disp > self.dim[0]:
            disp -= self.dim[0]

        column_copy = [self.board[row][column] for row in range(self.dim[0])]

        if disp > 0:
            for row in range(self.dim[0]):
                new_board[row][column] = copy.deepcopy(column_copy[(row - disp)])

        elif disp < 0:
            for row in range(self.dim[0]):
                new_board[row][column] = copy.deepcopy(column_copy[(row - disp)%self.dim[0]])

        return new_board

    def pretend_shift_row(self, row, disp = 1):
        new_board = copy.deepcopy(self.board)

        while disp > self.dim[1]:
            disp -= self.dim[1]

        row_copy = [self.board[row][column] for column in range(self.dim[1])]

        if disp > 0:
            for column in range(self.dim[1]):
                new_board[row][column] = copy.deepcopy(row_copy[(column - disp)])

        elif disp < 0:
            for column in range(self.dim[1]):
                new_board[row][column] = copy.deepcopy(row_copy[(column - disp)%self.dim[1]])

        return new_board

    def ai_shift_column(self, column, displacement):
        if self.last_move['row'] or not(self.last_move['row']) and self.last_move['index'] != column:
            self.moves += 1
            self.last_move = {'row': False, 'index': column}
            self.past_moves.append(self.last_move)
            
        if animating_ai:
            self.sliding.append(SlidingLine(False, column, displacement, self))

        self.shift_column(column, displacement)
        self.past_moves.append(self.last_move)
        self.col_streak += 1
        self.row_streak = 0

    def ai_shift_row(self, row, displacement):
        if not(self.last_move['row']) or self.last_move['row'] and self.last_move['index'] != row:
            self.moves += 1
            self.last_move = {'row': True, 'index': row}
            self.past_moves.append(self.last_move)

        if animating_ai:
            self.sliding.append(SlidingLine(True, row, displacement, self))

        self.shift_row(row, displacement)
        self.past_moves.append(self.last_move)
        self.row_streak += 1
        self.col_streak = 0

    def set_solved(self): # returns True if solved and False if not solved

        i = 0
        for sqr_row in range(self.board_square_dim[0]):
            for sqr_col in range(self.board_square_dim[1]):
                for row in range(self.s*sqr_row, self.s*(sqr_row + 1)):
                    for col in range(self.s*sqr_col, self.s*(sqr_col + 1)):
                        if self.board[row][col] != tile_colors[i]:
                            self.puzzle_solved = False
                            return
                i += 1

        self.puzzle_solved = True

    def solve(self): # sets the board to solved (used as a testing shorcut)

        i = 0
        for sqr_row in range(self.board_square_dim[0]):
            for sqr_col in range(self.board_square_dim[1]):
                for row in range(self.s*sqr_row, self.s*(sqr_row + 1)):
                    for col in range(self.s*sqr_col, self.s*(sqr_col + 1)):
                        self.board[row][col] = tile_colors[i]
                i += 1


    def get_neighbor(self, tile, disp): # returns the color of nearby tiles
        return self.board[tile[0] + disp[0]][tile[1] + disp[1]]

    def calculate_connectedness(self, hypo_board = None):
        
        if hypo_board == None: # hypotheical board
            board = self.board
            self.connectedness = 0
        else:
            board = hypo_board

        self.temporary_connectedness = 0

        def check_adjacent(tile, d_x, d_y):
            next = ( (tile[0] + d_y)%self.dim[0], (tile[1] + d_x)%self.dim[1])
            if board[next[0]][next[1]] == board[tile[0]][tile[1]]:
                self.temporary_connectedness += 1
                
        for row in range(self.dim[0]):
            for column in range(self.dim[1]):
                tile = (row, column)
                check_adjacent(tile, 0, 1)
                check_adjacent(tile, 1, 0)

        if hypo_board == None:
            self.connectedness = self.temporary_connectedness
        else:
            return self.temporary_connectedness

    def test_all_moves(self):
        self.calculate_connectedness()

        best_possible_move = [True, 0, 0]
        max_delta_conn = -10000000
        current_move_connectedness = 0 # the connectedness of the resulting board of the current board shift

        delta_conn = 0

        for move_number in range(1, self.moves_per_decision + 1):

            if not(self.row_streak >= self.max_consecutive_row_moves):
                for row in range(self.dim[0]):
                    if not(self.last_move['row'] and self.last_move['index'] == row):
                        for displacement in self.row_displacement_range:
                            new_board = self.pretend_shift_row(row, displacement)
                            delta_conn = self.calculate_connectedness(new_board) - self.connectedness

                            if move_number == self.moves_per_decision:
                                if delta_conn > max_delta_conn:
                                    if not(new_board == self.board):
                                        max_delta_conn = delta_conn
                                        best_possible_move = [True, row, displacement]

            if not(self.col_streak >= self.max_consecutive_column_moves):
                for column in range(self.dim[1]):
                    if not(not self.last_move['row'] and self.last_move['index'] == column):
                        for displacement in self.col_displacement_range:
                            new_board = self.pretend_shift_column(column, displacement)

                            if move_number == self.moves_per_decision:
                                delta_conn = self.calculate_connectedness(new_board) - self.connectedness

                                if delta_conn > max_delta_conn:
                                    if not(new_board == self.board):
                                        max_delta_conn = delta_conn
                                        best_possible_move = [False, column, displacement]
                                        

        return best_possible_move


    def draw_moving_tiles_ai(self, slide_obj):

        slide_obj.update()

        if self.moving_col != None:
            column = self.moving_col

            vert_displacement = slide_obj.displacement_achieved + self.moving_col_disp

            for row in range(len(self.board)): # draw each tile in column being dragged
                left = self.x + column*self.total_d
                top = self.y + row*self.total_d + vert_displacement

                over = self.tile_size
                down = self.tile_size

                TILE_COLOR = slide_obj.line[row]

                if top > self.y + self.dim[0]*self.total_d - self.haf_mar: # if top of tile is below bottom edge
                    self.moving_col_disp += -self.total_d

                    slide_obj.shift_line(1)

                    self.draw_moving_tiles_ai(slide_obj)
                    break

                elif top < self.y - self.tile_size - self.haf_mar: # if top of tile is above top edge
                    self.moving_col_disp += self.total_d

                    slide_obj.shift_line(-1)

                    self.draw_moving_tiles_ai(slide_obj)
                    break

                if row == self.dim[0] - 1:
                    if vert_displacement > self.haf_mar:
                        down = self.tile_size - vert_displacement + self.haf_mar

                        pygame.draw.rect(screen, TILE_COLOR,[left, self.y - self.haf_mar, over, vert_displacement - self.haf_mar])

                elif row == 0:
                    if vert_displacement < -self.haf_mar:
                        top = self.y - self.haf_mar
                        down = self.tile_size + vert_displacement + self.haf_mar

                        pygame.draw.rect(screen, TILE_COLOR,[left, self.y + (self.dim[0])*self.total_d + vert_displacement, over, -vert_displacement - self.haf_mar])

                    elif vert_displacement < 0:
                        top = self.y + vert_displacement
                        down = self.tile_size
                
                pygame.draw.rect(screen, TILE_COLOR,[left, top, over, down], 0)

        elif self.moving_row != None:
            row = self.moving_row

            horiz_displacement = slide_obj.displacement_achieved + self.moving_row_disp

            for column in range(len(self.board[0])):
                left = self.x + column*self.total_d + horiz_displacement
                top = self.y + row*self.total_d 

                over = self.tile_size
                down = self.tile_size

                TILE_COLOR = slide_obj.line[column]

                if left > self.x + self.dim[1]*self.total_d - self.haf_mar:
                    self.moving_row_disp += -self.total_d

                    slide_obj.shift_line(1)

                    self.draw_moving_tiles_ai(slide_obj)
                    break

                elif left < self.x - self.tile_size - self.haf_mar:
                    self.moving_row_disp += self.total_d

                    slide_obj.shift_line(-1)

                    self.draw_moving_tiles_ai(slide_obj)
                    break

                if column == self.dim[1] - 1:
                    if horiz_displacement > self.haf_mar:
                        over = self.tile_size - horiz_displacement + self.haf_mar

                        pygame.draw.rect(screen, TILE_COLOR,[self.x - self.haf_mar, top, horiz_displacement - self.haf_mar, down])

                elif column == 0:
                    if horiz_displacement < -self.haf_mar:
                        left = self.x - self.haf_mar
                        over = self.tile_size + horiz_displacement + self.haf_mar

                        pygame.draw.rect(screen, TILE_COLOR,[self.x + (self.dim[1])*self.total_d + horiz_displacement, top, -horiz_displacement - self.haf_mar, down])

                    elif horiz_displacement < 0:
                        left = self.x + horiz_displacement
                        over = self.tile_size

                pygame.draw.rect(screen, TILE_COLOR,[left, top, over, down], 0)

    def draw_board(self):

        if not outlined_squares:
            i = 0
            for row in range(self.board_square_dim[0]):
                for col in range(self.board_square_dim[1]):

                    SHADE = list(tile_colors[i])
                        
                    for f in range(len(SHADE)):
                        SHADE[f] = (3*SHADE[f])/5
                        if SHADE[f] > 255:
                            SHADE[f] = 255

                    NEW = tuple(SHADE)

                    start_x = self.x + col*self.outline_length - self.haf_mar
                    start_y = self.y + row*self.outline_length - self.haf_mar

                    side_l = self.outline_length

                    pygame.draw.rect(screen, NEW, [start_x, start_y, side_l, side_l])

                    i += 1

        if self.dragging and not self.ai_running:
            if self.moving_col != None:
                column = self.moving_col

                vert_displacement = dragging_factor*(mouse_pos[1] - start_mouse_pos[1]) + self.moving_col_disp

                for row in range(len(self.board)): # draw each tile in column being dragged
                    left = self.x + column*self.total_d
                    top = self.y + row*self.total_d + vert_displacement

                    over = self.tile_size
                    down = self.tile_size

                    TILE_COLOR = self.board[row][column]

                    if top > self.y + self.dim[0]*self.total_d - self.haf_mar: # if top of tile is below bottom edge
                        self.moving_col_disp += -self.total_d

                        self.shift_column(column, 1)

                        self.draw_board()
                        break

                    elif top < self.y - self.tile_size - self.haf_mar: # if top of tile is above top edge
                        self.moving_col_disp += self.total_d

                        self.shift_column(column, -1)

                        self.draw_board()
                        break

                    if row == self.dim[0] - 1:
                        if vert_displacement > self.haf_mar:
                            down = self.tile_size - vert_displacement + self.haf_mar

                            pygame.draw.rect(screen, TILE_COLOR,[left, self.y - self.haf_mar, over, vert_displacement - self.haf_mar])

                    elif row == 0:
                        if vert_displacement < -self.haf_mar:
                            top = self.y - self.haf_mar
                            down = self.tile_size + vert_displacement + self.haf_mar

                            pygame.draw.rect(screen, TILE_COLOR,[left, self.y + (self.dim[0])*self.total_d + vert_displacement, over, -vert_displacement - self.haf_mar])

                        elif vert_displacement < 0:
                            top = self.y + vert_displacement
                            down = self.tile_size
                    
                    pygame.draw.rect(screen, TILE_COLOR,[left, top, over, down], 0)

            elif self.moving_row != None:
                row = self.moving_row

                horiz_displacement = dragging_factor*(mouse_pos[0] - start_mouse_pos[0]) + self.moving_row_disp

                for column in range(len(self.board[0])):
                    left = self.x + column*self.total_d + horiz_displacement
                    top = self.y + row*self.total_d 

                    over = self.tile_size
                    down = self.tile_size

                    TILE_COLOR = self.board[row][column]

                    if left > self.x + self.dim[1]*self.total_d - self.haf_mar:
                        self.moving_row_disp += -self.total_d

                        self.shift_row(row, 1)

                        self.draw_board()
                        break

                    elif left < self.x - self.tile_size - self.haf_mar:
                        self.moving_row_disp += self.total_d

                        self.shift_row(row, -1)

                        self.draw_board()
                        break

                    if column == self.dim[1] - 1:
                        if horiz_displacement > self.haf_mar:
                            over = self.tile_size - horiz_displacement + self.haf_mar

                            pygame.draw.rect(screen, TILE_COLOR,[self.x - self.haf_mar, top, horiz_displacement - self.haf_mar, down])

                    elif column == 0:
                        if horiz_displacement < -self.haf_mar:
                            left = self.x - self.haf_mar
                            over = self.tile_size + horiz_displacement + self.haf_mar

                            pygame.draw.rect(screen, TILE_COLOR,[self.x + (self.dim[1])*self.total_d + horiz_displacement, top, -horiz_displacement - self.haf_mar, down])

                        elif horiz_displacement < 0:
                            left = self.x + horiz_displacement
                            over = self.tile_size

                    pygame.draw.rect(screen, TILE_COLOR,[left, top, over, down], 0)

        if self.ai_running:
            if len(self.sliding) > 0:
                self.draw_moving_tiles_ai(self.sliding[0])

        # draw regular tiles not being moved
        for row in range(len(self.board)):
            for column in range(len(self.board[0])):
                if not(row == self.moving_row or column == self.moving_col): # only draw if not being dragged

                    left = self.x + column*self.total_d
                    top = self.y + row*self.total_d

                    TILE_COLOR = self.board[row][column]
                    pygame.draw.rect(screen, TILE_COLOR,[left, top, self.tile_size, self.tile_size], 0)

        if outlined_squares:
            i = 0
            for row in range(self.board_square_dim[0]):
                for col in range(self.board_square_dim[1]):

                    OUTLINE_COLOR = tile_colors[i]
                    
                    start_x = self.x + col*self.outline_length - self.outline_width/2
                    start_y = self.y + row*self.outline_length - self.outline_width/2

                    end_x = start_x + self.outline_length - self.haf_mar
                    end_y = start_y + self.outline_length - self.haf_mar

                    pygame.draw.line(screen, OUTLINE_COLOR, (start_x, start_y), (start_x, end_y), self.outline_width)
                    pygame.draw.line(screen, OUTLINE_COLOR, (start_x, end_y), (end_x, end_y), self.outline_width)
                    pygame.draw.line(screen, OUTLINE_COLOR, (end_x, end_y), (end_x, start_y), self.outline_width)
                    pygame.draw.line(screen, OUTLINE_COLOR, (end_x, start_y), (start_x, start_y), self.outline_width)

                    i += 1


levels = [] # for storing every Level object. The data in each level object changes as player plays each level.
levels_const = {} # for storing a permanent copy of every level object

level_index = 0
for square_size in range(2, 4):
    for row_num in range(1, 4):
        for col_num in range(row_num, 4):
            if not(col_num == row_num == 1):
                levels_const[level_index] = Level(square_dim = square_size, board_square_dim = (row_num, col_num))
                level_index += 1

levels_const[level_index] = Level(square_dim = 4, board_square_dim = (1, 2))
"""
levels_const[1] = Level(dim = (3, 6), square_dim = 3, squares = [(0,0),(0,2)])
levels_const[0] = Level(dim = (9, 9), square_dim = 3, squares = [(row, col) for col in range(0,9,3) for row in range(0,9,3)] )
levels_const[2] = Level(dim = (4, 4), square_dim = 2, squares = [(0,0),(0,2),(2,0),(2,2)], tile_size = 50)
"""

for index in levels_const :  
    levels.append(None)
    levels[index] = copy.deepcopy(levels_const[index])

current = 0 # index of current level
number_of_levels = len(levels)

moveron = 1

t = 0
 
# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get():

        if event.type == MOUSEBUTTONDOWN:
            start_mouse_pos = pygame.mouse.get_pos()
            if not levels[current].ai_running:
                levels[current].set_click_tile(start_mouse_pos)

        if event.type == MOUSEBUTTONUP:
            if not levels[current].ai_running:
                levels[current].align_nearest()
                levels[current].reset_dragging()

        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE: # quit game
                pause = False
                done = True

            if event.key == pygame.K_p:
                pause = True

            while pause:

                for event in pygame.event.get():
                     if event.type == pygame.KEYDOWN:

                        if event.key == pygame.K_p:
                            pause = not pause

                        if event.key == pygame.K_ESCAPE: # quit game
                            pause = not pause
                            done = True

            if event.key == pygame.K_0:
                if levels[current].ai_running:
                    levels[current].reset_dragging()    
                levels[current].ai_running = not levels[current].ai_running

            if event.key == pygame.K_l:
                animating_ai = not animating_ai
            if event.key == pygame.K_k:
                constant_move_time = not constant_move_time

            # change levels
            if event.key == pygame.K_d:
                current = (current + 1)%number_of_levels
            if event.key == pygame.K_s:
                current = (current - 1)%number_of_levels

            if event.key == pygame.K_a:
                levels[current].scramble()
            if event.key == pygame.K_z:
                levels[current].solve()

            if event.key == pygame.K_1:
                levels[current].shift_column(1, 2)

            if levels[current].ai_running:
                if event.key == pygame.K_COMMA:
                    speed_factor /= speed_factor_factor
                if event.key == pygame.K_PERIOD:
                    speed_factor *= speed_factor_factor

                if event.key == pygame.K_2:
                    levels[current].ai_shift_column(1, 2)
                if event.key == pygame.K_3:
                    levels[current].ai_shift_column(3, -1)
                if event.key == pygame.K_4:
                    levels[current].ai_shift_column(3, 1)
                if event.key == pygame.K_5:
                    levels[current].ai_shift_row(2, moveron)
                    moveron = (moveron + 1)%levels[current].dim[1]

            if event.key == pygame.K_9:
                print "Max_connectedness:",str(levels[current].max_connectedness)
                print "Connectedness:",str(levels[current].connectedness)

                print(str(levels[current].test_all_moves()))
                
     
    # --- Game logic should go here

    if levels[current].ai_running:
        number_waiting = len(levels[current].sliding)
        
        if number_waiting > 0:
            curr_slide = levels[current].sliding[0]
            if curr_slide.is_row:
                levels[current].moving_row = curr_slide.index
            else:
                levels[current].moving_col = curr_slide.index

            if number_waiting > 1 and not constant_move_time:
                levels[current].sliding[0].velocity = int(levels[current].sliding[0].velocity*number_waiting)

            if abs(curr_slide.displacement_achieved) >= abs(curr_slide.target_displacement):   
                levels[current].reset_dragging()

                levels[current].sliding.pop(0)

        else:
                next_move = levels[current].test_all_moves()
                if next_move[0]: # it's a row
                    levels[current].ai_shift_row(next_move[1], next_move[2])
                else:
                    levels[current].ai_shift_column(next_move[1], next_move[2])

    
    #sleep(0.1) # Time in seconds.

    levels[current].set_solved()
    levels[current].calculate_connectedness()
    if t%100 == 0:
        print "Connectedness:",str(levels[current].connectedness)
        #print "Past moves:",str(levels[current].past_moves)

    mouse_pos = pygame.mouse.get_pos()
    levels[current].collapse_click_tile()


    # First, clear the screen to whatever. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(BACKGROUND)

    # --- Drawing code should go here
    

    levels[current].draw_board()

    if levels[current].puzzle_solved:
        draw_check(10, 300, 40)

    write_text(str(levels[current].moves), len(str(levels[current].moves)), 10, size[0]-80, size[1]/3)


 
    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
    t += 1
 
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
