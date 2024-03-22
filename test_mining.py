from gsppy.gsp import GSP
import json, sys

sceneries = [
    "1-first",
    "2-second",
    "3-third",
    "4-fourth",
    "5-fifth",
    "6-sixth",
    "7-seventh",
    "8-eighth",
]


def gsp_mining(sequences: list) -> list:
    result = GSP(sequences).search(0.08)
    return result


def format_tf_data(sequences: list) -> list:
    formated = []
    for user_sequence in sequences:
        formated.append([event["event"] for event in user_sequence.get("events")])
    return formated


def read_params(file: str) -> str:
    file_name = f"./sceneries/{file}.json"
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    return file_name


def write_result(result: list, file: str) -> None:
    with open(f"./sceneries_result/{file}.json", "w+") as _file:
        json.dump(result, _file)


def remap_keys(unit: dict) -> dict:
    seq_quantities = len(list(unit)[0])
    result = {}
    result[f"{seq_quantities}_sequences"] = [
        {"sequence": key, "total": value} for key, value in unit.items()
    ]
    return result


def remap_keys_old(unit: dict) -> list:
    return [{"sequence": key, "total": value} for key, value in unit.items()]


def main() -> None:
    for scenerie in sceneries:
        file_name = read_params(scenerie)

        with open(file_name, "r") as file:
            all_sequences = json.load(file)

        formated = format_tf_data(all_sequences)

        mining_result = gsp_mining(formated)
        result = []

        for unit in mining_result:
            result.append(remap_keys(unit))
            # print("\n\n")

        # mining_result = [dict(sequence=str(i[0]), support=i[1]) for i in mining_result]

        write_result(result, scenerie)
        # for i in result:
        #     print(i)
        #     print("\n\n")


if __name__ == "__main__":
    main()
