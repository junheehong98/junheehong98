from mobfot import MobFot
import csv
import json


fotmob = MobFot()
match_ids = [4193457, 4193477, 4193480, 4193493, 4193507, 4193510, 4193527, 4193536, 4193549, 4193555, 4193569, 4193579, 4193660]


result = fotmob.get_match_details(4193457)
print(result)