from pandas import read_csv
from numpy import unique
from mpmath import mp, erf
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QTextEdit, QPushButton, QLineEdit, QWidget
from PyQt5.QtCore import Qt
from sys import argv

df = read_csv("data.csv")  # Source: https://drive.google.com/drive/u/0/folders/1gLSw0RLjBbtaNy0dgnGQDAZOHIgCe-HH
champions = unique(df)

mp.dps = 18  # Prevents ZeroDivisionError
sigmas = [0.0] + [float(1 / (1 - erf(i / 2 ** (1 / 2)))) for i in range(10)]  # Converts to float to lose precision


def get_knn(data, champions_b, champions_r, invalid_b, invalid_r, row1, row2):
    connections = 0
    penalty = 0

    for i in range(5):
        if row1[i] == champions_b[i]:
            connections += 1
        if row2[i] == champions_r[i]:
            connections += 1
        if row1[i] in invalid_b:
            penalty += 1
        if row2[i] in invalid_r:
            penalty += 1

    score = sigmas[connections] * (1 - 0.1 * penalty)

    for i in range(5):
        data[row1[i]][i] += score
        data[row2[i]][i+5] += score

    return data


def run_ai():
    data = {i: [0] * 10 for i in champions}

    champions_b = [bt_line.text(), bj_line.text(), bm_line.text(), bb_line.text(), bs_line.text()]
    champions_r = [rt_line.text(), rj_line.text(), rm_line.text(), rb_line.text(), rs_line.text()]

    bans = ban_text.toPlainText().split("\n")

    invalid_b = bans + champions_r
    invalid_r = bans + champions_b

    for _, i in df.iterrows():
        row_b = [i["bt"], i["bj"], i["bm"], i["bb"], i["bs"]]
        row_r = [i["rt"], i["rj"], i["rm"], i["rb"], i["rs"]]

        # Runs knn twice; doubles sensitivity and makes results side-independent
        data = get_knn(data, champions_b, champions_r, invalid_b, invalid_r, row_b, row_r)
        data = get_knn(data, champions_b, champions_r, invalid_b, invalid_r, row_r, row_b)

    texts = [bt_text, bj_text, bm_text, bb_text, bs_text, rt_text, rj_text, rm_text, rb_text, rs_text]

    for j in range(10):
        result = {i: data[i][j] for i in data if i not in champions_b + champions_r + bans}
        result_sorted = dict(sorted(result.items(), key=lambda i: i[1], reverse=True))
        result_output = "\n".join([f"{i}: {j:.1e}" for i, j in result_sorted.items()])
        texts[j].setText(result_output)

    warning = []
    dupe_bans = []
    dupe_champions = []

    for i in bans:
        if i not in champions:
            warning.append(f'Warning: Ban "{i}" is not a Champion!')

        if i in dupe_bans:
            warning.append(f'Warning: Ban "{i}" is a duplicate!')

        dupe_bans.append(i)

    for i in [i for i in champions_b + champions_r if i != ""]:
        if i not in champions:
            warning.append(f'Warning: Pick "{i}" is not a Champion!')

        if i in bans:
            warning.append(f'Warning: Pick "{i}" is a Ban!')

        if i in dupe_champions:
            warning.append(f'Warning: Pick "{i}" is a duplicate!')

        dupe_champions.append(i)

    ai_text.setText("\n".join(warning))


app = QApplication(argv)
app.setStyle("Fusion")
layout = QGridLayout()

ban_label = QLabel("Ban")
ban_label.setAlignment(Qt.AlignCenter)
ban_text = QTextEdit()
layout.addWidget(ban_label, 0, 0)
layout.addWidget(ban_text, 1, 0, 2, 1)

ai_button = QPushButton("Run AI")
ai_button.clicked.connect(run_ai)
ai_text = QTextEdit()
layout.addWidget(ai_button, 3, 0)
layout.addWidget(ai_text, 4, 0, 2, 1)


def get_label(text, column, row):
    label = QLabel(text)
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label, column, row)


get_label("BT", 0, 1)
get_label("BJ", 0, 2)
get_label("BM", 0, 3)
get_label("BB", 0, 4)
get_label("BS", 0, 5)

get_label("RT", 3, 1)
get_label("RJ", 3, 2)
get_label("RM", 3, 3)
get_label("RB", 3, 4)
get_label("RS", 3, 5)


def get_line(column, row):
    line = QLineEdit()
    layout.addWidget(line, column, row)
    return line


bt_line = get_line(1, 1)
bj_line = get_line(1, 2)
bm_line = get_line(1, 3)
bb_line = get_line(1, 4)
bs_line = get_line(1, 5)

rt_line = get_line(4, 1)
rj_line = get_line(4, 2)
rm_line = get_line(4, 3)
rb_line = get_line(4, 4)
rs_line = get_line(4, 5)


def get_text(column, row):
    text = QTextEdit()
    layout.addWidget(text, column, row)
    return text


bt_text = get_text(2, 1)
bj_text = get_text(2, 2)
bm_text = get_text(2, 3)
bb_text = get_text(2, 4)
bs_text = get_text(2, 5)

rt_text = get_text(5, 1)
rj_text = get_text(5, 2)
rm_text = get_text(5, 3)
rb_text = get_text(5, 4)
rs_text = get_text(5, 5)

window = QWidget()
window.setLayout(layout)
window.show()
app.exec()
