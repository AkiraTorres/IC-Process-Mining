import os.path
import json
from gsppy.gsp import GSP
from prefixspan import PrefixSpan
import pandas as pd
import csv
import time
import statistics
import datetime
import sys
import numpy as np

sceneries_names = [
    "1-first",
    # "2-second",
    # "3-third",
    # "4-fourth",
    # "5-fifth",
    # "6-sixth",
    # "7-seventh",
    # "8-eighth",
    # "9-ninth",
    # "10-tenth",
    # "11-eleventh",
    # "12-twelfth",
    "13-thirteenth",
    # "14-fourteenth",
    # "15-fifteenth",
    # "16-sixteenth",
    # "17-seventeenth",
    # "18-eighteenth",
    # "19-nineteenth",
    # "20-twentieth",
    # "21-twenty_first",
    # "22-twenty_second",
    # "23-twenty_third",
    # "24-twenty_fourth",
]

activity = 1


def generate_data(data):
    # pd.read_json(file_name)
    # Criar uma lista de dicionários diretamente do JSON
    rows = []
    for item in data:
        for i in item["events"]:
            rows.append(
                {
                    "key": item["key"],
                    "temporal_folding": item["temporal_folding"],
                    "grade": item["grade"],
                    "max_grade": item["max_grade"],
                    "events": i,  # Armazenar toda a lista de eventos
                }
            )

    # Criar o DataFrame
    df = pd.DataFrame(rows)
    df.to_csv("test.csv", sep=";", index=False)
    return df


def gsp_mining(sequences_list: list, minsup: float = 0.08) -> list:
    return GSP(sequences_list).search(minsup)


def prefix_mining(sequences_list: list, minsup: float = 0.08, subsequence=None) -> list:
    ps = PrefixSpan(sequences_list)
    ps.minlen = 2
    min_support = len(sequences_list) * minsup

    if subsequence:
        res = ps.frequent(min_support, filter=lambda patt, matches: is_subsequence(subsequence, patt) and len(patt) > 1)
        return res

    res = ps.frequent(min_support)

    max_seq_len = 0
    for index in res:
        if len(index[1]) > max_seq_len:
            max_seq_len = len(index[1])

    n_sequences = [{} for _ in range(max_seq_len)]

    for index in res:
        n_sequences[len(index[1]) - 1][f"{index[1]}"] = index[0]

    return n_sequences


def format_tf_data(s) -> list:
    data = []
    s = pd.DataFrame(data=s).to_dict(orient="records")
    for user_sequence in s:
        tf = user_sequence["temporal_folding"]
        # if tf:
        #     sessions = [session for session in user_sequence["events"]]
        #     for session in sessions:
        #         events = [event["event"] for event in session]
        #         data.append(events)
        # else:
        events = [event["event"] for event in user_sequence["events"]]
        data.append(events)

    return data


def read_params(file: str) -> str:
    return f"./sceneries/{activity}/{file}.json"


def write_result(data, file_name, path="sceneries_results/activity", save_csv=False):
    # Convert data to native Python types for JSON serialization
    def convert_to_python_types(obj):
        if isinstance(obj, dict):
            return {k: convert_to_python_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_python_types(i) for i in obj]
        elif isinstance(obj, (np.integer, np.int64)):  # Handle numpy integer types
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):  # Handle numpy float types
            return float(obj)
        elif isinstance(obj, np.ndarray):  # Handle numpy arrays
            return obj.tolist()
        return obj

    data = convert_to_python_types(data)  # Apply conversion

    # Create directories if they don't exist
    if not os.path.exists(f"./{path}/json"):
        os.makedirs(f"./{path}/json")

    # Write JSON file
    with open(f"./{path}/json/{file_name}.json", "w+") as _file:
        json.dump(data, _file)

    # Optionally save as CSV
    if save_csv:
        write_csv(file_name, path)


