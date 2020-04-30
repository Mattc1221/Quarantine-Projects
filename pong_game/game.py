import math
import random
import numpy as np

from graphics import *


class Game:
    players = []
    valid_p1_strokes = ['UP', 'DOWN']
    valid_p0_strokes = ['W', 'S']
    ball = None
    scores = [0, 0]
    difficulty = [75, 65, 55, 45, 35]

    def __init__(self, b_width, b_height, d_index):
        self.b_width = b_width
        self.b_height = b_height
        self.p0_dir = 'W'
        self.p1_dir = 'UP'
        self.score_text = self.set_up_scores()
        self.speed = int((self.b_width / self.difficulty[d_index] + self.b_height / self.difficulty[d_index]) / 2)

    def start_game(self):
        win = GraphWin('Pong', self.b_width, self.b_height)
        win.setBackground(color_rgb(0, 0, 0))
        make_space(win, self.b_width, self.b_height)
        self.make_players(self.b_width, self.b_height)
        self.ball = self.make_ball(self.b_width, self.b_height)
        self.draw_all(win)
        for score_t in self.score_text: score_t.draw(win)
        time.sleep(1)
        while True:
            key = win.checkKey()
            if self.process_key_stroke(key):
                end_text = Text(Point(self.b_width/2, self.b_height/2), 'Press <Enter> to continue')
                end_text.setTextColor('white')
                end_text.setSize(20)
                end_text.draw(win)
                break
            g = self.ball.move_ball(self.players[0].get_rect(), self.players[1].get_rect(), self.b_height, self.b_width)
            if g:
                self.update_score(g)
                if self.check_win(win):
                    break
                self.reset(win)
        key = win.checkKey()
        while key != 'Return' and key != 'Enter':
            key = win.checkKey()
        win.checkMouse()
        win.close()

    def set_up_scores(self):
        t1 = Text(Point(int(self.b_width * 4 / 14), int(self.b_height / 8)), '0')
        t1.setSize(20)
        t1.setTextColor('white')
        t2 = Text(Point(int(self.b_width * 10 / 14), int(self.b_height / 8)), '0')
        t2.setSize(20)
        t2.setTextColor('white')
        return [t1, t2]

    def update_score(self, scored):
        if scored:
            if self.ball.circ.getCenter().getX() < self.b_width / 2:
                self.scores[1] += 1
            else:
                self.scores[0] += 1
        self.score_text[0].setText(str(self.scores[0]))
        self.score_text[1].setText(str(self.scores[1]))

    def check_win(self, win):
        index_ = {0: 'Left Player wins\n press <Enter> to continue', 1: 'Right Player wins\n press <Enter> to continue'}
        if self.scores[0] == 5 or self.scores[1] == 5:
            win_text = Text(Point(self.b_width / 2, self.b_height / 2),
                            index_[0 if self.scores[0] > self.scores[1] else 1])
            win_text.setSize(25)
            win_text.setTextColor('white')
            win_text.draw(win)
            return True
        return False

    def process_key_stroke(self, key):
        if key.upper() in self.valid_p1_strokes:
            self.p1_dir = key.upper()
        elif key.upper() in self.valid_p0_strokes:
            self.p0_dir = key.upper()
        if key.upper() == 'Q':
            return True
        self.players[0].move_stick(self.p0_dir, int(self.b_height / 50))
        self.players[1].move_stick(self.p1_dir, int(self.b_height / 50))
        return False

    def draw_all(self, win):
        for p in self.players: p.draw_stick(win)
        self.ball.draw_ball(win)

    def make_players(self, board_width, board_height):
        width, height = int(board_width / 30), int(board_width * 2 / 8)
        x0, x1, y = int(board_width / 7), int(board_width * 6 / 7), int(board_height / 2)
        player0 = Stick(x0, y, width, height, board_width, board_height)
        player1 = Stick(x1, y, width, height, board_width, board_height)
        self.players.append(player0)
        self.players.append(player1)

    def make_ball(self, board_width, board_height):
        return Ball(int(board_width / 2), int(board_height / 2), int(board_width / 70), self.speed)

    def reset(self, win):
        for p in self.players: p.rect.undraw()
        self.players = []
        self.make_players(self.b_width, self.b_height)
        for new_p in self.players: new_p.draw_stick(win)
        self.ball.circ.undraw()
        self.ball = self.make_ball(self.b_width, self.b_height)
        self.ball.draw_ball(win)


class Stick:
    def __init__(self, x, y, width, height, x_range, y_range):
        self.rect = make_rect(x, y, width, height)
        self.x_range = x_range
        self.y_range = y_range

    def move_stick(self, ndir, dist):
        top_y = self.rect.getP1().getY()
        bottom_y = self.rect.getP2().getY()
        move_dict = {'UP': -1, 'DOWN': 1, 'W': -1, 'S': 1}
        if top_y + move_dict[ndir] * dist > int(-self.y_range / 10) \
                and bottom_y + move_dict[ndir] * dist < int(self.y_range * 1.1):
            self.rect.move(0, move_dict[ndir] * dist)
        else:
            self.rect.move(0, 0)

    def draw_stick(self, win):
        self.rect.draw(win)

    def get_rect(self):
        return self.rect


