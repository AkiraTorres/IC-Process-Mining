import json
import sys
import time
import pandas as pd

data = "./data/see_course2060_12-11_to_11-12_logs_filtered.csv"
mapping = pd.read_csv("data/event_mapping.csv")

all_logs_data = pd.read_csv(data, index_col="id").sort_values("t")


def save_to_csv(list_of_dataframes):
    for df in list_of_dataframes:
        df["data"].to_csv(f"{df['name']}.csv")


def event_mapping(event, t: int, params: dict):
    mapped = mapping[(mapping.component == event[0]) & (mapping.action == event[1]) & (mapping.target == event[2])]
    e = mapped["class"].iloc[0]
    result = {"event": e, "time": t}
    if params["tf"]:
        tf = params["initial_date"] + (params["final_date"] - params["initial_date"]) / 2
        # tf = (time - params["initial_date"]) / (params["final_date"] - params["initial_date"]) * 100
        e = e + "_START" if t <= tf else e + "_END"
        result = {"event": e, "time": t}

    return result


# return a sequence of catalogued events based on a dataframe of events
def generate_sequence_from_df(df, params: dict):
    e = list(
        df.apply(
            lambda x: event_mapping([x.component, x.action, x.target], x.t, params),
            axis=1,
        )
    )
    e.pop(0)
    flag = False
    events = []
    for event in reversed(e):
        if (event["event"] == "assignment_sub" or event["event"] == "assignment_sub") and not flag:
            flag = True
        if flag:
            events.append(event)
    events = list(reversed(events))

    if not events:
        return None

    if params["coalescing_repeating"]:
        remove_indexes = []
        for i in range(len(events)):
            try:
                if events[i]["event"] == events[i + 1]["event"]:
                    if events[i]["event"] == "assignment_sub" or events[i]["event"] == "assignment_sub":
                        remove_indexes.append(i)
                    else:
                        remove_indexes.append(i + 1)
            except IndexError:
                pass
        # get index list in reverse order
        remove_indexes = sorted(remove_indexes, reverse=True)
        # drop elements in place
        for index in remove_indexes:
            del events[index]
    if params["coalescing_hidden"]:
        remove_indexes = []
        for i in range(len(events)):
            try:
                if events[i]["event"] == "assignment_vis" and events[i + 1]["event"] == "assignment_try":
                    remove_indexes.append(i)
                elif events[i]["event"] == "assignment_vis" and events[i + 1]["event"] == "assignment_sub":
                    remove_indexes.append(i)
                elif events[i]["event"] == "assignment_try" and events[i + 1]["event"] == "assignment_sub":
                    remove_indexes.append(i)
            except IndexError:
                pass
        # get index list in reverse order
        remove_indexes = sorted(remove_indexes, reverse=True)
        # drop elements in place
        for index in remove_indexes:
            del events[index]
    return events


# return a sequence of catalogued events based on a dataframe of events
def generate_sequence_from_df_with_temporal_folding(df, params: dict):
    e = list(
        df.apply(
            lambda x: event_mapping([x.component, x.action, x.target], x.t, params),
            axis=1,
        )
    )
    e.pop(0)
    flag = False
    events = []
    for event in reversed(e):
        if (event["event"] == "assignment_sub_START" or event["event"] == "assignment_sub_END") and not flag:
            flag = True
        if flag:
            events.append(event)
    events = list(reversed(events))

    if params["coalescing_repeating"]:
        remove_indexes = []
        for i in range(len(events) - 1):
            if events[i]["event"] == events[i + 1]["event"]:
                if events[i]["event"] == "assignment_sub_START" or events[i]["event"] == "assignment_sub_END":
                    remove_indexes.append(i)
                else:
                    remove_indexes.append(i + 1)
        # get index list in reverse order
        remove_indexes = sorted(remove_indexes, reverse=True)
        # drop elements in place
        for index in remove_indexes:
            del events[index]

    if params["coalescing_hidden"]:
        remove_indexes = []
        for i in range(len(events)):
            try:
                if events[i]["event"] == "assignment_vis_START" and events[i + 1]["event"] == "assignment_try_START":
                    remove_indexes.append(i)
                elif events[i]["event"] == "assignment_vis_START" and events[i + 1]["event"] == "assignment_sub_START":
                    remove_indexes.append(i)
                elif events[i]["event"] == "assignment_try_START" and events[i + 1]["event"] == "assignment_sub_START":
                    remove_indexes.append(i)
                elif events[i]["event"] == "assignment_vis_END" and events[i + 1]["event"] == "assignment_try_END":
                    remove_indexes.append(i)
                elif events[i]["event"] == "assignment_vis_END" and events[i + 1]["event"] == "assignment_sub_END":
                    remove_indexes.append(i)
                elif events[i]["event"] == "assignment_try_END" and events[i + 1]["event"] == "assignment_sub_END":
                    remove_indexes.append(i)
            except IndexError:
                pass
        # get index list in reverse order
        remove_indexes = sorted(remove_indexes, reverse=True)

        # drop elements in place
        for index in remove_indexes:
            # events.pop(index)
            del events[index]

    return events


