if __name__ == '__main__':
    from gsppy.gsp import GSP
    # import simplejson as json
    import json

    # import os

    # load data
    with open('data_Ativ2.json', 'r') as dataFile:
        # data = dataFile.read()
        allSequences = json.load(dataFile)

    goodSequences = allSequences['goodSequences']
    goodSequences = list(map(lambda seq: seq['events'], goodSequences))

    badSequences = allSequences['badSequences']
    badSequences = list(map(lambda seq: seq['events'], badSequences))

    # transactions = [
    # 		['Bread', 'Milk'],
    # 		['Bread', 'Diaper', 'Beer', 'Eggs'],
    # 		['Milk', 'Diaper', 'Beer', 'Coke'],
    # 		['Bread', 'Milk', 'Diaper', 'Beer'],
    # 		['Bread', 'Milk', 'Diaper', 'Coke']
    # 	]

    # result = GSP(goodSequences[0:10]).search(0.3)
    result = GSP(badSequences[0:10]).search(0.3)

    for i in result:
        print(i)
