""" Simple Snake Game

Author: Matthew Chiang

Description: This program allows the user to play a simple Snake Game. At the beginning of the game, a green Snake,
    initial1y 1 unit long, is randomly placed in an nxn plain. The snake grows by 1 unit as it eats red apples that are
    generated in random locations. A snake of length l has a head coordinate at snake[0]. As the head travels in
    direction d, the coordinate snake[1] is updated to the have the original coordinates of snake[0]. This idea follows
    for the rest of the inner indices of the snake. At position i, 0 <= i < l, in the snake, the next position of
    snake[i] is snake[i-1].

Rules:
    - Arrow keys change the direction of the snake.
        - If the length of the snake is greater than 1, then the snake's direction can not be changed 180 degrees.
    - Eating apples grows the snake by 1 unit and increases the score by 1.
    - If the snake collides with itself, or goes out of the maps bounds, the snake dies and the game stops.

Goal:
    - Navigate the snake to eat as many apples as possible without killing the snake. The score of the game is
      determined by the size of the snake.

Resources:
    - Libraries: random, time, math, graphics
    - Graphics library tutorial: https://www.youtube.com/channel/UC9-58hKjwQiD-RkH6Qu1lFQ/search?query=graphics
    - Graphics pdf: https://mcsp.wartburg.edu/zelle/python/graphics/graphics.pdf

"""

import math
import random
import playsound
from graphics import *


