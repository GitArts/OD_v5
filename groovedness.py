import numpy as np
import open3d as o3d
from helper import Vector, get_pcd, show_pcd, Find_corner
#mesh = o3d.geometry.TriangleMesh.create_coordinate_frame(origin=z_max, size=3)

def OB_cut_points(pcd, points, delay):
  Center = pcd.get_center()
  Center[1] = Center[1] + delay
  points =  points[(points[:, 1] > Center[1]-0.2)&(points[:, 1] < Center[1]+0.2)]
  return points

def merge_points(sec_points):
  while True:
    y_max2 = Find_corner(sec_points, 100000)["y_max"]
    Distance = np.linalg.norm(sec_points - y_max2, axis=1)
    # |=== marge together points if a distance between them are less then 1 ===|
    merge = sec_points[Distance < 1]				# <-- points which getting merged
    # |=== Leave z_max and z_min points of the marged points ===|
    z_max, z_min = Find_corner(merge, '000011').values()	# <-- two points which are merged
    # |=== Other points - which wasn't marged ===|
    sec_points = sec_points[Distance >= 1]
    # |=== Stack marged points ===|
    if 'points' not in locals():
      points = np.stack((z_min, z_max))
    else:
      points = np.vstack((points, z_max, z_min))
    # |=== Exit the loop when all points are analyzed ===|
    if np.size(sec_points)==0: print ("Merge - DONE"); break
  return points

def Graf_extremes(sec_points):
  # |=== Find max_y point ===|
  y_max1 = Find_corner(sec_points, 100000)["y_max"] # <-- points are upside down
  #|=== Def variables ===|
  local_max = {}
  local_min = {}
  max_count = 0
  min_count = 0
  Down = True # <-- First point will be in local minimum

  while True:
    # |=== Delete y_max1 prjection point from sec_points, but var is still exists -> will be used ===|
    sec_points = np.delete(sec_points, np.where(sec_points[:, 0] == y_max1[0]), axis=0)
    if np.size(sec_points) == 0: break
    # |=== y_max2 point has y_max value ===|
    y_max2 = Find_corner(sec_points, 100000)["y_max"]

    # |=== Find graf local maximums (z_axes) ===|
    if y_max2[2] < y_max1[2] and Down == False:
      max_count += 1
      local_max[f"{max_count}"] = y_max1
      Down = True
    # |=== Find graf local minimums (z axes) ===|
    if y_max2[2] > y_max1[2] and Down == True:
      min_count += 1
      local_min[f"{min_count}"] = y_max1
      Down = False

    y_max1 = y_max2
  points_max = np.asarray(list(local_max.values()))
  points_min = np.asarray(list(local_min.values()))
  #print ("max_points:\n", points_max)
  #print ("min_points:\n", points_min)
  #print ("Extremes - DONE")
  return points_max, points_min # <-- Are dictionaries

def Analyse(MAX, MIN):
  """
  Rievu skaits - ??emt v??r?? tikai kritumus;
  Zem??kais iekritums - ??emt v??r?? tikai kritumus
  """
  
  Skip_last = np.shape(MIN) == np.shape(MAX)
  DIFF = []
  Highest_peak = 0
  for i in range(np.shape(MAX)[0]):
    # |=== First point analysis ===|
    Y = abs(MAX[i, 0] - MIN[i, 0])   # <-- Y att??lums starp pirmo MAX punktu un pirmo MIN punktu
    Z = abs(MAX[i, 2] - MIN[i, 2])
    if Y < 1.5 and Z > 1: # <-- nov??r?? avenes liekuma anal??zi. Liekums nav rievain??gums
      Highest_peak = Z if abs(Z) > Highest_peak else Highest_peak
      DIFF.append(Z/Y)
    # |=== If Skip_last is True then break the loop at last check ===|
    if i == np.shape(MAX)[0]-1 and Skip_last:
      break

    # |=== Second point analysis ===|
    Y = abs(MAX[i, 0] - MIN[i+1, 0]) # <-- Y att??lums starp pirmo MAX punktu un otro MIN punktu
    Z = abs(MAX[i, 2] - MIN[i+1, 2])
    if Y < 1.5 and Z > 1:
      Highest_peak = Z if abs(Z) > Highest_peak else Highest_peak
      DIFF.append(Z/Y)
    peak_count = np.shape(MAX)[0]
  
  Groove = sum(DIFF) if np.size(DIFF) != 0 else 0
  if 'peak_count' not in locals(): peak_count = 0
  return Groove, Highest_peak, peak_count

def groove_main(pcd):
  # |=== Load pcd ===|
  # pcd = get_pcd("../OBJEKTI/CID7.pcd", pcd=True)["pcd"] # <-- pcd var in this line is just a placeholder
  points = np.asarray(pcd.points)
  # |=== Analyze 3 object areas using Delay ===|
  Groove_lst = []
  Final_H = 0
  Final_C = 0
  for Delay in range(-2, 3, 2):
  # |=== Object analyses points ===|
    sec_points = OB_cut_points(pcd, points, Delay)
    # |=== Functions ===|
    if np.size(sec_points) == 0: continue
    sec_points = merge_points(sec_points)
    MAX, MIN = Graf_extremes(sec_points)
    Groove, Highest_peak, peak_count = Analyse(MAX, MIN)
    # |=== Find final max peak height and peak count ===|
    Final_H = Highest_peak if Highest_peak > Final_H else Final_H
    Final_C = peak_count if peak_count > Final_C else Final_C
    Groove_lst.append(Groove)

  Groove = sum(Groove_lst)
  # |=== Rievain??bas pak??pes nov??rt??jums ===|
  print ("|=== Rievain??guma v??rt??bas ===|\n", "Rievain??guma indekss =", Groove)

  if Groove >= 2.5:
    print ("Ir rievains")
  else:
    print ("Nav rievains")
  return Groove, Final_H, Final_C

if __name__=="__main__":
  groove_main()
