import sys
import os
import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QGridLayout, QWidget, QPushButton, QLineEdit, QFileDialog
from PyQt5.QtGui import QCursor
import open3d as o3d
import numpy as np
from main import main
from helper import get_pcd, Stat_removal
import groovedness



app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("3D Object detection")
grid = QGridLayout()
#window.setStyleSheet("background-image: url(./B2.jpg)")    #background:#a8edb9;")
window.setStyleSheet("background: '#03105c'")
widgets = {"logo": [], "button": [], "text": [], "input": []}
Buttons = {}
Results = {"Objecta Nr": [], 
            "Objekta platums (W)": [],
            "Objekta dziļums (D)": [],
            "Objekta augstums (H)": [],
            "Rievainīgima indekss": [],
            "Objekta zemākā rieva": [],
            "Objekta rievu skaits": []}
            
fname = ''
pcd = ''
OB = "Pagaidām nav analizēts nevies punktu mākonis. Objektu nav."
OB_WDH = None
groove_ind = None
Groove_max_height = None
Groove_count = None

def create_BigButton(Text):
  button = QPushButton()
  button.setText(Text)
  button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
  button.setStyleSheet(
    "border: 4px solid '#BC006C';" +
    "border-radius: 15px;" +
    "font-size: 15px;" +
    "background: 'green';" +
    "color : 'white';" +
    "padding: 20px 10px;" +             # <-- Inside a element. (top-bottom (px), sides (px))
    "margin: 5px 50px;}" +              # <-- outside a element.
    "*:hover{background: '#BC006C';"   # <-- after cursor is hovered
  )
  widgets["button"].append(button)
  return button

def createLine(Text):
  Line = QLabel(Text)
  Line.setStyleSheet(
    "border: 4px solid 'black';" +
    "font-size: 10px;" +
    "color: 'white';" +
    "padding-bottom: 2px;" +
    "font-size: 20px;"
  )
  Line.setAlignment(QtCore.Qt.AlignCenter)
  widgets["text"].append(Line)
  return Line

def get_pcd_name():
  global fname, pcd
  # |=== delete pcd_info if there is one ===|
  while True:
    if widgets["text"][-1].text() == "Rādiuss:":
      break
    else:
      widgets["text"][-1].hide(); widgets["text"].pop()
  fname, filter = QFileDialog.getOpenFileName(window, 'Open Point cloud')
  if fname != '': pcd = get_pcd(fname, pcd=True)["pcd"]
  # fpath, fname = os.path.split(fname)

def add_warning():
  pcd_info = createLine("Lūdzu ielādējiet punktu mākoni!")
  pcd_info.setStyleSheet("color: 'red';"+"font-size: 25px;")
  grid.addWidget(pcd_info)

def clear_widgets():
  for widget in widgets: # <-- Button, logo
    if widgets[widget] != []:
      for _ in range(0, len(widgets[widget])): # <-- button1, button2 ...
        widgets[widget][-1].hide()
        widgets[widget].pop()

def Viz_ObFun(OB):
  return lambda: Viz_OB(OB)

def Viz_OB(OB):
  if isinstance(OB, str):
    add_warning()
  else:
    o3d.visualization.draw_geometries([OB])

# +++++++++++++++===================
def Filter():
  global pcd
  if isinstance(pcd, str): add_warning(); return None
  Before = np.shape(np.asarray(pcd.points))
  pcd, _ = Stat_removal(pcd, ratio = 10)
  After = np.shape(np.asarray(pcd.points))
  if After==(): createLine("Pēdējie pcd punktu ir izfiltrēti!"); grid.addWidget(widgets["text"][-1]); return None
  createLine(f"Ir izfiltrēti {Before[0] - After[0]} punkti")
  grid.addWidget(widgets["text"][-1])
  return None

def groovy(OB):
  return groovedness.groove_main(OB)

#def set_text(radius):
#  widgets["button"][3].setText("Notiek analīze ... ")

def _main_(radius):
  global OB, OB_WDH, groove_ind, Groove_max_height, Groove_count
  if fname == '': add_warning(); return None
  OB, OB_WDH, groove_ind, Groove_max_height, Groove_count = main(pcd, radius)
  #widgets["button"][3].setText("PCD analīze")
  #if OB=={}: OB = "Pagaidām nav analizēts nevies punktu mākonis. Objektu nav."
  key_nr = len(OB.keys())
  if key_nr==0:
    createLine("__info__\nObjekti nav atrasti.")
  if key_nr==1:
    After_detection_info = createLine(f"__Info__\nIr atrasts {key_nr} objekts.\nLai apskatītu objektu atcevišķi nospiediet 'Rādīt objektus'.")
  else:
    After_detection_info = createLine(f"__Info__\nIr atrasti {key_nr} objekti.\nLai apskatītu katru objektu atcevišķi nospiediet 'Rādīt objektus'.") 

  After_detection_info.setStyleSheet(
    "color : 'yellow';" +
    "font-size: 30px;"
    "margin: 1px 1px;"                # <-- outside a element.
  )
  widgets["text"].append(After_detection_info)
  grid.addWidget(After_detection_info, 9, 0)