class Board:
    difficulties = [.15, .12, .09, .06, .03]

    def __init__(self, board_size, snake_width=25, high_score=0, score_multiplier=2):
        self.board_size = board_size
        self.snakey = Snake(random.randint(0, math.floor(int(self.board_size * .75))),
                            random.randint(0, self.board_size - 1))
        self.apple = self.new_apple_coordinates()
        self.snake_width = snake_width
        self.direction = 'Right'
        self.quit = False
        self.score = 0
        self.high_score = high_score
        self.score_multiplier = score_multiplier + 1
        self.difficulty = self.difficulties[score_multiplier]

    def start_game(self):
        '''
        Runs a game of snake

        :return: integer value representing the score of the game
        '''
        # variables used in game loop
        dead = False
        key_index = ['Right', 'Left', 'Up', 'Down', 'q']
        grow = False

        # Sets up graphical window to be used as the game board
        win = GraphWin('Snake Game', self.board_size * self.snake_width, (self.board_size + 2) * self.snake_width)
        win.setBackground(color_rgb(25, 25, 25))

        # Shows score at bottom of screen
        score_text = Text(Point((self.board_size * self.snake_width) / 2, (self.board_size + 1) * self.snake_width), '')
        score_text.setTextColor(color_rgb(255, 255, 255))
        score_text.setText('Score: ' + str(self.score))
        score_text.draw(win)

        # Creates line to mark the bottom boundary
        ln = Line(Point(0, self.board_size * self.snake_width),
                  Point(self.board_size * self.snake_width, self.board_size * self.snake_width))
        ln.setWidth(2)
        ln.setFill(color_rgb(255, 255, 255))
        ln.draw(win)

        # creates the first rectangle
        init_point = [self.snakey.get_head()[0], self.snakey.get_head()[1]]
        rectangles = [self.get_scaled_rect(init_point)]
        rectangles[0].draw(win)

        # creates a graphical representation of the apple
        apple_graphic = self.new_scaled_apple()
        apple_graphic.draw(win)

        # gives one second before game starts
        time.sleep(1)

        # determines time that the game starts
        time1 = time.time()

        try:
            # runs the game loop. ends if snake 'dies' or player quits the game
            while not dead and not self.quit:
                time2 = time.time()
                elapsed_time = time2 - time1
                print(elapsed_time)

                # checks keyboard input (q or arrow keys)
                self.update_dir(win, key_index)

                # controls the rate at which the game is played
                if elapsed_time >= self.difficulty:
                    time1 = time2
                    if self.quit: break
                    self.draw_snake(rectangles, win, grow)

                    # updates snake movement
                    self.snakey.move(self.direction, grow)
                    grow = False

                    # checks keyboard input (q or arrow keys)
                    self.update_dir(win, key_index)

                    # checks if snake hits apple
                    if self.apple_snake_collision(self.snakey.get_head()):
                        # update the apple
                        apple_graphic.undraw()
                        apple_graphic = self.new_scaled_apple()
                        apple_graphic.draw(win)

                        # updates score
                        self.score += self.score_multiplier
                        score_text.setText('Score: ' + str(self.score))

                        # indicates that the snake will grow
                        grow = True

                    # checks keyboard input (q or arrow keys)
                    self.update_dir(win, key_index)

                    # checks if snake has reached 'death' conditions
                    if self.snake_out_of_bounds(self.snakey.get_head()) or self.snake_self_collision():
                        dead = True
                        break

                win.checkMouse()
            self.display_game_over(win)
            k = win.getKey()
            while k != 'Enter' and k != 'Return':
                k = win.getKey()
        except:
            pass
        win.close()
        return self.score

    def update_dir(self, win, key_index):
        '''
        Checks for key strokes and compares it valid key_index values

        :param win: window used for checking key strokes
        :param key_index: list of valid key strokes
        :return: None
        '''
        key = win.checkKey()
        if key in key_index:
            if key == 'q':
                self.quit = True
            else:
                self.direction = key

    def display_game_over(self, win):
        '''
        Displays the game over message

        :param win: GraphWin object that the text will be displayed on
        :return: None
        '''
        # calculate center of the screen
        x = int(win.getWidth() / 2)
        y = int(win.getHeight() / 2)

        # format and draw text
        text = Text(Point(x, y), "        GAME OVER!        \nclick <Enter> to continue")
        text.setTextColor(color_rgb(201, 30, 30))
        text.setSize(30)
        text.draw(win)

    def new_scaled_apple(self):
        '''
        updates the apple coordinates to random positions and creates a new apple to be eaten

        :return: Circle object - graphical representation of the apple
        '''
        new_coor = self.new_apple_coordinates()
        self.apple = new_coor
        r = int(self.snake_width * .4)
        apple_g = Circle(Point((self.apple[0] + .5) * self.snake_width, (self.apple[1] + .5) * self.snake_width), r)
        apple_g.setFill(color_rgb(201, 30, 30))
        apple_g.setOutline(color_rgb(0, 0, 0))
        return apple_g

    def draw_snake(self, rects, win, grow):
        '''
        re-draws the snake

        :param rects: a list of all of the rectangle objects that are a graphical representation of the snake's body
        :param win: a GraphWin object - the graphic game board
        :return: None
        '''
        # creates new body element of snake
        rect = self.get_scaled_rect(self.snakey.get_head())
        rect.draw(win)
        # checks if the length of the snake body is changed
        if not grow:
            rects.pop(0).undraw()
        rects.append(rect)

    def get_scaled_rect(self, pos):
        '''
        Creates a new Rectangle object with the right formatting and scaling, locatec at pos.

        :param pos: The x, y coordinates of the rectangle
        :return: a Rectangle object
        '''
        point1 = Point(pos[0] * self.snake_width, pos[1] * self.snake_width)
        point2 = Point((pos[0] + 1) * self.snake_width, (pos[1] + 1) * self.snake_width)
        rect = Rectangle(point1, point2)
        rect.setFill(color_rgb(26, 204, 2))
        rect.setOutline(color_rgb(0, 0, 0))
        return rect

    def in_body(self, pos):
        '''
        Determines if the pos is in the body of the snake

        :param pos: [x, y] where x andy y are integers
        :return: True if [x, y] in self.snakey.body, False otherwise
        '''
        body = self.snakey.body
        for e in body:
            if e == pos:
                return True
        return False

    def new_apple_coordinates(self):
        '''
        Randomly generates new location for the apple

        :return: x, y position of the apple
        '''
        # generates random location for apple
        rand = [random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)]

        # checks to make sure that apple isn't overlapping snake
        while self.in_body(rand):
            rand = [random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)]

        return rand

    def apple_snake_collision(self, snake_head):
        '''
        Detects if the snake is colliding with the apple

        :param snake_head: x, y location of the snakes head
        :return: True if snake is colliding with apple, False otherwise
        '''
        # snake collides with apple if the snake's head coordinate matches the apples
        if snake_head == self.apple:
            return True
        return False

    def snake_out_of_bounds(self, snake_head):
        '''
        Checks whether or not the snake is out of bounds

        :param snake_head: x, y location of the snakes head
        :return: True if snake is out-of-bounds of the game board, False otherwise
        '''
        # checks the snake's head's x coordinate
        if snake_head[0] < 0 or snake_head[0] >= self.board_size:
            return True
        # checks the snake's head's y coordinate
        if snake_head[1] < 0 or snake_head[1] >= self.board_size:
            return True
        return False

    def snake_self_collision(self):
        '''
        Checks if the snake is colliding with itself

        :return: True if snake collides with itself, False otherwise
        '''
        body = self.snakey.body
        if self.snakey.get_head() in body[:len(body) - 2]:
            return True
        return False


