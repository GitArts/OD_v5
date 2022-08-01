import pandas as pd
import os

columns = ["Nr", "object", "Vizualization"]
titled_column = {"column1": [1, 2, 3],
                "column2": [4, 5, 6],
                "column3": [7, 8, 9]}

data = pd.DataFrame.from_dict(titled_column)

# save
print ("file name:")
path = input()
if os.path.exists(path + ".xlsx"): os.remove(path + ".xlsx")
data.to_excel(path + ".xlsx", index=False)

print(data)
