from game import *


def main():
    agent1 = Agent(0.4)
    agent2 = Agent(0.5)
    user = User()
    mng = GameManager(agent1, agent2)
    for _ in range(20000):
        mng.shuffle()
        mng.start()
        while not mng.is_end():
            mng.do_turn()

    agent1.debug = True
    mng = GameManager(agent1, user)
    while True:
        mng.shuffle()
        mng.start()
        while not mng.is_end():
            mng.do_turn()


if __name__ == '__main__':
    main()
