from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return 'Вы пытаетесь выстрелить за доску!'


class BoardUsedException(BoardException):
    def __str__(self):
        return 'Вы уже стреляли в эту клетку'


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, start_ship, length, orientation):
        self.start_ship = start_ship
        self.length = length
        self.orientation = orientation
        self.lives = length
    
    @property
    def dots(self):
        ship_dots = []
        for count in range(self.length):
            cur_x = self.start_ship.x
            cur_y = self.start_ship.y
            
            if self.orientation == 0:
                cur_x += count
            
            elif self.orientation == 1:
                cur_y += count
            
            ship_dots.append(Dot(cur_x, cur_y))
        
        return ship_dots
    
    def shoot(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hide=False):
        self.hide = hide
        
        self.count = 0
        
        self.field = [['O'] * 6 for _ in range(6)]
        
        self.busy = []
        self.ships = []
    
    def add_ship(self, ship):
        
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = '■'
            self.busy.append(d)
        
        self.ships.append(ship)
        self.contour(ship)
            
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = '*'
                    self.busy.append(cur)
    
    def __str__(self):
        res = '  1 2 3 4 5 6'
        for i, row in enumerate(self.field, 1):
            res += f'\n{i} {" ".join(row)}'
        
        if self.hide:
            res = res.replace('■', 'O')
        return res
    
    def out(self, d):
        return not((0 <= d.x < 6) and (0 <= d.y < 6))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        
        if d in self.busy:
            raise BoardUsedException()
        
        self.busy.append(d)
        
        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Корабль уничтожен!')
                    return False
                else:
                    print('Корабль ранен!')
                    return True
        
        self.field[d.x][d.y] = '*'
        print('Мимо!')
        return False
    
    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    
    def ask(self):
        raise NotImplementedError()
    
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход соперника: {d.x + 1} {d.y + 1}')
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input('Ваш ход - ').split()
            
            if len(cords) != 2:
                print('Введите 2 координаты!')
                continue
            
            x, y = cords
            
            if not(x.isdigit()) or not(y.isdigit()):
                print('Введите числа!')
                continue
            
            x, y = int(x), int(y)
            
            return Dot(x-1, y-1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hide = True
        
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def __str__(self):
        print('''Приветствуем вас в игре Морской бой.
Правила всем известны, но мы повторим их, что бы не упустить ничего:
1. Доска строится случайным образом, как ваша, так и соперника;
2. Нельзя стрелять в одну и ту же клетку;
3. Нельзя стрелять в рядом стоящие клетки, когда корабль уничтожен;
4. Нельзя стрелять в клетки, стоящие за пределами поля.
Удачной вам игры, пусть победит везучий!''')
        input('Нажмите Enter что бы продолжить.')
    
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board
    
    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board()
        attempts = 0
        for i in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, 6), randint(0, 6)), i, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def loop(self):
        num = 0
        while True:
            print('~' * 20 + '\nВаше игровое поле:')
            print(self.us.board)
            print('~' * 20 + '\nИгровое поле соперника:')
            print(self.ai.board)
            if num % 2 == 0:
                print('~' * 20 + '\nВаш черед ходить!')
                repeat = self.us.move()
            else:
                print('~' * 20 + '\nЧеред соперника!')
                repeat = self.ai.move()
            if repeat:
                num -= 1
            
            if self.ai.board.count == 7:
                print('~' * 20 + '\nВы победили!!!')
                break
            
            if self.us.board.count == 7:
                print('~' * 20 + '\nК сожалению, компьютер был удачливее вас!!!')
                break
            num += 1
            
    def start(self):
        self.__str__()
        self.loop()
            
            
s_t_g = Game()
s_t_g.start()