class Ball:
    def __init__(self, x, y, radius, speed):
        self.circ = make_circ(x, y, radius)
        self.speed = speed
        self.movement, self.beta = self.get_random_direction()

    def get_random_direction(self):
        beta = np.radians(random.randint(0, 360))
        x = int(self.speed * np.cos(beta))
        y = int(self.speed * np.sin(beta))
        return [x, y], beta

    def draw_ball(self, win):
        self.circ.draw(win)

    def move_ball(self, rect1, rect2, b_height, b_width):
        goal = self.check_bounce(rect1, rect2, b_height, b_width)
        self.circ.move(self.movement[0], self.movement[1])
        return goal

    def check_bounce(self, rect1, rect2, b_height, b_width):
        r1_p1, r1_p2 = rect1.getP1(), rect1.getP2()
        r2_p1, r2_p2 = rect2.getP1(), rect2.getP2()
        point = self.circ.getCenter()
        # print(point.getX(), self.circ.getRadius(), r1_p1.getX(), r1_p2.getX())

        # check bounce player1
        if int(point.getX()) - self.circ.getRadius() in range(int(r1_p1.getX()), int(r1_p2.getX())) \
                and int(point.getY()) in range(int(r1_p1.getY()), int(r1_p2.getY())):
            self.bounce('h')
            if self.movement[0] < 0:
                self.movement[0] = -self.movement[0]
                self.beta = self.beta % 2 * math.pi
                if self.beta <= math.pi:
                    self.beta = np.radians(180) - self.beta
                else:
                    self.beta = - self.beta
        # check bounce player2
        elif int(point.getX()) + self.circ.getRadius() in range(int(r2_p1.getX()), int(r2_p2.getX())) \
                and int(point.getY()) in range(int(r2_p1.getY()), int(r2_p2.getY())):
            self.bounce('h')
            if self.movement[0] > 0:
                self.movement[0] = -self.movement[0]
                self.beta = self.beta % 2 * math.pi
                if self.beta <= math.pi:
                    self.beta = np.radians(180) - self.beta
                else:
                    self.beta = - self.beta
        # check ceiling and floor
        elif point.getY() - self.circ.getRadius() <= 0:
            self.bounce('v')
            if self.movement[1] < 0:
                self.movement[1] = -self.movement[1]
                self.beta = -self.beta
        elif point.getY() + self.circ.getRadius() >= b_height:
            self.bounce('v')
            if self.movement[1] > 0:
                self.movement[1] = -self.movement[1]
                self.beta = -self.beta
        # check sides
        if point.getX() - self.circ.getRadius() <= 0 or point.getX() + self.circ.getRadius() >= b_width:
            self.bounce('h')
            return True
        return False

    def bounce(self, dir):
        if dir == 'v':
            self.movement[1] = -self.movement[1]
            self.beta = -self.beta
        elif dir == 'h':
            self.movement[0] = -self.movement[0]
            self.beta = self.beta % 2 * math.pi
            if self.beta <= math.pi:
                self.beta = np.radians(180) - self.beta
            else:
                self.beta = - self.beta
        self.variate_vector()

    def variate_vector(self):
        theta = np.radians(random.randint(-5, 5))
        self.beta = theta + self.beta
        c, s = np.cos(self.beta) * self.speed, np.sin(self.beta) * self.speed
        self.movement = [int(c), int(s)]
        print(self.beta, self.movement)


def make_rect(x, y, width=10, height=10, color='white', line_color='white'):
    # set up the start button
    rect = Rectangle(Point(x - int(width / 2), y - int(height / 2)),
                     Point(x + int(width / 2), y + int(height / 2)))
    rect.setFill(color)
    rect.setOutline(line_color)
    return rect


def make_circ(x, y, radius=10, color='white', line_color='white'):
    # set up the start button
    circ = Circle(Point(x, y), radius)
    circ.setFill(color)
    circ.setOutline(line_color)
    return circ


def test():
    game = Game(800, 600, 3)
    game.start_game()


def run_game():
    '''
    Creates a game menu. Allows player to repeatedly play the snake game

    :return: None
    '''
    quit_game = False
    t_start = 0
    while not quit_game:
        # if time.time() - t_start > 57:
        #     t_start = time.time()
        #     playsound.playsound('Undertale_music.mp3', False)

        window = GraphWin("Let's play Pong!", 500, 450)
        window.setBackground(color_rgb(0, 0, 0))

        make_space(window, 500, 450)

        # creates Pong logo
        img = Image(Point(250, 175), 'Space_Pong.png')
        img.draw(window)

        # sets up the start button
        button = make_button([250, 350], 100, 50, text='Start!', color='white', text_color='black')
        for e in button: e.draw(window)

        # sets up difficulty boxes
        diff_buttons, x_base = [], 150
        colors = [color_rgb(255, 255, 255), color_rgb(227, 227, 227), color_rgb(204, 204, 204),
                  color_rgb(179, 179, 179), color_rgb(156, 156, 156)]
        for i in range(5): diff_buttons.append(
            make_button([x_base + (50 * i), 416], 50, 50, text=str(i + 1), color=colors[i],
                        text_color=color_rgb(0, 0, 0)))
        for b in diff_buttons:
            for e in b: e.draw(window)

        # detects when the a button is pressed
        start = False
        diff = 2
        while not start:
            mouse = window.checkMouse()
            start = point_in_rect(mouse, button[0], button[1])
            for i in range(len(diff_buttons)):
                if point_in_rect(mouse, diff_buttons[i][0], diff_buttons[i][1]):
                    if i != diff:
                        diff_buttons[diff][0].setFill(colors[diff])
                        diff_buttons[diff][1].setTextColor(color_rgb(0, 0, 0))
                    diff = i

        # closes old window
        window.close()

        # plays the game
        game = Game(800, 600, diff)
        game.start_game()


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


def point_in_rect(point, rect, text, text_color=color_rgb(200, 200, 200)):
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


def make_space(win, b_width, b_height):
    for i in range(int(b_width * b_height / 500)):
        c = Circle(Point(random.randint(0, b_width, ), random.randint(0, b_height)), random.random() * 2)
        c.setFill('white')
        c.draw(win)

if __name__ == '__main__':
    run_game()