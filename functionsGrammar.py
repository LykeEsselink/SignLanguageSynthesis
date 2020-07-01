'''
Functions pertaining to the pre-processsing of the sentence (grammar aspect).
IMPORTANT: all the functions in this file should be replaced by a grammar that covers all these aspects.
'''
import spacy
import nl_core_news_sm

#'Main' Function
'''Approximates and adds indices, negation scope and affirmation scope (should preferably be replaced by a grammar)
    input: a string of NGT glosses
    output: a list of tuples containing NGT glosses and their PoS-tag. Tuples also contain indices in the case of verbs '''
def preprocess(sentence):
    indicator = indicatorCheck(sentence)
    sentence, begin, end = removeIndicators(sentence, indicator)

    #Generates syntactical information of input sentence
    nlp = spacy.load('nl_core_news_sm')
    doc = nlp(sentence.lower())

    #Organises context
    context = []
    size = 0
    already = False
    for sent in doc.sents:
        for token in sent:
            if begin == 0 and size == 0:
            #Appends word with its context (PoS-tag and dependancy)
                context, already, size = replaceIndicators(context, token, indicator, begin, end, already, size)
                context.append((str(token.text), token.pos_, token.dep_))
            #Adds negation/affirmation indicators from before back to sentence
            else:
            	#Appends word with its context (PoS-tag and dependancy)
                context.append((str(token.text), token.pos_, token.dep_))
                context, already, size = replaceIndicators(context, token, indicator, begin, end, already, size)

    #Concatenates special verb cases with 'niet'
    context = neg_verbs_concat(context)
    #Adds negation and affirmation indicators and indexes
    context = indexing(context)
    context = negating(context, context[-1][1]=='PUNCT')
    context = affirming(context, context[-1][1]=='PUNCT')

    return context



#Helper Functions
'''Returns which indicators are present in sentence, else returns false'''
def indicatorCheck(sentence):
	#Negation indicators
	if 'n(' in sentence and ')n' in sentence:
		return ('n(', ')n')
	#Affirmation indicators
	elif 'a(' in sentence and ')a' in sentence:
		return ('a(', ')a')
	#Neither
	else:
		return False

'''Removes indicators and stores their place in the sentence'''
def removeIndicators(sentence, indicator):
	if indicator:
		indBegin, indClose = indicator
		#Saves where indicators were found
		begin = sentence.find(indBegin)
		end = sentence.find(indClose)
		#Removes indicators from sentence temporarily
		sentence = sentence.replace(indBegin, '')
		sentence = sentence.replace(indClose, '')
		#Return new sentence, and where the indicators were located
		return sentence, begin, end
	return sentence, '', ''

'''Replaces indicators in context'''
def replaceIndicators(context, token, indicator, begin, end, already, size):
	if indicator:
		indBegin, indClose = indicator
		size += len(token) + 1 # account for space
		#Adds 'n(' or 'a(' when arrived at the right index, and it has not been added before
		if size >= begin and already == False:
			context.append((indBegin, '', ''))
			already = True
			#Accounts for size of "n(" (would be +=2, but since there is already a space it's +=1)
			size += 1
			return context, already, size

		#Adds ')n' or ')a' when arrived at the right index, and it has encountered 'n(' before
		if size >= end and already:
			context.append((indClose, '', ''))
			already = None
			size += 1
			return context, already, size

	return context, already, size