def exit_func():
  sys.exit(app.exec())

def frame1():
  clear_widgets()
  '''
  # |=== image ===|
  image = QPixmap("my_fev.png")
  image = image.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
  logo = QLabel()
  logo.setPixmap(image)
  logo.setAlignment(QtCore.Qt.AlignCenter)
  logo.setStyleSheet("margin: 10px 50px;")
  grid.addWidget(logo, 0, 0)
  '''
  # |=== Info ===|
  r_info = createLine("Pirms punktu-mākoņa analīzes, lūdzu zemāk norādīt rādiusu.\nPēc noklusējuma rādiuss ir 20, bet objektu atpazīšanas uzlabošanai rādiuss var tikt lietots no 5 līdz 40.\nJa objekti atrodas tuvu viens otram ieteicams izmantot mazāku rādiusu.\n")
  r_info.setStyleSheet(
    "font-size: 20px;" +
    "color : 'white';" +
    "padding: 1px 10px;"            # <-- Inside a element. (top-bottom (px), sides (px))
  )
  R_info = QLabel("Rādiuss:")
  R_info.setStyleSheet(
    "font-size: 25px;" +
    "color : 'white';" +
    "padding: 1px 10px;" +             # <-- Inside a element. (top-bottom (px), sides (px))
    "margin: 5px 50px;"                # <-- outside a element.
  )

  grid.addWidget(widgets["text"][-1], 0, 0)
  widgets["text"].append(R_info)
  grid.addWidget(widgets["text"][-1], 1, 0)

  # |=== Radius text line ===|
  Linebox = QLineEdit() # QTextEdit() # Linebox.text()
  Linebox.setPlaceholderText("20")
  Linebox.setStyleSheet(
    "border: 2px solid '#BC006C';" +
    "border-radius: 10px;" +
    "font-size: 30px;" +
    "background: '#f5bdb0';" +
    "color : 'black';" +
    "padding: 20px 10px;" +             # <-- Inside a element. (top-bottom (px), sides (px))
    "margin: 5px 50px;"                # <-- outside a element.
  )
  #Linebox.setAlignment(QtCore.Qt.AlignCenter)
  grid.addWidget(Linebox, 2, 0)
  widgets["input"].append(Linebox)
  grid.addWidget(widgets["input"][-1], 2, 0)

  # |=== Buttons ===|
  button1 = create_BigButton("Izvēlēties punktu mākoni")
  button2 = create_BigButton("PCD vizualizācija")
  button3 = create_BigButton("PCD Trokšņu filtrācija")
  button4 = create_BigButton("PCD analīze")
  button5 = create_BigButton("Rādīt objektus")
  button6 = create_BigButton("Aizvērt programmu")

  #|=== On click ===|
  button1.clicked.connect(get_pcd_name)
  button2.clicked.connect(lambda: Viz_OB(pcd))
  button3.clicked.connect(Filter)
  #button4.clicked.connect(set_text)
  button4.clicked.connect(lambda: _main_(Linebox.text()))
  button5.clicked.connect(frame2)
  button6.clicked.connect(exit_func)

  # |=== Add buttons to grid ===|
  inx = 0
  for _ in range(np.size(widgets["button"])):
    grid.addWidget(widgets["button"][inx], inx+3, 0)
    inx += 1