def write_csv(file_name, path=f"sceneries_results/{activity}"):
    json_file = open(f"./{path}/json/{file_name}.json")
    json_data = json.load(json_file)

    # Create directories if they don't exist
    if not os.path.exists(f"./{path}/csv"):
        os.makedirs(f"./{path}/csv")

    with open(f"./{path}/csv/{file_name}.csv", "w+", newline="\n") as f:
        writer = csv.DictWriter(f, delimiter=";", fieldnames=json_data["2_sequences"]["sequences"][0])
        writer.writeheader()

        for key in json_data.keys():
            for seq in json_data[key]["sequences"]:
                # seq["grade"] = seq["grade"]["avg"]
                # seq["grave_median"] = seq["grade"]["median"]
                # seq["grave_mode"] = seq["grade"]["mode"]
                # del seq["grade"]
                seq["ids"] = len(seq["ids"])
                seq["sequence"] = ">".join(seq["sequence"])
            # json_data[key]["sequences"]["sequence"] = json_data[key]["sequences"]["sequence"].join('>')
            # print(json_data[key]["sequences"], end="\n\n")
            # writer.writerows(json_data[key]["sequences"])
            writer.writerows(json_data[key]["sequences"])
    json_file.close()


def remap_keys(user_sequences, seq_quantities):
    def process_key(key):
        modified_key = key.replace("[", "").replace("]", "").replace("'", "")
        return [part.strip() for part in modified_key.split(",")]

    return {
        f"{seq_quantities}_sequences": [{"sequence": process_key(k), "total": v} for k, v in user_sequences.items()]
    }


def is_subsequence(subseq, sequence):
    i = 0
    for elem in sequence:
        if i < len(subseq) and elem == subseq[i]:
            i += 1
        if i == len(subseq):
            return True
    return False


def is_sublist_with_gap(sub_list, main_list, gap=20):
    main_len, sub_len = len(main_list), len(sub_list)
    if sub_len == 0:
        return True

    start = 0
    for sub_elem in sub_list:
        found = False
        while start < main_len and (start - (sub_len - 1)) <= gap:
            if main_list[start] == sub_elem:
                found = True
                break
            start += 1
        if not found:
            return False
        start += 1
    return True


def extract_events(event_list):
    data = [event_dict["event"] for event_dict in event_list]
    return data


def get_supports(formatted, minsup, sequence_list):
    res = prefix_mining(formatted, minsup, sequence_list)
    f, i = len(res), 0
    for matches, patt in res:
        i += matches
    return i


def get_sequence_ids(target, data):
    return [row["key"] for _, row in data.iterrows() if is_subsequence(target, row["events"])]


def get_sequence_grade(ids, data):
    filtered_data = data[data["key"].isin(ids)]
    if filtered_data.empty:
        return 0, 0, 0, 0

    grades = filtered_data["grade"].sort_values()
    return grades.mean(), grades.std(ddof=0), grades.median(), grades.mode().iloc[0]


def get_time_span(ids, data):
    filtered_data = data[data["key"].isin(ids)]
    if filtered_data.empty:
        return [0, 0, 0, 0]

    start_times = filtered_data["events"].apply(lambda x: x[0]["time"])
    end_times = filtered_data["events"].apply(lambda x: x[-1]["time"])

    total_time = end_times.max() - start_times.min()
    avg_time = (end_times - start_times).mean()
    return [total_time, avg_time, start_times.min(), end_times.max()]


def get_sequences_length(data):
    lengths = []
    for index, row in data.iterrows():
        lengths.append(len(row["events"]))
    min_len = min(lengths)
    max_len = max(lengths)
    avg_len = statistics.mean(lengths)
    dev_len = statistics.stdev(lengths)
    return min_len, max_len, avg_len, dev_len


def generate_total_csv():
    datas = [pd.read_csv(f"sceneries_results/{activity}/csv/{scenery}.csv", sep=";") for scenery in sceneries_names]
    datas = [df.assign(scenery=i + 1) for i, df in enumerate(datas)]
    total = pd.concat(datas)
    cols = total.columns.tolist()
    cols.insert(0, cols.pop(cols.index("scenery")))
    total = total.reindex(columns=cols)
    total = total.round(2)
    total.to_csv(f"sceneries_results/{activity}/total.csv", sep=";", index=False)


def get_top_k(k=5):
    datas = [pd.read_csv(f"sceneries_results/{activity}/csv/{scenery}.csv", sep=";") for scenery in sceneries_names]
    datas = [df.assign(scenery=i + 1) for i, df in enumerate(datas)]
    datas = [df[df["sequence_size"] > 1] for df in datas]
    datas = [df.nlargest(k, "total") for df in datas]
    total = pd.concat(datas)
    cols = total.columns.tolist()
    cols.insert(0, cols.pop(cols.index("scenery")))
    total = total.reindex(columns=cols)
    total = total.sort_values(by=["scenery", "total"], ascending=False)
    total.to_csv(f"sceneries_results/{activity}/top_k.csv", sep=";", index=False)