'''Concatenates certain verbs with 'niet'''
def neg_verbs_concat(context):
	newcontext = []
	newentry = ''
	end = len(context)
	skipone= False
	#Loops over context
	for i, item in enumerate(context):
		#Verbs with integrated negation
		verbs = ['willen', 'wil', 'kunnen', 'kan', 'mogen', 'mag', 'hoeven', \
									'hoeft', 'lukken', 'lukt', 'doen', 'doe']
		#Once 'niet' is encountered
		if item[0] == 'niet':
			#Checks if not out of bounds
			if i-1 != -1: 
				#When the previous entry is in verb list
				preventry = context[i-1][0]
				if preventry in verbs:
					#Lemmatises verbs
					index = verbs.index(preventry)
					if index % 2 == 0:
						index += 1
					#Concatenates the two entries
					newentry += verbs[index] + '_niet'
					newcontext = newcontext[:-1]
					#Adds to new context
					newcontext.append((newentry, 'VERB', ''))
					continue
			#Checks if not out of bounds
			if i+1 != end:
				#When the next entry is in verb list
				nextentry = context[i+1][0]
				if nextentry in verbs:
					#Lemmatises verbs
					index = verbs.index(nextentry)
					if index % 2 == 0:
						index += 1
					#Concatenates the two entries
					newentry += verbs[index] + '_niet'
					newcontext.append((newentry, 'VERB', ''))
					#Makes sure to not add the verb to the context twice
					skipone = True
					continue
		#Skips one context item if necessary
		if not skipone:
			#Adds item to context
			newcontext.append(item)
		else:
			skipone = False

	return newcontext

'''Adds indexes to the sentence if necessary '''
def indexing(context):
	indexes = ["INDEX_3A","INDEX_3B"]

	#Stores the verbs and their respective indexes as tuples
	subjObj = []

	#List of directional verbs
	directionals = ["gooien","lopen","kijken", "roepen","geven","antwoorden","gaan","halen"]

	#List of pronouns (not all are recognised by the parser)
	pronouns = ["ik","jij","hij","zij","index_1","index_2","index_3a","index_3b"]

	#Checks the sentence for verbs and everything that is treated as a noun
	verbCount = len(["yes" for word,tag,_ in context if ((tag == "VERB" and word in directionals) or word == "op_aux")])
	nounCount = len(["yes" for word,tag,_ in context if tag == "NOUN" or word in pronouns])

	zijnCheck = []

	#Checks for adjectives if the sentence does not only consist of verbs and nouns
	if len(context) != verbCount + nounCount:
		adjCheck = ["yes" for _,tag,dep in context if tag == "ADJ"]

		#Checks whether the verb "zijn" is in the sentence if adjectives have been found
		if adjCheck:
			zijnCheck = ["yes" for c in context if c[0] == "zijn" and c[2] == "cop"]

	#Will store the sign associated with the latest index for indexing adjectives
	indexSign = ""


	#Checks each word in the sentence and updates context accordingly with the necessary indexes
	for i, sign in enumerate(context):
		end = len(context) - 1
		word = sign[0]
		tag = sign[1]
		p = ""
		if word == "zijn" and sign[2] == "cop":
			del context[i]
			sign = context[i]
			word = sign[0]
			tag = sign[1]

		#Adds the correct index to the sentence
		if (tag == "NOUN" and word not in ["i_3a","i_3b","op_aux"]) or word in pronouns:
			#Chooses the correct index
			if word in ["ik","index_1"]:
				index = "1"
				if word == "index_1":
					sign = ("ik","")
			elif word in ["jij","index_2"]:
				index = "2"
				if word == "index_2":
					sign = ("jij","")
			elif word == "index_3a" or word == "index_3b":
				indexSign = word
				p = indexes.index(word.upper())
				p = indexes.pop(p)
				index = p[-2:]
				#Adds the used index to the end of the list so it can be re-used
				indexes.append(p)
				tag = ""
			else:
				#Ensures that INDEX_3A and INDEX_3B alternate
				p = indexes.pop(0)
				index = p[-2:]
				#Adds the used index to the end of the list so it can be re-used
				indexes.append(p)
				indexSign = p

			#Adds the index to the last verb
			if subjObj and ((len(subjObj[-1]) < 3 and type(subjObj[-1][0] == int)) or len(subjObj[-1]) < 2):
				subjObj[-1].append((index,i))
			#Creates a new tuple if the last directional verb already has two indexes assinged to it
			elif verbCount > 0 and nounCount > 1:
				subjObj.append([(index,i)])
			#Ensures no index is added after the noun if 'zijn' is not in the sentence
			elif tag == "NOUN" and not zijnCheck:
				indexSign = ""
				continue

			nounCount = nounCount - 1
			#Modifies the word if it's a noun or index_3a or index_3b
			if p:
				#Replaces the word with its corresponding index
				sign = (p,"")
				if tag == "NOUN":
					#Checks whether the index should be added after the noun
					if i != end and context[i+1][1] != "ADJ" and context[i+1][0] not in ["i_3a","i_3b"]:
						#Inserts the index after the noun
						context.insert(i+1,sign)
					#Assures the noun is not replaced by the index
					sign = context[i]

		#Modifies the word in the case that it's an index placed for reference in a later sentence
		elif word in ["i_3a","i_3b"]:
			word = "INDEX_" + word[-2:].upper()
			context[i] = (word,"")
			continue

		elif subjObj and ((tag == "VERB" and word in directionals) or word == "op_aux") and len(subjObj[-1]) != 3:
			#Stores the index of the verb so the indices of the subject and object can be added to it later
			subjObj[-1].insert(0,i)
			verbCount = verbCount - 1

		elif tag == "ADJ" and (sign[2] == "ROOT" or (i != end and context[i+1][1] != "ADJ")) and indexSign:
			#Inserts the index of the most recent noun after the adjective
			context.insert(i+1,(indexSign,""))

		#Removes the dependencies from the words
		context[i] = sign[:2]

	end = len(context)

	
	if subjObj:
		#Loops through the tuples of collected verbs and indices
		for item in subjObj:
			#Adds the indices of the corresponding subject and object to the verbs
			if type(item[0]) == int:
				i = item[0] - (end - len(context))
				verb = list(context[i])
				verb.append(item[1][0])
				if len(item) < 3:
					continue
				verb.append(item[2][0])
				#Deals with the special case of op_aux
				if verb[0] == "op_aux":
					verb[0] = "_".join(["op",verb[2],verb[3]])
					verb = [verb[0],""]
				context[i] = tuple(verb)
			#Removes indices from context in the case that they are unnecessary
			else:
				i = item[0][1]
				if context[i][0] not in pronouns:
					del context[i+1]
				if len(item) == 2 and context[item[1][1]][0] not in pronouns:
					del context[item[1][1]]

	return context

