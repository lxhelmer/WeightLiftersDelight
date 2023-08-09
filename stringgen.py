pl_classes_male = [55,61,67,73,81,89,96,102,109,999]
pl_classes_female = [45,49,55,59,64,71,76,81,87,999]
wl_classes_male = [59,66,74,83,93,105,120,999]
wl_classes_female = [47,52,57,63,69,76,84,999]

for i in pl_classes_male:
    print("""INSERT INTO classes (max_weight, sex, sport) VALUES ("""+ str(i) + """,True,'PL');""")
for i in pl_classes_female:
    print("""INSERT INTO classes (max_weight, sex, sport) VALUES ("""+ str(i) + """,False,'PL');""")
for i in wl_classes_male:
    print("""INSERT INTO classes (max_weight, sex, sport) VALUES ("""+ str(i) + """,True,'WL');""")
for i in wl_classes_female:
    print("""INSERT INTO classes (max_weight, sex, sport) VALUES ("""+ str(i) + """,False,'WL');""")
