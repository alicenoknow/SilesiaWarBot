import logging
import os
from silesia_war_bot import *
from paths import *


def init():
    try:
        counties = gpd.read_file(shp)
        with open(currneigh_data, 'rb') as fd2:
            curr_neighbours = pickle.load(fd2)
        with open(conq_data, 'rb') as fd3:
            conquered = pickle.load(fd3)
        with open(neigh_data, 'rb') as fd1:
            neighbours = pickle.load(fd1)
        fd1.close()
        fd2.close()
        fd3.close()

    except Exception as e:
        msg = "Cannot read required files! " + str(e)
        logging.error(msg)
        exit()
    return BOT(counties, curr_neighbours, conquered, neighbours)


def simulate():
    war_bot = init()
    try:
        if war_bot.is_gameover():
            war_bot.close()
            exit()

        war_bot.simulate()
        war_bot.close()
    except:
        war_bot.close()


def reset():
    war_bot = init()
    war_bot.reset()
    war_bot.close()
    if os.path.exists(img_path):
        os.remove(img_path)

