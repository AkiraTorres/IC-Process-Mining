import json
import sys

import pandas as pd

data = "./data/see_course2060_12-11_to_11-12_logs_filtered.csv"
mapping = pd.read_csv("./data/event_mapping.csv")

all_logs_data = pd.read_csv(data, index_col="id").sort_values("t")


def save_to_csv(list_of_dataframes):
    for df in list_of_dataframes:
        df["data"].to_csv(f"{df['name']}.csv")


def event_mapping(event, time: int, is_temp_fold: bool = False):
    mapped = mapping[
        (mapping.component == event[0])
        & (mapping.action == event[1])
        & (mapping.target == event[2])
    ]
    e = mapped["class"].iloc[0]
    result = e
    if is_temp_fold:
        tf = (time - 1573527600) / (1574218500 - 1573527600) * 100
        e = e + "_START" if tf <= 50 else e + "_END"
        result = {"event": e, "time": time}

    return {"event": e, "time": time}
    return result


# return a sequence of catalogued events based on a dataframe of events
def generate_sequence_from_df(df, params: dict):
    e = list(
        df.apply(
            lambda x: event_mapping([x.component, x.action, x.target], x.t),
            axis=1,
        )
    )
    e.pop(0)
    flag = False
    events = []
    for event in reversed(e):
        if (
            event["event"] == "assignment_sub" or event["event"] == "assignment_sub"
        ) and not flag:
            flag = True
        if flag:
            events.append(event)
    events = list(reversed(events))

    if not events:
        return None

    for i in range(len(events)):
        try:
            if params["coalescing_repeating"]:
                while events[i] == events[i + 1]:
                    if (
                        events[i]["event"] == "assignment_sub"
                        or events[i]["event"] == "assignment_sub"
                    ):
                        events.pop(i)
                    else:
                        events.pop(i + 1)
            if params["coalescing_hidden"]:
                if (
                    events[i]["event"] == "assignment_vis"
                    and events[i + 1]["event"] == "assignment_try"
                ):
                    events.pop(i)
                elif (
                    events[i]["event"] == "assignment_vis"
                    and events[i + 1]["event"] == "assignment_sub"
                ):
                    events.pop(i)
                elif (
                    events[i]["event"] == "assignment_try"
                    and events[i + 1]["event"] == "assignment_sub"
                ):
                    events.pop(i)
        except IndexError:
            pass
    return events


# return a sequence of catalogued events based on a dataframe of events
def generate_sequence_from_df_with_temporal_folding(df, params: dict):
    e = list(
        df.apply(
            lambda x: event_mapping([x.component, x.action, x.target], x.t, True),
            axis=1,
        )
    )
    e.pop(0)
    flag = False
    events = []
    for event in reversed(e):
        if (
            event["event"] == "assignment_sub_START"
            or event["event"] == "assignment_sub_END"
        ) and not flag:
            flag = True
        if flag:
            events.append(event)
    events = list(reversed(events))

    if not events:
        return None

    for i in range(len(events)):
        try:
            if params["coalescing_repeating"]:
                while events[i] == events[i + 1]:
                    if (
                        events[i]["event"] == "assignment_sub_START"
                        or events[i]["event"] == "assignment_sub_END"
                    ):
                        events.pop(i)
                    else:
                        events.pop(i + 1)

            if params["coalescing_hidden"]:
                if (
                    events[i]["event"] == "assignment_vis_START"
                    and events[i + 1]["event"] == "assignment_try_START"
                ):
                    events.pop(i)
                elif (
                    events[i]["event"] == "assignment_vis_START"
                    and events[i + 1]["event"] == "assignment_sub_START"
                ):
                    events.pop(i)
                elif (
                    events[i]["event"] == "assignment_try_START"
                    and events[i + 1]["event"] == "assignment_sub_START"
                ):
                    events.pop(i)
                elif (
                    events[i]["event"] == "assignment_vis_END"
                    and events[i + 1]["event"] == "assignment_try_END"
                ):
                    events.pop(i)
                elif (
                    events[i]["event"] == "assignment_vis_END"
                    and events[i + 1]["event"] == "assignment_sub_END"
                ):
                    events.pop(i)
                elif (
                    events[i]["event"] == "assignment_try_END"
                    and events[i + 1]["event"] == "assignment_sub_END"
                ):
                    events.pop(i)
        except IndexError:
            pass
    return events


# make the database ready for GSP and prefix datamining algorithms
def prepare_database(df, params: dict) -> list:
    events_by_user = []
    unique_users = df.drop_duplicates(subset=["userid"])
    unique_users = unique_users["userid"].tolist()

    for userid in unique_users:
        if params["tf"]:
            events = generate_sequence_from_df_with_temporal_folding(
                df[df.userid == userid], params
            )
        else:
            events = generate_sequence_from_df(df[df.userid == userid], params)
        if events:
            new_user = {"key": str(userid), "events": events}
            events_by_user.append(new_user)
    with open("./" + params["path"] + ".json", "w+") as file:
        json.dump([user for user in events_by_user], file)
    return events_by_user


def partitioning():
    activity_logs = (
        all_logs_data.sort_values("t")
        .query("t >= 1573527600 & t <= 1574218500")
        .query("assignment_id == 12841 | component != 'core' & component != 'mod_page'")
    )

    first_access = all_logs_data.sort_values("t").drop_duplicates(subset=["userid"])
    first_access = first_access.sort_values("userid")

    return [first_access, activity_logs]


def classify_events(activity, first_access):
    return pd.concat([first_access, activity])  # .sort_values("userid")


# parametrization
def read_params(argv: list) -> dict:
    params = {
        "tf": False,
        "path": "events_by_user",
        "activity": 1,
        "initial_date": 1574218500,
        "final_date": 1573527600,
        "assignment_id": 12841,
        "coalescing_repeating": False,
        "coalescing_hidden": False,
    }

    if len(argv) == 1:
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
        if argv[index] == "-id" or argv[index] == "--assignment_id":
            params["assignment_id"] = argv[index + 1]
            index += 1
            continue
        if argv[index] == "-r" or argv[index] == "--coalescing_repeating":
            params["coalescing_repeating"] = True
            continue
        if argv[index] == "-c" or argv[index] == "--coalescing_hidden":
            params["coalescing_hidden"] = True
            continue
        if argv[index] == "-h" or argv[index] == "--help":
            print(
                "-tf:    temporal folding\n-p [path]:     path to save the file\n-act:   activity id\n-init []:  "
                "initial date\n-final: final date\n-id:    assignment id\n-r:     coalescing repeating\n-c:     "
                "coalescing hidden"
            )
            sys.exit(0)

    return params


def main(params: dict):
    first_access, activity = partitioning()
    activity = classify_events(activity, first_access)

    prepare_database(activity, params)


if __name__ == "__main__":
    main(read_params(sys.argv))
