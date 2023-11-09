import pandas as pd
from matplotlib import pyplot as plt
data = "./data/see_course2060_12-11_to_11-12_logs_filtered.csv"

all_logs_data = pd.read_csv(data, index_col="id").sort_values("t")
all_logs_data.head()

first_logs = all_logs_data.query("t >= 1573527600").query("t <= 1574218500").query("assignment_id == 12841")
first_logs.to_csv("see_course2060_first_activity_logs.csv")

second_logs = all_logs_data.query("t >= 1574132400").query("t <= 1574823300").query("assignment_id == 12842")
second_logs.to_csv("see_course2060_second_activity_logs.csv")

third_logs = all_logs_data.query("t >= 1574737200").query("t <= 1575428100").query("assignment_id == 12843")
third_logs.to_csv("see_course2060_third_activity_logs.csv")

fourth_logs = all_logs_data.query("t >= 1575342000").query("t <= 1576032900").query("assignment_id == 12844")
fourth_logs.to_csv("see_course2060_fourth_activity_logs.csv")

first_access = all_logs_data.sort_values("userid").query("component == 'core'").drop_duplicates(subset=['userid'])
first_access.to_csv("first_access_logs.csv")


first_logs_size = len(first_logs.index)
second_logs_size = len(second_logs.index)
third_logs_size = len(third_logs.index)
fourth_logs_size = len(fourth_logs.index)
total_size = len(all_logs_data.index)

print(first_logs_size + second_logs_size + third_logs_size + fourth_logs_size)

fig = plt.figure(figsize=(4, 5))
sizes = [first_logs_size, second_logs_size, third_logs_size, fourth_logs_size]
plt.bar(["first", "second", "third", "fourth"], sizes)
plt.title("Number of events by activity")
plt.show()

fig = plt.figure(figsize=(4, 5))
total_logs_size = 0
for i in sizes:
    total_logs_size += i
plt.bar(["before filter", "after filter"], [total_size, total_logs_size])
plt.title("Diference between db before and after filter")
plt.show()