class Snake:
    # this is all illegal successive direction combinations
    no_nos = ['RightLeft', 'LeftRight', 'UpDown', 'DownUp']

    def __init__(self, x_pos, y_pos, direction='Right'):
        self.direction = direction  # the direction of the snake
        self.body = []  # this will contain the coordinates of every block of the snake
        self.body.append([x_pos, y_pos])
        self.size = len(self.body)  # size of the snake
        self.directions = {'Right': (1, 0), 'Left': (-1, 0), 'Up': (0, -1), 'Down': (0, 1)}  # movement vectors

    def move(self, new_dir='', grow=False):
        '''
        updates the snakes coordinates to move it one position.
        :param new_dir: what direction to move the snake in
        :param grow: if True, grow snake size by one, otherwise, length remains the same
        :return: the new position of the head of the snake
        '''
        s = str(self.direction) + str(new_dir)
        # default for new_dir should be self.direction
        if new_dir == '':
            new_dir = self.direction

        # cannot turn 180 degrees if snake is longer than size 1
        elif self.size > 1 and s in self.no_nos:
            new_dir = self.direction
        # calculates the new position of the snakes head and adds it to the body
        head = self.body[self.size - 1]
        new_x = head[0] + self.directions[new_dir][0]
        new_y = head[1] + self.directions[new_dir][1]
        self.body.append([new_x, new_y])

        # determines if snakes body gets longer or remains the same
        if not grow:
            self.body.pop(0)
        else:
            self.size += 1

        # stores the current direction
        self.direction = new_dir

        return [new_x, new_y]

    def get_head(self):
        '''
        gets the x, y coordinates of the head of the snake
        :return: x y coordinates in the form [x, y]
        '''
        return self.body[self.size - 1]


def point_in_rect(point, rect, text, text_color=color_rgb(200,200,200)):
    '''
    Determines if the given point is in the given rectangle and updates the rectangle and the rectangle text accorrdingly

    :param point: Point object from the graphics.py library
    :param rect: Rectangle object from the graphics.py library
    :param text: Text object from the graphics.py library
    :return: True if point is in rect, False otherwise
    '''
    if point is None: return False

    # gets all points needed for calculation
    x, y = point.getX(), point.getY()
    x0, y0 = rect.getP1().getX(), rect.getP1().getY()
    x1, y1 = rect.getP2().getX(), rect.getP2().getY()

    # performs calculation
    if x0 < x < x1 and y0 < y < y1:
        rect.setFill(color_rgb(35, 35, 35))
        text.setTextColor(text_color)
        return True
    return False