def get_supports_by_scenery():
    datas = [pd.read_csv(f"sceneries_results/{activity}/csv/{scenery}.csv", sep=";") for scenery in sceneries_names]
    datas = [df.assign(scenery=i + 1) for i, df in enumerate(datas)]
    info = {
        "scenery": [],
        "i_support": [],
        "s_support": [],
    }
    for index, data in enumerate(datas):
        info["scenery"].append(index + 1)
        info["i_support"].append(
            f"{statistics.mean(data['i_support']):.2f} (+- {statistics.stdev(data['i_support']):.2f})"
        )
        info["s_support"].append(f"{statistics.mean(data['ids']):.2f} (+- {statistics.stdev(data['ids']):.2f})")

    supports_df = pd.DataFrame(info)
    general_info = pd.read_csv(f"sceneries_results/{activity}/general_info.csv", sep=";")
    general_info = general_info.round(2)

    general_info = pd.merge(general_info, supports_df, on="scenery", suffixes=("", "_new"))
    general_info = general_info.drop(columns=["i_support", "s_support"])
    general_info = general_info.rename(columns={"i_support_new": "i_support", "s_support_new": "s_support"})

    general_info.to_csv(f"sceneries_results/{activity}/general_info.csv", sep=";", index=False)


def generate_gen_info():
    g = {
        "scenery": [],
        "minsup": [],
        "max_grade": [],
        "total_sequences": [],
        "time_span_in_days": [],
        "longest_pattern_length": [],
        "shortest_pattern_length": [],
        "average_pattern_length": [],
        "longest_sequence_length": [],
        "shortest_sequence_length": [],
        "average_sequence_length": [],
        "elapsed_time": [],
        "i_support": [],
        "s_support": [],
    }

    general_info = pd.DataFrame(g)
    general_info["scenery"] = general_info["scenery"].astype(str)
    general_info["average_pattern_length"] = general_info["average_pattern_length"].astype(str)
    general_info["average_sequence_length"] = general_info["average_sequence_length"].astype(str)
    general_info.to_csv(f"sceneries_results/{activity}/general_info.csv", sep=";", index=True)
    # elapsed_time = pd.read_csv(f"sceneries_results/{activity}/general_info.csv", sep=";")[["scenery", "elapsed_time"]]

    for index, scenery in enumerate(sceneries_names):
        df = pd.read_csv(f"sceneries_results/{activity}/csv/{scenery}.csv", sep=";")
        minsup = 0.08
        lengths = df["sequence_size"].tolist()
        lengths.sort()
        times = df["avg_time_span"].tolist()
        times.sort()
        file_name = read_params(scenery)
        all_sequences = pd.read_json(file_name)
        min_len, max_len, avg_len, dev_len = get_sequences_length(all_sequences)

        general_info.loc[index, "scenery"] = scenery.split("-")[0]
        general_info.loc[index, "minsup"] = minsup
        general_info.loc[index, "max_grade"] = df["max_grade"].iloc[0]
        general_info.loc[index, "total_sequences"] = len(df)
        general_info.loc[index, "longest_pattern_length"] = lengths[-1]
        general_info.loc[index, "shortest_pattern_length"] = lengths[0]
        general_info.loc[index, "average_pattern_length"] = (
            f"{statistics.mean(lengths)} (+- {statistics.stdev(lengths)})"
        )
        general_info.loc[index, "longest_sequence_length"] = max_len
        general_info.loc[index, "shortest_sequence_length"] = min_len
        general_info.loc[index, "average_sequence_length"] = f"{avg_len:.2f} (+- {dev_len:.2f})"
        general_info.loc[index, "time_span_in_days"] = (
            datetime.datetime.fromtimestamp(times[-1]) - datetime.datetime.fromtimestamp(times[0])
        ).days
    general_info = general_info.round(2)
    general_info.to_csv(f"./sceneries_results/{activity}/general_info.csv", sep=";", index=False)


