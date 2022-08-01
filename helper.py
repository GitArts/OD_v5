import open3d as o3d
import numpy as np
from copy import deepcopy

"""
 _get_pcd(sample_name, pcd=0, points=0, colors=0)
 show_pcd(pcd_or_points, vector=0, color=0, save=0, name = 'show_pcd_save.pcd')
 Find_corner(points)
 Vector(points)
 scale_pcd(pcd, n, pcd_center)
 Align_base(pcd)
"""

def get_pcd(sample_name, pcd=False, points=False, colors=False):
  pcd_dict = {}
  pointcloud = o3d.io.read_point_cloud(sample_name)
  if pcd:       pcd_dict["pcd"] = pointcloud
  if points:    pcd_dict["points"] = np.asarray(pointcloud.points)
  if colors:    pcd_dict["colors"] = np.asarray(pointcloud.colors)

  return pcd_dict

def show_pcd(pcd_or_points, vector=False, color=False, save=False, name = 'show_pcd_save.pcd'):
  if vector:  # Don't use list of points in variable pcd_or_points
    points = pcd_or_points
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
  else:
    pcd = pcd_or_points
  if save: o3d.io.write_point_cloud(name, pcd)
  if color: pcd.paint_uniform_color([160/255, 82/255, 45/255])
  if isinstance(pcd_or_points, list):
    o3d.visualization.draw_geometries([elem for elem in pcd_or_points])
  else:
    o3d.visualization.draw_geometries([pcd])

def Find_corner(points, MM_check):
  MM = list(str(MM_check)) # <-- defines which Min_Max values we need
  Dict = {}
  if MM[0] == '1':
    Y_max = np.amax(points, where=[True, False, False], initial=-np.inf)
    Y_max = points[np.where(points[:, 0] == Y_max)][0]
    Dict["y_max"] = Y_max
  if MM[1] == '1':
    Y_min = np.amin(points, where=[True, False, False], initial=np.inf)
    Y_min = points[np.where(points[:, 0] == Y_min)][0]
    Dict["y_min"] = Y_min
  if MM[2] == '1':
    X_max = np.amax(points, where=[False, True, False], initial=-np.inf)
    X_max = points[np.where(points[:, 1] == X_max)][0]
    Dict["x_max"] = X_max
  if MM[3] == '1':
    X_min = np.amin(points, where=[False, True, False], initial=np.inf)
    X_min = points[np.where(points[:, 1] == X_min)][0]
    Dict["x_min"] = X_min
  if MM[4] == '1':
    Z_max = np.amax(points, where=[False, False, True], initial=-np.inf)
    Z_max = points[np.where(points[:, 2] == Z_max)][0]
    Dict["z_max"] = Z_max
  if MM[5] == '1':
    Z_min = np.amin(points, where=[False, False, True], initial=np.inf)
    Z_min = points[np.where(points[:, 2] == Z_min)][0]
    Dict["z_min"] = Z_min
  return Dict

def Vector(points, colors=None):
  pcd = o3d.geometry.PointCloud()
  pcd.points = o3d.utility.Vector3dVector(points)
  if isinstance(colors, np.ndarray): pcd.colors = o3d.utility.Vector3dVector(colors)
  return pcd

# Statisticak outlier removal function
def Stat_removal(pointcloud, neighbors = 20, ratio = 0.5):
  cl, ind = pointcloud.remove_statistical_outlier(nb_neighbors=neighbors, std_ratio=ratio)
  return cl, ind

# Helper function which displays deleted (outlier) points and va>
def display_inlier_outlier(cloud, ind):
  inlier_cloud = cloud.select_by_index(ind)
  outlier_cloud = cloud.select_by_index(ind, invert=True)
  outlier_cloud.paint_uniform_color([1, 0, 0])
  inlier_cloud.paint_uniform_color([0.8, 0.8, 0.8])
  return outlier_cloud

def scale_pcd(pcd, n, pcd_center, ForwScale=True):
  if ForwScale: # if you want anti-scale this segment must be scipted
    points = np.asarray(pcd.points)
    MM = Find_corner(points, 110000)
    y_max, y_min = MM["y_max"][0], MM["y_min"][0]
    y_diff = y_max-y_min
    n = 360/y_diff
  else:
    pass
  Scaled_pcd = deepcopy(pcd)
  Scaled_pcd.scale(n, center = pcd_center)
  scaled_by = 1/n
  return Scaled_pcd, scaled_by

# |== align base on z axis ==|
def Align_base(pcd):
  # Rotate around Y axis =======================================>
  MM = Find_corner(np.asarray(pcd.points), '001100')
  diff_z_x = MM["x_max"][2] - MM["x_min"][2]    # <-- get z valu>
  diff_x = MM["x_max"][1] - MM["x_min"][1]      # <-- get x valu>

  rot_y = np.arcsin(diff_z_x/diff_x) # <-- rad
  R = pcd.get_rotation_matrix_from_xyz((rot_y, 0, 0))
  pcd.rotate(R, center = MM["x_max"])

  # Rotate around X axis =======================================>
  MM = Find_corner(np.asarray(pcd.points), 110000)
  diff_z_y = MM["y_max"][2] - MM["y_min"][2]
  diff_y = MM["y_max"][0] - MM["y_min"][0]
  rot_x = np.arcsin(diff_z_y/diff_y) # <-- rad
  R = pcd.get_rotation_matrix_from_xyz((0, rot_x, 0))
  pcd.rotate(R, center = MM["y_max"])
  return pcd, MM["y_max"][2]

def get_height(OB, pcd, BB):
  OB_points = np.asarray(OB.points)
  pcd_points = np.asarray(pcd.points)
  OB_MM = Find_corner(OB_points, 111100)
  pcd_points = pcd_points[(pcd_points[:, 0] < OB_MM["y_max"][0]+1)&
                            (pcd_points[:, 0] > OB_MM["y_min"][0]-1)&
                            (pcd_points[:, 1] < OB_MM["x_max"][1]+1)&
                            (pcd_points[:, 1] > OB_MM["x_min"][1]-1)]
  #breakpoint()
  MM = np.asarray(list(Find_corner(pcd_points, 111100).values()))
  Min_Z = min(MM[0][2], MM[1][2], MM[2][2], MM[0][2])
  Min_Z_point = MM[np.where(MM[:, 2] == Min_Z)][0]
  H = abs(BB.get_min_bound()[2] - Min_Z) # pcd is upside down. BB.Z_min == points.Z_max. 
  if abs(BB.get_max_bound()[2] - BB.get_min_bound()[2]) > H: H = abs(BB.get_max_bound()[2] - BB.get_min_bound()[2])*2
  return H

# |=== print object information Height, Width, Depth ===|
def OB_param(OB, pcd, BB):
  H = get_height(OB, pcd, BB)
  W = BB.get_max_bound()[0] - BB.get_min_bound()[0]
  D = BB.get_max_bound()[1] - BB.get_min_bound()[1]
  return W, D, H
  # platums dziņums augstums