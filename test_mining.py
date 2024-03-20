from gsppy.gsp import GSP
import json, sys


def gsp_mining(sequences: list) -> list:
    result = GSP(sequences).search(0.08)
    return result


def format_tf_data(sequences: list) -> list:
    formated = []
    for user_sequence in sequences:
        formated.append([event["event"] for event in user_sequence.get("events")])
    return formated


def read_params():
    json_data = "./teste.json"
    if len(sys.argv) > 1:
        json_data = sys.argv[1]
    return json_data


def main():
    json_data = read_params()

    with open(json_data, "r") as file:
        all_sequences = json.load(file)

    formated = format_tf_data(all_sequences)

    for i in gsp_mining(formated):
        print(i, end="\n\n")


if __name__ == "__main__":
    main()
