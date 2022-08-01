import open3d as o3d
import numpy as np
from copy import deepcopy
from helper import get_pcd, show_pcd, Find_corner, scale_pcd


pcd1 = get_pcd("../data_avenes3d/par_2.pcd", pcd=True)["pcd"]
pcd2 = deepcopy(pcd1)

MM11 = Find_corner(np.asarray(pcd1.points), 110000)
MM21 = Find_corner(np.asarray(pcd2.points), 110000)

Center = pcd2.get_center()
scale_pcd(pcd1, 2, Center)

MM12 = Find_corner(np.asarray(pcd1.points), 110000)
MM22 = Find_corner(np.asarray(pcd2.points), 110000)

print (MM11)
print (MM21)
print (MM12)
print (MM22)