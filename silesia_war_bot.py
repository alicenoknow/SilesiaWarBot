import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import random
from datetime import datetime
import pickle
from paths import *


def get_date():
    date = datetime.now()
    minute = date.minute
    if minute < 10:
        minute = "0" + str(minute)
    return str(date.day) + "/" + str(date.month) + "/" + str(date.year) + " " + str(date.hour) + ":" + str(minute) + " "


class BOT:
    def __init__(self, counties, curr_neighbours, conquered, neighbours):
        self.counties = counties.copy()
        self.conquered = conquered
        self.curr_neighbours = curr_neighbours
        self.neighbours = neighbours
        self.counties_num = 36
        self.attacker = None
        self.territory = None
        self.defender = None

    def find_attacker(self):
        players = []
        scores = []
        for i in range(self.counties_num):
            if len(self.conquered[i]) > 0:
                players.append(i)
                scores.append(self.get_score(i))
        sum_scores = sum(scores)
        scores = list(map(lambda x: x / sum_scores, scores))
        self.attacker = np.random.choice(players, p=scores)

    def find_defender(self):
        for owner in range(self.counties_num):
            if self.territory in self.conquered[owner]:
                self.defender = owner
                return

    def find_territory(self):
        self.territory = random.choice(self.curr_neighbours[self.attacker])

    def is_gameover(self):
        for i in range(self.counties_num):
            if len(self.conquered[i]) == self.counties_num:
                return True
        return False

    def is_in_game(self, county):
        return len(self.conquered[county]) > 0

    def reset(self):
        self.curr_neighbours = self.neighbours
        for i in range(self.counties_num):
            self.conquered[i] = [i]
            self.counties.loc[i, 'OWNER'] = i
        res = open(res_txt, 'w+')
        res.write("")
        res.close()
        rhtml = open(res_html, 'w+')
        rhtml.write("")
        rhtml.close()
        shtml = open(scores_html, 'w+')
        shtml.write("")
        shtml.close()

    def save_ranking(self):
        scores = []
        conq = []

        for i in range(self.counties_num):
            scores.append(self.get_score(i))
            conq.append(len(self.conquered[i]))
        ranking = pd.DataFrame(self.counties['NAME_2'])
        ranking.loc[:, 'Score'] = scores
        ranking.loc[:, 'Counquered territories'] = conq
        ranking.to_csv("ranking.csv", sep='\t', index=False)

        with open(scores_html, "w+") as html:
            html.write("<meta charset=\"utf-8\">\n<link rel=\"stylesheet\" href=\"../static/style.css\">")
            html.write("<table id=\"sheet\">")
            html.write("\n<tr><th>County</th><th>Score</th><th>Number of territories</th></tr>\n")

            for i in range(self.counties_num):
                if scores[i] == 0:
                    continue
                name = self.counties.loc[i, 'NAME_2']
                score = round(scores[i], 3)
                conq_num = conq[i]
                row = "<tr><td>" + str(name) + "</td>\n<td>" + str(score) + "</td>\n<td>" + str(
                    conq_num) + "</td>\n</tr>"
                html.write(row)
            html.write("</table>")
        html.close()

    def get_score(self, county):
        territories = self.conquered[county]
        score = 0
        for ter in territories:
            score += float(self.counties.loc[ter, 'Score'])
        return score

    def remove_territory_from_loser(self):
        self.conquered[self.defender].remove(self.territory)
        self.update_neighbours(self.defender)

    def add_territory_to_winner(self):
        self.counties.loc[self.territory, 'OWNER'] = self.attacker
        self.conquered[self.attacker].append(self.territory)
        self.update_neighbours(self.attacker)

    def update_neighbours(self, county):
        curr = set()
        for subter in self.conquered[county]:
            for i in range(len(self.neighbours[subter])):
                curr.add(self.neighbours[subter][i])
        self.curr_neighbours[county] = [x for x in curr if x not in self.conquered[self.attacker]]

    def plot_map(self):
        self.counties["Result"] = None
        for i in self.conquered[self.attacker]:
            self.counties.loc[i, "Result"] = "Conqueror"
        self.counties.loc[self.territory, "Result"] = "Conquered"
        fig, ax = plt.subplots(1)
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)
        fig.tight_layout()
        self.counties.plot(ax=ax, column="OWNER", cmap="gist_ncar", edgecolor='grey', alpha=0.4)
        self.counties.plot(ax=ax, column="Result", cmap='spring', edgecolor='black', legend=True)
        plt.savefig(img_path)
        del self.counties["Result"]

    def save_result(self):
        date = get_date()
        msg = "\n<br /><br />" + date + " The county " + str(
            self.counties.loc[self.attacker, 'NAME_2']) + " conquered territory " \
                                                          "of " + str(
            self.counties.loc[self.territory, 'NAME_2']) + " previously owned by county " + str(
            self.counties.loc[self.defender, 'NAME_2']) + ". "
        if not self.is_in_game(self.defender):
            msg += "The county " + str(self.counties.loc[self.defender, 'NAME_2']) + " was completely destroyed."
        if self.is_gameover():
            msg += " All territories have been conquered by county " + str(
                self.counties.loc[self.attacker, 'NAME_2']) + ". Game over."

        with open(res_txt, 'r') as contents:
            save = contents.read()
        with open(res_txt, 'w') as contents:
            contents.write(msg)
        with open(res_txt, 'a') as contents:
            contents.write(save)
        contents.close()

        with open(res_html, "w+") as html:
            html.write("<meta charset=\"utf-8\"> \n<link rel=\"stylesheet\" href=\"../static/style.css\">")
            html.write("\n<p id=\"includedContent\">\n")
            html.write(msg)
            html.write(save)
            html.write("\n\n</p>")
        html.close()

    def close(self):
        self.counties.to_file(shp)
        with open(neigh_data, 'wb') as fd1:
            pickle.dump(self.neighbours, fd1)
        with open(currneigh_data, 'wb') as fd2:
            pickle.dump(self.curr_neighbours, fd2)
        with open(conq_data, 'wb') as fd3:
            pickle.dump(self.conquered, fd3)
        fd1.close()
        fd2.close()
        fd3.close()

    def simulate(self):
        self.find_attacker()
        self.find_territory()
        self.find_defender()
        self.remove_territory_from_loser()
        self.add_territory_to_winner()
        self.plot_map()
        self.save_result()
        self.save_ranking()