def frame2():
  clear_widgets()

  if isinstance(OB, str):
    NoOb = createLine(OB)
    widgets["text"].append(NoOb)
    grid.addWidget(NoOb, 1, 0, 1, 2) #(*widget, fromRow, fromColumn, rowSpan, colomnSpan)
    inx = 2
  else:
    # |=== Captions of the table ===|
    Table_Nr = createLine("Objecta Nr")
    W, D, H = createLine("Objekta platums (W)"), createLine("Objekta dziļums (D)"), createLine("Objekta augstums (H)")
    Table_Groove = createLine("Rievainīgima indekss")
    Max_groove_var = createLine("Objekta zemākā rieva")
    groove_count_var = createLine("Objekta rievu skaits")
    Table_Viz = createLine("Vizualizēt objektu")

    grid.addWidget(Table_Nr, 0, 0)
    grid.addWidget(W, 0, 1)
    grid.addWidget(D, 0, 2)
    grid.addWidget(H, 0, 3)
    grid.addWidget(Table_Groove, 0, 4)
    grid.addWidget(Max_groove_var, 0, 5)
    grid.addWidget(groove_count_var, 0, 6)
    grid.addWidget(Table_Viz, 0, 7)
    # |=== create, On click, add to grid ===|
    inx = 1
    for key in OB:
      Nr = createLine(f"{str(inx)}.")
      W_Nr = createLine(str(OB_WDH[f"{inx}"][0]))
      D_Nr = createLine(str(OB_WDH[f"{inx}"][1]))
      H_Nr = createLine(str(OB_WDH[f"{inx}"][2]))
      groove_inx = createLine(str(groove_ind[f"{inx}"]))
      groove_HEIGHT = createLine(str(Groove_max_height[f"{inx}"]))
      groove_COUNT = createLine(str(Groove_count[f"{inx}"]))
      # |=== Result Dictionary ===|
      Results["Objecta Nr"].append(f"{str(inx)}.")
      Results["Objekta platums (W)"].append(str(OB_WDH[f"{inx}"][0]))
      Results["Objekta dziļums (D)"].append(str(OB_WDH[f"{inx}"][1]))
      Results["Objekta augstums (H)"].append(str(OB_WDH[f"{inx}"][2]))      
      Results["Rievainīgima indekss"].append(str(groove_ind[f"{inx}"]))
      Results["Objekta zemākā rieva"].append(str(Groove_max_height[f"{inx}"]))
      Results["Objekta rievu skaits"].append(str(str(Groove_count[f"{inx}"])))

      # |=== Create 2 buttons for vizualization and groovedness analyses ===|
      Viz = QPushButton("Vizualizēt")
      Viz.setStyleSheet("background: 'yellow';")
      widgets["button"].append(Viz)	# <-- add to dict to disable an object later

      # |=== On click event ===|
      Viz.clicked.connect(Viz_ObFun(OB[key]))

      # |=== Add to grid ===|
      #     |== Table ==|
      grid.addWidget(Nr, inx, 0)
      grid.addWidget(W_Nr, inx, 1)
      grid.addWidget(D_Nr, inx, 2)
      grid.addWidget(H_Nr, inx, 3)
      grid.addWidget(groove_inx, inx, 4)
      grid.addWidget(groove_HEIGHT, inx, 5)
      grid.addWidget(groove_COUNT, inx, 6)
      grid.addWidget(Viz, inx, 7)
      inx += 1
    
    info_groove = createLine("|== Info ==|\n\n|== Faila saglabāšana ==|\nPirms saglabāšanas lūdzu norādiet faila nosaukumu teksta lodziņā. \nIr iespējams mainīt mapes. Piemēram var norādīt <mapes nosaukums>/faila nosaukums. \nIzmantojiet '/' zīmi, starp mapes un faila nosaukumu. \n\n|== Rievainīgums ==|\nObjekts skaitās rievains, ja rievainīguma indeks ir virs 2,5.\nJo lielāks indekss, jo rievaināks ir objekts.\nObjekta rievainība atkarīga no rievu daudzuma un lieluma.")
    grid.addWidget(info_groove, inx, 3, inx+1, 7)
    # |======== last buttons =======|
    button_save = create_BigButton("Saglabāt tabulu excel formātā")
    # |=== path QLine ===|
    path = QLineEdit()
    path.setPlaceholderText("Rezultāts")
    path.setStyleSheet(
      "font-size: 30px;" +
      "background: '#f5bdb0';" +
      "color : 'black';" +
      "padding: 20px 10px;" +             # <-- Inside a element. (top-bottom (px), sides (px))
      "margin: 5px 50px;"                # <-- outside a element.
    )
    widgets["input"].append(path)
    button_save.clicked.connect(lambda: save_txt(widgets["input"][-1].text()))
    grid.addWidget(button_save, inx, 0, inx, 2)
    grid.addWidget(path, inx, 2)
  button_last = create_BigButton("Atpakaļ")
  button_last.clicked.connect(frame1)
  grid.addWidget(button_last, inx+1, 0, inx+1, 2)
  
def test_fun(Text):
  print (Text)

def save_txt(path):  
  if path == '': path="Rezultāts"
  print (path)
  if os.path.exists(path + ".xlsx"): os.remove(path + ".xlsx")
  
  head, tail = os.path.split(path)
  print ("head:", head)
  print ("tail", tail)
  if head !='' and not os.path.exists(head):
    Dir_info = createLine("Mape ar tādu nosaukumu neeksistē!")
    grid.addWidget(Dir_info, inx, 3, inx+1, 7)
    return
  
  data = pd.DataFrame.from_dict(Results)
  data.to_excel(path+".xlsx", index=False)


window.setLayout(grid)
frame1()
window.show()
sys.exit(app.exec())
