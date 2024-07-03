import json
import csv

filename = "../sceneries_results/json/8-eighth.json"  #

arquivo = open(filename)
# arquivo = open('results_new2006/2-second.json')
json_data = json.load(arquivo)

with open(filename.replace(".json", ".csv"), "w", newline="\n") as f:
    writer = csv.DictWriter(f, delimiter=";", fieldnames=json_data["1_sequences"]["sequences"][0])
    writer.writeheader()

    for key in json_data.keys():
        for seq in json_data[key]["sequences"]:
            seq["sequence"] = ">".join(seq["sequence"])
        # json_data[key]["sequences"]["sequence"] = json_data[key]["sequences"]["sequence"].join('>')
        # print(json_data[key]["sequences"]["sequence"])
        writer.writerows(json_data[key]["sequences"])
        writer.writerows(json_data[key]["sequences"])

arquivo.close()