# make the database ready for GSP and prefix datamining algorithms
def prepare_database(df, params: dict, grade_df=None) -> list:
    events_by_user = []
    unique_users = df.drop_duplicates(subset=["userid"])
    unique_users = unique_users["userid"].tolist()

    for userid in unique_users:
        if params["tf"]:
            events = generate_sequence_from_df_with_temporal_folding(df[df.userid == userid], params)
        else:
            events = generate_sequence_from_df(df[df.userid == userid], params)
        if events:
            new_user = {"key": str(userid), "events": events}
            if grade_df is not None:
                # print(userid)
                user_grade = grade_df.query(f"userid == {userid}")["student_grade"]
                if user_grade.empty:
                    user_grade = 0.0
                else:
                    user_grade = user_grade.iloc[0]
                new_user["grade"] = user_grade
                new_user["max_grade"] = grade_df["max_grade"].iloc[0]
            events_by_user.append(new_user)
    # print(json.dumps(events_by_user[0], indent=2, default=lambda o: str(o)))
    return events_by_user


def partitioning(params, grade_df=None):
    init_date = params["initial_date"]
    final_date = params["final_date"]
    assignment_id = params["assignment_id"]
    grades = None
    activity_logs = (
        all_logs_data.sort_values("t")
        .query(f"t >= {init_date} & t <= {final_date}")
        .query(f"assignment_id == {assignment_id} | component != 'core' & component != 'mod_page'")
        # .query(f"t >= 1573527600 & t <= 1574218500")
    )

    first_access = all_logs_data.sort_values("t").drop_duplicates(subset=["userid"])
    first_access = first_access.sort_values("userid")

    if grade_df is not None:
        grades = grade_df.query(f"id == {assignment_id}")
        # .query(f"time_open >= {init_date} & time_close <= {final_date}"))  # ["userid", "student_grade", "max_grade"]

    return [first_access, activity_logs, grades]


def classify_events(activity, first_access):
    return pd.concat([first_access, activity])  # .sort_values("userid")