def alter_support_to_percentage():
    # datas = [pd.read_csv(f"sceneries_results/{activity}/csv/{scenery}.csv", sep=";") for scenery in sceneries_names]
    gen_info = pd.read_csv(f"sceneries_results/{activity}/general_info.csv", sep=";")
    top_k = pd.read_csv(f"sceneries_results/{activity}/top_k.csv", sep=";")

    # for index, data in enumerate(datas):
    #     # data["s_support"] = data["s_support"] / gen_info.loc[index, "total_sequences"]
    #     data = data.round(4)
    #     data.to_csv(f"sceneries_results/{activity}/csv/{sceneries_names[index]}.csv", sep=";", index=False)

    gen_info["s_support"] = gen_info["s_support"] / gen_info["total_sequences"]
    gen_info = gen_info.round(4)
    gen_info.to_csv(f"sceneries_results/{activity}/general_info.csv", sep=";", index=False)
    for i in range(0, len(sceneries_names)):
        # Check if the scenery matches the current index
        if (top_k["scenery"] == i + 1).any():
            # Calculate the support values
            top_k.loc[top_k["scenery"] == i + 1, "s_support"] = top_k["s_support"] / gen_info["total_sequences"].iloc[i]
            # Round the values
            top_k = top_k.round(4)
            # Save the DataFrame to a CSV file
            top_k.to_csv(f"sceneries_results/{activity}/top_k.csv", sep=";", index=False)


