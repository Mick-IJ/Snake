from ipy_lib import SnakeUserInterface


class Coordinate:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def coordinate(self):
        return str(self.x), str(self.y)

    def shift(self, x_shift, y_shift):
        self.x += x_shift
        self.y += y_shift

    def change_coordinate(self, new_x, new_y):
        old_x = self.x
        old_y = self.y
        self.x = new_x
        self.y = new_y
        return old_x, old_y


class CoordinateRow:
    def __init__(self, row):
        self.row = row

    def append(self, coordinate):
        self.row.append(coordinate)

    def move_head(self, jump=0):
        global direction
        distance = 1 + jump
        if direction == 'r':
            self.row[0].shift(distance, 0)
            if self.row[0].x >= X_RANGE:
                self.row[0].x = 0
        elif direction == 'l':
            self.row[0].shift(-distance, 0)
            if self.row[0].x <= -1:
                self.row[0].x = X_RANGE - 1
        elif direction == 'u':
            self.row[0].shift(0, -distance)
            if self.row[0].y <= -1:
                 self.row[0].y = Y_RANGE - 1
        else:  # direction == 'd':
            self.row[0].shift(0, distance)
            if self.row[0].y >= Y_RANGE:
                self.row[0].y = 0

    def move_coordinates(self, jump=0):
        old_x = self.row[0].x
        old_y = self.row[0].y
        self.move_head(jump=jump)
        for element in self.row:
            if element != self.row[0]:
                old_x, old_y = element.change_coordinate(old_x, old_y)

    def check_coordinate(self, coordinate):
        result = False
        for element in self.row:
            if element.coordinate() == coordinate.coordinate():
                result = True
        return result


# CONSTANTS
X_RANGE = 32
Y_RANGE = 24
ui = SnakeUserInterface(X_RANGE, Y_RANGE)
fps = 5
count = 0
direction = 'r'
snake = CoordinateRow([Coordinate(1, 0), Coordinate(0, 0)])
walls_list = CoordinateRow([])


def change_direction(event=None, mystic=False):
    global direction
    if event is None:  # In case of level
        direction_change = direction
    else:  # event is an event:
        direction_change = event.data

    if mystic:
        direction_change = direction_randomizer(direction_change)

    if direction_change == 'l' and direction != 'r':
        direction = 'l'
    elif direction_change == 'r' and direction != 'l':
        direction = 'r'
    elif direction_change == 'u' and direction != 'd':
        direction = 'u'
    elif direction_change == 'd' and direction != 'u':
        direction = 'd'


def direction_randomizer(direction_change):
    if direction_change == 'l':
        return 'r'
    elif direction_change == 'r':
        return 'd'
    elif direction_change == 'd':
        return 'u'
    else:
        return 'l'


def select_free_coordinate():
    global snake, walls_list
    while True:
        food_x = ui.random(X_RANGE)
        food_y = ui.random(Y_RANGE)
        possible_position = Coordinate(food_x, food_y)
        if not snake.check_coordinate(possible_position) and not walls_list.check_coordinate(possible_position):
            return possible_position


def create_coordinaterow(a_list, split_on=' '):
    row = CoordinateRow([])
    for raw_coordinate in a_list:
        coordinates = raw_coordinate.split(split_on)
        the_coordinate = Coordinate(coordinates[0], coordinates[1])
        row.append(the_coordinate)
    return row


def place_walls():
    global walls_list
    for wall_piece in walls_list.row:
        ui.place_transparent(wall_piece.x, wall_piece.y, 3)


def place_snake():
    global snake
    for snake_piece in snake.row:
        if snake_piece != snake.row[0]:
            ui.place_transparent(snake_piece.x, snake_piece.y, 2)
        else:
            ui.place(snake_piece.x, snake_piece.y, ui.SNAKE)


def check_game_over(start=0, step=1):
    global snake, walls_list
    for wall_piece in walls_list.row[start::step]:
        if snake.row[0].coordinate() == wall_piece.coordinate():
            game_over()
    for snake_piece in snake.row[1:]:
        if snake.row[0].coordinate() == snake_piece.coordinate():
            game_over()


def game_over():
    global snake
    ui.wait(500)
    print('GAME OVER')
    print('Your score was: %i') % (len(snake.row) * 100 - 200)
    ui.close()


def create_start_step(mystic=False):
    if mystic:
        start = ui.random(2)  # becomes 0 or 1
        step = ui.random(2) + 2  # becomes 2 or 3
    else:
        start = 0
        step = 1
    return start, step


def level_info(level=0):
    global snake, walls_list, direction
    filename = 'SnakeInput%i.txt' % level
    data = open(filename).read()
    text = data.split('=')

    snake_data = text[0].splitlines()
    snake = create_coordinaterow(snake_data)

    direction = text[1].lower()
    change_direction()

    walls_data = text[2].splitlines()
    walls_list = create_coordinaterow(walls_data)


def animation_function(food_coordinate, start, step, jump=0):
    global snake
    ui.clear()
    ui.place(food_coordinate.x, food_coordinate.y, ui.FOOD)
    place_walls()

    snake.move_coordinates(jump=jump)
    check_game_over(start=start, step=step)
    place_snake()


def food_eaten(food_coordinate, heroic=False):
    global fps, snake, walls_list, count
    if snake.row[0].coordinate() == food_coordinate.coordinate():
        count = 0
        snake.append(food_coordinate)

        if heroic:
            for i in range(len(snake.row) - 2):
                wall_coordinate = select_free_coordinate()
                walls_list.append(wall_coordinate)

        food_coordinate = select_free_coordinate()  # new food coordinate

        if len(snake.row) % 3 == 0:
            fps += 2
    return food_coordinate


def process_alarm(food_coordinate, start, step, heroic):
    global count
    count += 1
    animation_function(food_coordinate, start, step)
    food_coordinate = food_eaten(food_coordinate, heroic)

    if heroic and count % 30 == 0:
        walls_list.append(food_coordinate)
        food_coordinate = select_free_coordinate()
        count = 0

    return food_coordinate


def process_event(event, food_coordinate, jump, start, step, heroic, mystic):
    global fps, snake, walls_list
    if event.name == 'arrow':
        change_direction(mystic=mystic, event=event)

    if jump > 0 and event.name == 'other' and event.data == 'space':
        animation_function(food_coordinate, start, step, jump=jump)
        food_coordinate = food_eaten(food_coordinate, heroic)

    if event.name == 'alarm':
        food_coordinate = process_alarm(food_coordinate, start, step, heroic)

    return food_coordinate


def the_snake_game(level=0, heroic=False, mystic=False, jump=0):
    global fps
    if 4 >= level > 0:
        level_info(level)

    food_coordinate = select_free_coordinate()
    start, step = create_start_step(mystic)

    while True:
        ui.show()
        ui.set_animation_speed(fps)
        event = ui.get_event()
        food_coordinate = process_event(event, food_coordinate, jump, start, step, heroic, mystic)


the_snake_game(level=0, jump=1, heroic=True)
