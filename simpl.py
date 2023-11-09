import pandas as pd

def partitioning(all_logs_data):
    # cols = ["id", "t"]
    # all_logs_data = pd.read_csv(data, index_col="id")

    first_logs = all_logs_data.query("t >= 1573527600").query("t <= 1574218500").sort_values("t")
    second_logs = all_logs_data.query("t >= 1574132400").query("t <= 1574823300").sort_values("t")
    third_logs = all_logs_data.query("t >= 1574737200").query("t <= 1575428100").sort_values("t")
    fourth_logs = all_logs_data.query("t >= 1575342000").query("t <= 1576032900").sort_values("t")
    
    return [first_logs, second_logs, third_logs, fourth_logs]


def save(logs):
    first_logs, second_logs, third_logs, fourth_logs = [i for i in logs]

    first_logs.to_csv("see_course2060_first_activity_logs.csv")
    second_logs.to_csv("see_course2060_second_activity_logs.csv")
    third_logs.to_csv("see_course2060_third_activity_logs.csv")
    fourth_logs.to_csv("see_course2060_fourth_activity_logs.csv")


def extract_record(logs):
    first_logs, second_logs, third_logs, fourth_logs = [i for i in logs]

    first_logs = first_logs.query("assignment_id == 12841")
    second_logs = second_logs.query("assignment_id == 12842")
    third_logs = third_logs.query("assignment_id == 12843")
    fourth_logs = fourth_logs.query("assignment_id == 12844")

    first_logs_size = len(first_logs.index)
    second_logs_size = len(second_logs.index)
    third_logs_size = len(third_logs.index)
    fourth_logs_size = len(fourth_logs.index)

    print(f"total of {first_logs_size + second_logs_size + third_logs_size + fourth_logs_size} logs")

    return [first_logs, second_logs, third_logs, fourth_logs]


def check_if_equals(logs, data):
    total_after_filter = len(logs[0].index) + len(logs[1].index) + len(logs[2].index) + len(logs[3].index)
    total_before_filter = len(data.index)

    total_without_course_vis = len(data.query("component == 'core'").index)
    total_irrelevant_activities = len(data.query("assignment_id not in [12841, 12842, 12843, 12844]").index)

    print(total_after_filter + total_irrelevant_activities)
    print(total_before_filter)


if __name__ == "__main__":
    data = "./data/see_course2060_12-11_to_11-12_logs_filtered.csv"
    all_logs_data = pd.read_csv(data, index_col="id")
    logs = partitioning(all_logs_data)
    logs = extract_record(logs)

    check_if_equals(logs, all_logs_data)

    save(logs)
