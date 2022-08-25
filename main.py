import open3d as o3d
import numpy as np
from os import path
from copy import deepcopy

from OD_FUNC import *
from groovedness import *
from Object_func import *
from helper import get_pcd, show_pcd, Find_corner, scale_pcd, Stat_removal, OB_param
'''
This project contains 24 functions:
-------------------------------
OD_FUNC:
  1. get_one_object() - gets one potential object for later analysis;
  2. _get_one_obejct() - second algorithm which trys to recognize one object by it's projection;
  3. In_while_func() - This function is supplement function which is used in _get_one object function;
  4. test_OB() - test if projection slightly looks like object projection or not;
  5. get_projection() - gets obejct projection. This function uses get_colorpoints function;

Object_func:
  1. get_colorpoints() - Gets sample points or projection points using color analyse;
  2. Is_object() - analyzes object which cames from get_one_object() function.
			Returns True if an object meets certain criteria and False - if not;
  3. get_BoBox() - if Is_object() returned True then this function gets bounding box of the object;
  4. From_BB_get_points() - Gets objekt points from known bounding box
  5. del_object() - deletes analized object from pcd, which allows to get next potential object;
  6. print_BB_info() - print object information Height, Width, Depth

grooviedness:
  1. OB_cut_points() - get object analyses points
  2. merge_points() - merge closest points together
  3. Grad_extremes() - locate object max and min values in local areas
  4. Analyse() - Analyzes object groovedness

helper:
  1. get_pcd() - returns dictionary which contains pointcloud it self, pointcloud points and pointcloud colors, 
				if the corresponding function argument is set to True.
  2. show_pcd() - visualizes pcd ar pcd.points
  3. Find_corner() - Finds corners of points (y_max, y_min, x_max, x_min, z_max, z_min);
  4. Vector() - converts points into pcd
  5. Stat_removal() - filteres out noise points based on neghbors checking;
  6. display_inlier_outlier() - calculates and returns outliers for pointcloud
  7. scale_pcd() - calculete and scale pcd into needed size
  8. Align_base() - calculate and rotate pcd so all base corners have the same z value

This file (main.py):
  1. main() - calls all functions;

At the end of this file (~ line 106) please specify which pointcloud (pcd) to load. Use variable 'pcd_name'
'''

def main(pcd, radius):
            # |=== Check inputs ===|
  radius = 20 if radius=="" else int(radius)
  if radius < 5: radius=5
  if radius > 40: radius=40
  
   # |=== Rotate pcd for analysis ===|
  pcd_rot = deepcopy(pcd)                 # <-- copy pcd
  
     # |=== Scale pcd for analysis ===|
  pcd_center = pcd.get_center()
  pcd, scale_num = scale_pcd(pcd, -1, pcd_center) # (-1) <-- This value doesn't matter here
  pcd_rot_scd = deepcopy(pcd)                 # <-- pcd_copy_A is rotated and scaled

     # |=== Get sample points ===|
  pcd = get_colorpoints(pcd)
  for _ in range(3):
    pcd, ind = Stat_removal(pcd, ratio=0.5)

    # |=== Def variables ===|
  OB = {}
  OB_WDH = {}
  groove_ind = {}
  BB = {}
  Groove_max_height = {} 
  Groove_count = {}
  BB_nr = 0
  count = 0
  projection_points = None # <-- Projection_points activates if second algorithm is in use.
  
  # |=== While 'True' -> keep looking and analyzing possible objects. ===|
  while True:
    try:
      # If the second algorithm activates then there are values in projection_points variable.
      obj_pcd, projection_points, Skip = get_one_object(pcd, pcd_rot_scd, projection_points, radius)
    except:
      break     # <-- |=== " No more objects " ===|
      
    # |=== If the sec algorithm faild then Skip = True. -->
    # --> So do not analyse (Do not use Is_object()) ===|

    if not Skip:
      # |=== If the obj_pcd (which is one possible object) is trully an object --> ===|
      Is_an_object = Is_object(obj_pcd, radius)

      # |=== --> Then save the object and it's parameters ===|
      if Is_an_object:
        BB_nr += 1       # There are f{BB_nr} Bounding boxes. BB["BB0"] will be 'pcd'.
        
        # |=== save the object bounding box ===|
        BB[f"BB{BB_nr}"] = get_BoBox(obj_pcd)
        # |=== From BB get and save colored object ===|
        OB[f"OB{BB_nr}"] = From_BB_get_pcd(BB[f"BB{BB_nr}"], pcd_rot_scd)
        #  |== anti-scale bounding boxes and save anti-scaled BB ==|
        BB[f"BB{BB_nr}"], _ = scale_pcd(BB[f"BB{BB_nr}"], scale_num, pcd_center, ForwScale=False)
        # |=== anti-scale OB ===|
        OB_anti_scd, _ = scale_pcd(obj_pcd, scale_num, pcd_center, ForwScale=False)
        # |=== get and save OB height, width, depth (real size parameters) ===|
        OB_WDH[f"{BB_nr}"] = OB_param(OB_anti_scd, pcd_rot, BB[f"BB{BB_nr}"]) # (OB, pcd, BB) is input
        # |=== find and save objekt |=Groovedness index, max height, how many grovies=| ===|
        groove_ind[f"{BB_nr}"], Groove_max_height[f"{BB_nr}"], Groove_count[f"{BB_nr}"] = groove_main(OB_anti_scd)
      else:
        pass
    pcd = del_object(pcd, obj_pcd) # after this line execution pcd contains the same points,
  # |=== BB print() ===|
  #print_BB_info(BB, Base_z)
  # Rotate pcd again ===========================
  BB["BB0"] = pcd_rot
  # ============ Get np array from bounding boxes ======
  dict_lengh = len(BB.keys())
  # Information out =====================================
  print (f"\n{dict_lengh - 1} objects were detected")
  # PCD and bounding boxes visuzalization ====
  o3d.visualization.draw_geometries([BB[f"{i}"] for i in BB.keys()])
# ========================= End of the main() ============================= #
  return OB, OB_WDH, groove_ind, Groove_max_height, Groove_count

if __name__  ==  '__main__':
  # use ./file.pcd for current directory
  #pcd_name = "../data_cidonijas3d/a5.pcd"
  # pcd_name = "../akfen_3d_imaging/data_avenes3d/par_1.pcd"
  # pcd_name = "../../data_cidonijas3d/a1.pcd"
  # problēma ar brūnu fonu ========
  pcd_name = "./../../samples/berries/PATRICIJA_3.pcd"
  pcd = get_pcd(pcd_name, pcd=True)["pcd"]
  exit(main(pcd, 10))