# parametrization
def read_params(argv: list) -> dict:
    params = {
        "tf": True,
        "path": "sceneries/1-first",
        "grade_path": "./data/see_course2060_quiz_grades.csv",
        "activity": 1,
        "initial_date": 1573527600,
        "final_date": 1574218500,
        "assignment_id": 12841,
        "coalescing_repeating": True,
        "coalescing_hidden": True,
    }

    if False and len(argv) == 1:
        print(
            "-tf:    temporal folding\n-p [path]:     path to save the file\n-act [int]:   activity\n-init []:  "
            "initial date\n-final: final date\n-id [int]:    assignment id\n-r:     coalescing repeating\n-c:     "
            "coalescing hidden"
        )
        sys.exit(0)

    for index in range(len(argv)):
        if argv[index] == "-tf" or argv[index] == "--temporal_folding":
            params["tf"] = True
            continue
        if argv[index] == "-p" or argv[index] == "--path":
            params["path"] = argv[index + 1]
            index += 1
            continue
        if argv[index] == "-pg" or argv[index] == "--grade-path":
            params["grade_path"] = argv[index + 1]
            index += 1
            continue
        if argv[index] == "-act" or argv[index] == "--activity":
            params["activity"] = argv[index + 1]
            index += 1
            continue
        if argv[index] == "-init" or argv[index] == "--initial":
            params["initial_date"] = argv[index + 1]
            index += 1
            continue
        if argv[index] == "-final" or argv[index] == "--final":
            params["final_date"] = argv[index + 1]
            index += 1
            continue
        if argv[index] == "-id" or argv[index] == "--assignment-id":
            params["assignment_id"] = argv[index + 1]
            index += 1
            continue
        if argv[index] == "-r" or argv[index] == "--coalescing-repeating":
            params["coalescing_repeating"] = True
            continue
        if argv[index] == "-c" or argv[index] == "--coalescing-hidden":
            params["coalescing_hidden"] = True
            continue
        if argv[index] == "-h" or argv[index] == "--help":
            print(
                "-tf:    temporal folding\n-p [path]:     path to save the file\n-pg [grade's path]: path of grades "
                "csv\n-act:   activity id\n-init []:"
                "initial date\n-final: final date\n-id:    assignment id\n-r:     coalescing repeating\n-c:     "
                "coalescing hidden"
            )
            sys.exit(0)

    return params


def main(params: dict):
    activities_details = [
        {"initial_date": 1573527600, "final_date": 1574218500, "assignment_id": 12841},
        # {"initial_date": 1574132400, "final_date": 1574823300, "assignment_id": 12842},
        # {"initial_date": 1574737200, "final_date": 1575428100, "assignment_id": 12843},
        # {"initial_date": 1575342000, "final_date": 1576032900, "assignment_id": 12844},
    ]
    for activity in range(1, len(activities_details) + 1):
        params["activity"] = activity
        params["initial_date"] = activities_details[activity - 1]["initial_date"]
        params["final_date"] = activities_details[activity - 1]["final_date"]
        params["assignment_id"] = activities_details[activity - 1]["assignment_id"]

        grade_df = None
        sceneries_names = [
            {"path": "1-first", "tf": True, "coalescing_repeating": True, "coalescing_hidden": True},
            {"path": "2-second", "tf": True, "coalescing_repeating": True, "coalescing_hidden": False},
            {"path": "3-third", "tf": True, "coalescing_repeating": False, "coalescing_hidden": True},
            {"path": "4-fourth", "tf": True, "coalescing_repeating": False, "coalescing_hidden": False},
            {"path": "5-fifth", "tf": False, "coalescing_repeating": True, "coalescing_hidden": True},
            {"path": "6-sixth", "tf": False, "coalescing_repeating": True, "coalescing_hidden": False},
            {"path": "7-seventh", "tf": False, "coalescing_repeating": False, "coalescing_hidden": True},
            {"path": "8-eighth", "tf": False, "coalescing_repeating": False, "coalescing_hidden": False},
        ]
        for scenery in sceneries_names:
            start = time.time()
            params["tf"] = scenery["tf"]
            params["coalescing_repeating"] = scenery["coalescing_repeating"]
            params["coalescing_hidden"] = scenery["coalescing_hidden"]
            params["path"] = f"sceneries/{params["activity"]}/{scenery['path']}"

            if params["grade_path"]:
                grade_df = pd.read_csv(params["grade_path"])
            first_access, activity, grades = partitioning(params, grade_df)
            activity = classify_events(activity, first_access)

            events_by_user = prepare_database(activity, params, grades)

            with open("./" + params["path"] + ".json", "w+") as file:
                json.dump(events_by_user, file, indent=2, default=lambda o: str(o))
            print(f"Execution time, {params["path"]}: {(time.time() - start):.2f}")
        print()


if __name__ == "__main__":
    main(read_params(sys.argv))