def run_game():
    '''
    Creates a game menu. Allows player to repeatedly play the snake game

    :return: None
    '''
    quit_game = False
    highscore = 0
    t_start = 0
    while not quit_game:
        if time.time() - t_start > 57:
            t_start = time.time()
            playsound.playsound('Undertale_music.mp3', False)

        window = GraphWin("Let's play snake", 500, 450)
        window.setBackground(color_rgb(25, 25, 25))

        # creates snake logo
        img = Image(Point(250, 175), 'Snake_Graphic.png')
        img.draw(window)

        # sets up the start button
        button = make_button([250, 300], 100, 50, text='Start!')
        for e in button: e.draw(window)

        # sets up difficulty boxes
        diff_buttons, x_base = [], 150
        colors = [ color_rgb(26, 204, 2), color_rgb(166, 201, 8), color_rgb(201, 198, 8), color_rgb(201, 127, 8), color_rgb(201, 8, 8)]
        for i in range(5): diff_buttons.append(make_button([x_base + (50*i), 366], 50, 50, text=str(i+1), color=colors[i], text_color=color_rgb(0,0,0)))
        for b in diff_buttons:
            for e in b: e.draw(window)

        # set up high score text
        high_score_txt = Text(Point(80, 25), "High-score: " + str(highscore))
        high_score_txt.setSize(20)
        high_score_txt.setTextColor(color_rgb(255, 255, 255))
        high_score_txt.draw(window)

        # set up title text
        title = Text(Point(250, 75), "LETS PLAY...")
        title.setSize(30)
        title.setTextColor(color_rgb(26, 204, 2))
        title.draw(window)

        # detects when the a button is pressed
        start = False
        diff = 2
        try:
            while not start:
                mouse = window.checkMouse()
                start = point_in_rect(mouse, button[0], button[1])
                for i in range(len(diff_buttons)):
                    if point_in_rect(mouse, diff_buttons[i][0], diff_buttons[i][1]):
                        if i != diff:
                            diff_buttons[diff][0].setFill(colors[diff])
                            diff_buttons[diff][1].setTextColor(color_rgb(0,0,0))
                        diff = i

            # runs start animation
            animation(window, 25)
        except:
            window.close()
            break

        # closes old window
        window.close()

        # plays the game
        board = Board(18, 40, highscore, score_multiplier=diff)
        highscore = max(board.start_game(), highscore)


def make_button(x_y, width, height, color=color_rgb(200, 0, 0), text='', text_size=20,
                text_color=color_rgb(255, 255, 255)):
    '''
    Creates a button

    :param x_y: [(int), (int)] center coordinate of the button
    :param width: int - width of the button
    :param height: int height of the button
    :param color: a graphics.py color
    :param text: str - text of the button
    :param text_size: int - size of the text
    :param text_color: color of the button text
    :return:
    '''
    # set up the start button
    button = Rectangle(Point(x_y[0] - int(width / 2), x_y[1] - int(height / 2)),
                       Point(x_y[0] + int(width / 2), x_y[1] + int(height / 2)))
    button.setFill(color)

    # set up start button text
    button_txt = Text(Point(x_y[0], x_y[1]), text)
    button_txt.setSize(text_size)
    button_txt.setTextColor(text_color)
    return [button, button_txt]


def animation(win, snake_width):
    '''
    Performs a little animation
    :param win: GraphWin object that the animation will go on
    :param snake_width: integer representing pixel width of animation snake
    :return: None
    '''
    snakes = []
    # determines the number of snakes and how long each snake will be
    num_snakes = int(win.getWidth() / snake_width) + 1
    snake_length = int(win.getHeight() / snake_width) + 1

    # finds the coordinates for all parts of each snake
    for x in range(num_snakes):
        snake = []
        for y in range(snake_length):
            if x % 2 == 0:
                snake.append([x, y])
            else:
                snake.append([x, snake_length - y - 1])
        snakes.append(snake)

    # displays the snake to the screen
    for snake in snakes:
        for body in snake:
            rect = Rectangle(Point(body[0] * snake_width, body[1] * snake_width),
                             Point((body[0] + 1) * snake_width, (body[1] + 1) * snake_width))
            rect.setFill(color_rgb(26, 204, 2))
            rect.setOutline(color_rgb(0, 0, 0))
            rect.draw(win)


if __name__ == '__main__':
    run_game()