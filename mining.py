from gsppy.gsp import GSP
from prefixspan import PrefixSpan
import pandas as pd
import json
import csv
import time
import statistics
import datetime

sceneries_names = [
    # "1-first",
    # "2-second",
    # "3-third",
    # "4-fourth",
    # "5-fifth",
    # "6-sixth",
    # "7-seventh",
    # "8-eighth",
    "9-ninth",
    "10-tenth",
    "11-eleventh",
    "12-twelfth",
]

activity = 1


def gsp_mining(sequences_list: list, minsup: float = 0.08) -> list:
    return GSP(sequences_list).search(minsup)


def prefix_mining(sequences_list: list, minsup: float = 0.08, subsequence=None) -> list:
    ps = PrefixSpan(sequences_list, minlen=2)
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
        data.append([event["event"] for event in user_sequence["events"]])
    return data


def read_params(file: str) -> str:
    return f"./sceneries/{activity}/{file}.json"


def write_result(data, file_name, path=f"sceneries_results/{activity}", save_csv=False):
    with open(f"./{path}/json/{file_name}.json", "w+") as _file:
        json.dump(data, _file)

    if save_csv:
        write_csv(file_name, path)


def write_csv(file_name, path=f"sceneries_results/{activity}"):
    json_file = open(f"./{path}/json/{file_name}.json")
    json_data = json.load(json_file)
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
    len_subseq = len(subseq)
    len_sequence = len(sequence)
    i, j = 0, 0

    if len_subseq > len_sequence:
        return False

    while i < len_subseq and j < len_sequence:
        # subseq_element = subseq[i].strip() if isinstance(subseq[i], str) else subseq[i]
        # sequence_element = (sequence[j].strip() if isinstance(sequence[j], str) else sequence[j])
        if subseq[i] == sequence[j]:
            i += 1
        j += 1

    return i == len_subseq


def is_sublist_with_gap(sub_list, main_list, gap=20):
    if not sub_list:
        return True

    sub_len = len(sub_list)
    main_len = len(main_list)

    for start in range(main_len - sub_len + 1):
        sub_index = 0
        matches = 0

        for main_index in range(start, main_len):
            if main_list[main_index] == sub_list[sub_index]:
                matches += 1
                sub_index += 1
                if matches == sub_len:
                    return True
            elif main_index - start >= sub_index * (gap + 1):
                break

    return False


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
    ids = []
    for index, row in data.iterrows():
        if is_subsequence(target, row["events"]):
            ids.append(row["key"])
    return ids


def get_sequence_grade(ids, data):
    grades = []
    for index, row in data.iterrows():
        if row["key"] in ids:
            grades.append(row["grade"])

    grades.sort()
    avg = statistics.mean(grades) if grades else 0
    dev = statistics.stdev(grades) if grades else 0
    median = statistics.median(grades) if grades else 0
    mode = statistics.mode(grades) if grades else 0
    return avg, dev, median, mode


def get_time_span(ids, data):
    times = []
    avg_times = []
    for index, row in data.iterrows():
        if row["key"] in ids:
            events = row["events"]
            t1 = events[0]["time"]
            t2 = events[-1]["time"]
            times.append(t1)
            times.append(t2)
            avg_times.append(t2 - t1)
    times.sort()
    total = (times[-1]) - (times[0])
    avg = sum(avg_times) / len(avg_times) if avg_times else 0
    initial = times[0]
    final = times[-1]
    return [total, avg, initial, final]


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
    general_info = pd.merge(general_info, supports_df, on="scenery")
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
        general_info.loc[index, "average_pattern_length"] = f"{statistics.mean(lengths)} (+- {statistics.stdev(lengths)})"
        general_info.loc[index, "longest_sequence_length"] = max_len
        general_info.loc[index, "shortest_sequence_length"] = min_len
        general_info.loc[index, "average_sequence_length"] = f"{avg_len:.2f} (+- {dev_len:.2f})"
        general_info.loc[index, "time_span_in_days"] = (
            datetime.datetime.fromtimestamp(times[-1]) - datetime.datetime.fromtimestamp(times[0])
        ).days
    general_info = general_info.round(2)
    general_info.to_csv(f"./sceneries_results/{activity}/general_info.csv", sep=";", index=False)
    print(general_info.shape)


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
        if (top_k['scenery'] == i + 1).any():
            # Calculate the support values
            top_k.loc[top_k['scenery'] == i + 1, "s_support"] = top_k["s_support"] / gen_info["total_sequences"].iloc[i]
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
    }
    general_info = pd.DataFrame(g)
    general_info["scenery"] = general_info["scenery"].astype(str)
    general_info["average_pattern_length"] = general_info["average_pattern_length"].astype(str)
    general_info["average_sequence_length"] = general_info["average_sequence_length"].astype(str)
    general_info = general_info.round(2)
    general_info.to_csv(f"sceneries_results/{activity}/general_info.csv", sep=";", index=False)

    for index, scenery in enumerate(sceneries_names):
        begin = time.time()
        print(f"[{datetime.datetime.now().strftime("%H:%M:%S")}] Processing {scenery}", end=" | ")
        minsup = 0.08
        file_name = read_params(scenery)
        all_sequences = pd.read_json(file_name)
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

        general_info.loc[index, "scenery"], _ = scenery.split("-")
        general_info.loc[index, "minsup"] = minsup
        general_info.loc[index, "max_grade"] = max_grade
        general_info.loc[index, "total_sequences"] = total_sequences
        general_info.loc[index, "longest_pattern_length"] = lengths[-1]
        general_info.loc[index, "shortest_pattern_length"] = lengths[0]
        general_info.loc[index, "longest_sequence_length"] = max_len
        general_info.loc[index, "shortest_sequence_length"] = min_len
        general_info.loc[index, "average_sequence_length"] = f"{avg_len:.2f} (+- {dev_len:.2f})"
        general_info.loc[index, "average_pattern_length"] = (
            f"{statistics.mean(lengths)} (+- {statistics.stdev(lengths)})"
        )
        general_info.loc[index, "time_span_in_days"] = (
            datetime.datetime.fromtimestamp(times[-1]) - datetime.datetime.fromtimestamp(times[0])
        ).days

        # print(json.dumps(final_result['2_sequences'], indent=2, default=lambda o: str(o)))
        sceneries[scenery] = final_result
        write_result(final_result, scenery, f"sceneries_results/{activity}", True)
        # break
        end = time.time()
        print(f"Elapsed time: {(end - begin):.2f}")
        general_info.loc[index, "elapsed_time"] = end - begin
    general_info = general_info.round(2)
    general_info.to_csv(f"sceneries_results/{activity}/general_info.csv", sep=";", index=False)
    get_supports_by_scenery()
    generate_total_csv()
    get_top_k()
    # alter_support_to_percentage()


if __name__ == "__main__":
    # main()
    # [write_csv(data) for data in sceneries_names]
    generate_gen_info()
    get_supports_by_scenery()
    generate_total_csv()
    get_top_k()
    # alter_support_to_percentage()