# noinspection PyTypedDict
def main():
    sceneries = {}
    g = {
        "scenery": [],
        "minsup": [],
        "max_grade": [],
        "total_sequences": [],
        "time_span_in_days": [],
        "longest_pattern_length": [],
        "shortest_pattern_length": [],
        "average_pattern_length": [],
        "longest_sequence_length": [],
        "shortest_sequence_length": [],
        "average_sequence_length": [],
        "elapsed_time": [],
        "i_support": [],
        "s_support": [],
    }
    if os.path.exists(f"sceneries_results/{activity}/general_info.csv"):
        general_info = pd.read_csv(f"sceneries_results/{activity}/general_info.csv", sep=";")
    else:
        general_info = pd.DataFrame(g)
    general_info["scenery"] = general_info["scenery"].astype(str)
    general_info["average_pattern_length"] = general_info["average_pattern_length"].astype(str)
    general_info["average_sequence_length"] = general_info["average_sequence_length"].astype(str)
    general_info = general_info.round(2)
    general_info.to_csv(f"sceneries_results/{activity}/general_info.csv", sep=";", index=False)

    new_lines = []
    for index, scenery in enumerate(sceneries_names):
        begin = time.time()
        print(f"[{datetime.datetime.now().strftime("%H:%M:%S")}] Processing {scenery}", end=" | ")
        minsup = 0.08
        file_name = read_params(scenery)
        with open(file_name) as file:
            data = json.load(file)
        all_sequences = generate_data(data)
        original_seq = all_sequences.copy()
        max_grade = int(all_sequences["max_grade"].iloc[0])
        get_sequences_length(original_seq)
        formatted = format_tf_data(all_sequences)
        all_sequences["events"] = all_sequences["events"].apply(extract_events)

        # mining_result_gsp = gsp_mining(formatted)
        mining_result_prefix = prefix_mining(formatted, minsup)

        total_sequences = 0
        for sequences in mining_result_prefix:
            total_sequences += len(sequences)

        result = []
        for i in range(len(mining_result_prefix)):
            result.append(remap_keys(mining_result_prefix[i], i + 1))

        # get I-support, F-support, most and least repeated sequences by sequence size
        final_result = {
            f"{i}_sequences": {"sequences": [], "most_repeated": {}, "least_repeated": {}}
            for i in range(1, len(result) + 1)
        }
        lengths = []
        times = []
        for freq in result:
            for key, sequences in freq.items():
                most_repeated = {"total": 0, "sequence": {}}
                least_repeated = {"total": 9999999, "sequence": {}}
                for seq in sequences:
                    sequence_list = seq["sequence"]
                    i_support = get_supports(formatted, minsup, sequence_list)
                    ids = get_sequence_ids(sequence_list, all_sequences)
                    avg, dev, median, mode = get_sequence_grade(ids, all_sequences)
                    total_time, avg_time, initial_time, final_time = get_time_span(ids, original_seq)
                    sequence = {
                        "sequence_size": len(sequence_list),
                        "sequence": sequence_list,
                        "total": seq["total"],
                        "total_time_span": total_time,
                        "avg_time_span": avg_time,
                        "i_support": i_support,
                        "s_support": len(ids),
                        "ids": ids,
                        "grade_avg": avg,
                        "grade_avg_deviation": dev,
                        "grade_median": median,
                        "grade_mode": mode,
                        "max_grade": max_grade,
                    }
                    final_result[key]["sequences"].append(sequence)
                    if sequence["total"] > most_repeated["total"]:
                        most_repeated = sequence
                    if least_repeated["total"] > sequence["total"] > 1:
                        least_repeated = sequence
                    lengths.append(sequence["sequence_size"])
                    times.append(initial_time)
                    times.append(final_time)
                final_result[key]["most_repeated"] = most_repeated
                final_result[key]["least_repeated"] = least_repeated

        lengths.sort()
        times.sort()
        min_len, max_len, avg_len, dev_len = get_sequences_length(original_seq)

        new_lines.append(
            {
                "scenery": scenery.split("-")[0],
                "minsup": minsup,
                "max_grade": max_grade,
                "total_sequences": total_sequences,
                "time_span_in_days": (
                    datetime.datetime.fromtimestamp(times[-1]) - datetime.datetime.fromtimestamp(times[0])
                ).days,
                "longest_pattern_length": lengths[-1],
                "shortest_pattern_length": lengths[0],
                "average_pattern_length": f"{statistics.mean(lengths)} (+- {statistics.stdev(lengths)})",
                "longest_sequence_length": max_len,
                "shortest_sequence_length": min_len,
                "average_sequence_length": f"{avg_len:.2f} (+- {dev_len:.2f})",
                "elapsed_time": time.time() - begin,
                "i_support": "",
                "s_support": "",
            }
        )

        # general_info.loc[index, "scenery"], _ = scenery.split("-")
        # general_info.loc[index, "minsup"] = minsup
        # general_info.loc[index, "max_grade"] = max_grade
        # general_info.loc[index, "total_sequences"] = total_sequences
        # general_info.loc[index, "longest_pattern_length"] = lengths[-1]
        # general_info.loc[index, "shortest_pattern_length"] = lengths[0]
        # general_info.loc[index, "longest_sequence_length"] = max_len
        # general_info.loc[index, "shortest_sequence_length"] = min_len
        # general_info.loc[index, "average_sequence_length"] = f"{avg_len:.2f} (+- {dev_len:.2f})"
        # general_info.loc[index, "average_pattern_length"] = (
        #     f"{statistics.mean(lengths)} (+- {statistics.stdev(lengths)})"
        # )
        # general_info.loc[index, "time_span_in_days"] = (
        #     datetime.datetime.fromtimestamp(times[-1]) - datetime.datetime.fromtimestamp(times[0])
        # ).days

        # print(json.dumps(final_result['2_sequences'], indent=2, default=lambda o: str(o)))
        sceneries[scenery] = final_result
        write_result(final_result, scenery, f"sceneries_results/{activity}", True)
        # break
        end = time.time()
        print(f"Elapsed time: {(end - begin):.2f}")
        # general_info.loc[index, "elapsed_time"] = end - begin

    new_lines_df = pd.DataFrame(new_lines)

    for _, row in new_lines_df.iterrows():
        if row["scenery"] in general_info["scenery"].values:
            general_info.loc[general_info["scenery"] == row["scenery"]] = pd.DataFrame([row])
        else:
            general_info = pd.concat([general_info, row.to_frame().T], ignore_index=True)

    general_info = general_info.sort_values(by="scenery", ascending=True).reset_index(drop=True)
    general_info = general_info.round(2)
    general_info.to_csv(f"sceneries_results/{activity}/general_info.csv", sep=";", index=False)
    get_supports_by_scenery()
    generate_total_csv()
    get_top_k()
    # alter_support_to_percentage()


if __name__ == "__main__":
    main()
    # [write_csv(data) for data in sceneries_names]
    # generate_gen_info()
    # get_supports_by_scenery()
    # generate_total_csv()
    # get_top_k()
    # alter_support_to_percentage()