'''Adds negation to context when dealing with negation words'''
def negating(context, question = False):
	newcontext = []
	negationwords = ['geen', 'niemand', 'nergens', 'niets', 'nooit', 'nog_niet', \
	'wil_niet', 'mag_niet', 'kan_niet', 'lukt_niet', 'hoeft_niet','doe_niet']
	last = len(context)
	#Ignores questionmark at the end of the sentence
	buffer = 0
	if question:
		buffer += 1
	#Rejects sentences where negation is already satisfied
	insertion = False
	for i, tuple in enumerate(context):
		newcontext.append(tuple)
		word = tuple[0]
		#Ignores if already manually negated or affirmed
		if word == 'n(' or word == 'a(':
			return context
		#Adds start of negation
		if word in negationwords:
			newcontext.insert(i, ('n(', '', ''))
			insertion = True
		#Adds end of negation
		if i + 1 + buffer == last and insertion:
			newcontext.append((')n', '', ''))

	return newcontext

'''Adds affirmation to context when dealing with affirmation words'''
def affirming(context, question = False):
	newcontext = []
	affirmationwords = ['wel',	'kunnen', 'lukken', 'kunnen_01']
	last = len(context)
	#Ignores questionmark at the end of the sentence
	buffer = 0
	if question:
		buffer += 1
	#Rejects sentences where negation is already satisfied
	insertion = False
	for i, tuple in enumerate(context):
		newcontext.append(tuple)
		word = tuple[0]
		#Ignores if already manually negated or affirmed
		if word == 'a(' or word == 'n(':
			return context
		#Adds start of affirmation
		if word in affirmationwords:
			newcontext.insert(i, ('a(', ''))
			insertion = True
		#Adds end of affirmation
		if i + 1 + buffer == last and insertion:
			newcontext.append((')a', ''))

	return newcontext
