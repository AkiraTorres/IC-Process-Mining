if __name__ == '__main__':
    from gsppy.gsp import GSP
    # import simplejson as json
    import json

    # import os

    # load data
    with open('data_Ativ1.json', 'r') as dataFile:
        # data = dataFile.read()
        allSequences = json.load(dataFile)

    with open('events_by_user.json', 'r') as file:
        extracted_sequences = json.load(file)

    with open('all_events.json', 'r') as file:
        all_sequences = json.load(file)

    goodSequences = allSequences['goodSequences']
    goodSequences = list(map(lambda seq: seq['events'], goodSequences))

    badSequences = allSequences['badSequences']
    badSequences = list(map(lambda seq: seq['events'], badSequences))

    sequences = list(map(lambda seq: seq['events'], extracted_sequences))
    all_sequences_list = list(map(lambda seq: seq['events'], all_sequences))
    # print(goodSequences[0:3])
    # print("\n")
    # print(sequences)

    # transactions = [
    # 		['Bread', 'Milk'],
    # 		['Bread', 'Diaper', 'Beer', 'Eggs'],
    # 		['Milk', 'Diaper', 'Beer', 'Coke'],
    # 		['Bread', 'Milk', 'Diaper', 'Beer'],
    # 		['Bread', 'Milk', 'Diaper', 'Coke']
    # 	]

    # result = GSP(goodSequences[0:3]).search(0.3)
    # result = GSP(badSequences[0:10]).search(0.3)
    result = GSP(sequences).search(0.3)
    # result = GSP(all_sequences_list).search(0.3)
    # result = GSP(data).search(0.3)

    # print(goodSequences[0:5])

    # print(extracted_sequences[0:5])

    for i in result:
        print(i, end="\n\n")
