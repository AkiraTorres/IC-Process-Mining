def processSeq(sequences, args, fileSuffix):
	ps = PrefixSpan(sequences)
	result = ps.frequent(len(sequences) * float(args[2]), closed=True) #list of tuples
	#order by frequence
	result.sort(key=lambda tup: tup[0], reverse = True)
	
	#write to file
	file = open(args[1]+"_"+args[2].replace(".json","")+"_OUTPUT_"+fileSuffix+".json","w") 
	
	file.write(json.dumps(result)) 	
	#print on screen
	print(json.dumps(result))

#arguments: [1] dataFilePath [2] support (0-1)
if __name__ == '__main__': 
	from prefixspan import PrefixSpan
	import json
	import sys

	#load data
	with open(sys.argv[1], 'r') as dataFile:
		allSequences = json.load(dataFile)

	#TODO: juntar num arquivo só os dois conjuntos, ou tavlez tb as seqs de todas as ativs
	processSeq(list(map(lambda seq: seq['events'] , allSequences['goodSequences'])), sys.argv, 'GOOD')
	processSeq(list(map(lambda seq: seq['events'] , allSequences['badSequences'])), sys.argv, 'BAD')

