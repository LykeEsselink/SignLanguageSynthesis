'''
Functions pertaining to the processing of the sentence, based on the sentence context.
'''
import sign
import re
import pickle

from HamNoSysDict import categoriesHamNoSys as cat #categorydict
infoSigns = pickle.load(open("dictFile.p", "rb")) #signdict


#'Main' function
'''Create the SiGML of the signs
    input: [(word0, PoS-tag, Syntactic_Dependency), (word1, PoS-tag, Syntactic_Dependency), ...]
    output: SiGML code without pre- and postamble'''
def processSentence(context, flag):
    abc = ['A', 'AA', 'B', 'BB', 'C', 'CC', 'D', 'DD', 'E', 'EE', 'F', 'FF',
           'G', 'GG', 'H', 'I', 'II', 'J', 'K', 'KK', 'L', 'LL', 'M', 'MM', 'N',
           'NN', 'O', 'OO', 'P', 'PP', 'Q', 'QQ', 'R', 'RR', 'S', 'SS', 'T',
           'TT', 'U', 'UU', 'V', 'W', 'WW', 'X', 'Y', 'YY', 'Z', 'ZZ']

    infoSigns = pickle.load(open("dictFile.p", "rb"))

    #Detects WH-questions
    wh = whDetect(context)
    #Detects alternative questions
    alt = altDetect(context)

    sigml = ''
    neg = None
    left = False
    end = len(context)
    #Generates markup for the signs in the sentence
    for i,item in enumerate(context):
        word = item[0]
        pos = item[1]
        word = word.upper()
        partly = False

        #Automatically spells single letters
        if word in abc:
            word += '_VINGERSPELLEN'

        #Handles questionmark
        if word == '?':
            #Adds palm up movement when handling WHquestions
            if wh:
                word = 'PALM_OMHOOG'
            #And nothing needs to happen after yes/no questions, so skip the question mark for these
            else:
                continue

        # or alternative questiones
        if word == ',':
            word = 'Q_PART_ALT'

        #Starts negation
        if word == 'N(':
            neg = True
            continue

        #Starts affirmation
        if word == 'A(':
            neg = False
            continue

        #Stops negation and affirmation
        if word == ')N' or word == ')A':
            neg = None
            continue

        #Stores the index
        if "3B" in word:
            left = True

        if word.isnumeric():
            sigml, neg = sign_number(word, neg, wh, sigml, context, infoSigns)
        else:
            #Adds word to matches if partly in dict
            partly, matches = find_matches(word, context, infoSigns)

        #Fingerspell word if not in dict at all, it is not a number, or spell-flag is encountered
        if (not partly and not word.isnumeric()) or flag == 'spell':
            sigml, neg = fingerspell(word, neg, wh, sigml)
        #Finds the sign if a word is partly in the dict
        elif partly:
            currentSign = sign.Sign(word, pos, neg, wh, context, matches)
            #Alternative questions: turn body right
            if alt == True:
                checkL, altNew = leftsideOr(alt, i, word, pos, context)
                #Rotate body left
                if checkL:
                    currentSign.nonmanual.append('<hnm_body tag = "RL"/>')
                #Updates alternative question status
                else:
                    alt = altNew
            #Alternative questions: turn body left
            elif alt == False:
                checkR, altNew = rightsideOr(alt, i, word, pos, context)
                #Rotate body right
                if checkR:
                    currentSign.nonmanual.append('<hnm_body tag = "RR"/>')
                #Updates alternative question status
                else:
                    alt = altNew

            #Performs the sign on the left side with the left hand if the index is 3B
            elif left and (pos == "NOUN" or pos == "ADJ"):
                currentSign = currentSign.mirror()
                left = False
            elif pos == "VERB" and len(item) > 2:
                currentSign.directional(item[2:])
            #Turns the body and head towards INDEX_3A and INDEX_3B
            elif pos != "ADJ":
                if (pos == "NOUN" and i+1 != end) and (i != 0 and end != 1):
                    if context[i+1][0] == "INDEX_3A":
                        currentSign.nonmanual.append('<hnm_body tag = "RR"/>')
                        #the head turn is repeated this often to make it look more natural
                        currentSign.nonmanual.append('<hnm_head tag="SR"/>')
                        currentSign.nonmanual.append('<hnm_head tag="SR"/>')
                        currentSign.nonmanual.append('<hnm_head tag="SR"/>')
                        currentSign.nonmanual.append('<hnm_head tag="SR"/>')
                    elif context[i+1][0] == "INDEX_3B":
                        currentSign.nonmanual.append('<hnm_body tag = "RL"/>')
                        #the head turn is repeated this often to make it look more natural
                        currentSign.nonmanual.append('<hnm_head tag="SL"/>')
                        currentSign.nonmanual.append('<hnm_head tag="SL"/>')
                        currentSign.nonmanual.append('<hnm_head tag="SL"/>')
                        currentSign.nonmanual.append('<hnm_head tag="SL"/>')
                elif word == "INDEX_3A":
                    currentSign.nonmanual.append('<hnm_body tag = "RR"/>')
                    #the head turn is repeated this often to make it look more natural
                    currentSign.nonmanual.append('<hnm_head tag="SR"/>')
                    currentSign.nonmanual.append('<hnm_head tag="SR"/>')
                    currentSign.nonmanual.append('<hnm_head tag="SR"/>')
                    currentSign.nonmanual.append('<hnm_head tag="SR"/>')
                elif word == "INDEX_3B":
                    currentSign.nonmanual.append('<hnm_body tag = "RL"/>')
                    #the head turn is repeated this often to make it look more natural
                    currentSign.nonmanual.append('<hnm_head tag="SL"/>')
                    currentSign.nonmanual.append('<hnm_head tag="SL"/>')
                    currentSign.nonmanual.append('<hnm_head tag="SL"/>')
                    currentSign.nonmanual.append('<hnm_head tag="SL"/>')

            currentSigml = currentSign.get_full_sigml()
            sigml += currentSigml + '\n'

    return sigml

#Helper Functions
'''Detects WH-questions'''
def whDetect(context):
	WHwords = ['HOE', 'WAAROM', 'WANNEER', 'WIE', 'WAT', 'WAAR', 'WAARVOOR']
	for item in context:
		if item[0].upper() in WHwords:
			return True
	return False

'''Detects alternative questions'''
def altDetect(context):
	if context[-1][0] == ',':
		return True
	else:
		return None

'''Signs the number in var word'''
def sign_number(word, neg, WH, sigml, context, dict = infoSigns):
	numbers = list(word)
	length = len(numbers)
	switch = {4:'DUIZEND', 5:'DUIZEND', 6:'DUIZEND', 7:'MILJOEN', 8:'MILJOEN',
			  9:'MILJOEN', 10:'MILJARD', 11:'MILJARD', 12:'MILJARD'}
	#While there are still numbers to sign
	while length > 0:
		#Modular 3 to check what to sign
		mod = length%3
		#Number is between 10-100
		if mod == 2:
			#Checks edge case
			if numbers[0] == '0' and numbers[1] != '0':
				number = written_num(numbers[1])
			#Ignores zeroes
			elif numbers [0] == '0' and numbers[1] == '0':
				numbers = numbers[2:]
				continue
			else:
				#Joins numbers
				number = numbers[0] + numbers[1]
			#Signs number
			_, matches = find_matches(number, context, dict)
			sigml, neg = get_sigml_neg(number, '', neg, WH, [], matches, sigml)
			#Deletes signed numbers
			numbers = numbers[2:]
		# number is between 1-10
		if mod == 1:
			#Gets gloss and sign
			number = written_num(numbers[0])
			_, matches = find_matches(number, context, dict)
			sigml, neg = get_sigml_neg(number, '', neg, WH, [], matches, sigml)
			#Deletes signed number
			numbers = numbers[1:] # delete signed number
		#Number is > 100
		if mod == 0:
			#Don't sign zero
			if numbers[1] == '0' and numbers[2] != '0':
				number = written_num(numbers[2])
			else:
				number = numbers[1] + numbers[2]
			#Ignores 1 and 0 if it's the first number
			if numbers[0] != '1' and numbers [0] != '0':
				#Signs first number
				num = written_num(numbers[0])
				_, matches = find_matches(num, context, dict)
				sigml, neg = get_sigml_neg(num, '', neg, WH, [], matches, sigml)
			#Signs hundred if necessary
			if numbers[0] != '0':
				sigml, neg = get_sigml_neg('HONDERD', '', neg, WH, [], {}, sigml)
			#Signs next two numbers
			_, matches = find_matches(number, context, dict)
			sigml, neg = get_sigml_neg(number, '', neg, WH, [], matches, sigml)
			numbers = numbers[3:] # delete signed numbers
		#Depending on length of list, sign billion/million/thousand
		if length in switch.keys():
			sigml, neg = get_sigml_neg(switch[length], '', neg, WH, [], {}, sigml)
		length = len(numbers)
	return sigml, neg

'''Returns the dict entry for a letter'''
def written_num(num):
	num = int(num)
	if num == 1:
		return 'EEN_1'
	elif num == 2:
		return 'TWEE_2'
	elif num == 3:
		return 'DRIE_3'
	elif num == 4:
		return 'VIER_4'
	elif num == 5:
		return 'VIJF_5'
	elif num == 6:
		return 'ZES_6'
	elif num == 7:
		return 'ZEVEN_7'
	elif num == 8:
		return 'ACHT_8'
	elif num == 9:
		return 'NEGEN_9'
	return str(num)

'''Gets SiGML, as well as negation state'''
def get_sigml_neg(word, pos, neg, WH, context, matches, sigml):
    #Fetches SiGML of word
	currentSign = sign.Sign(word, pos, neg, WH, context, matches)
	currentSigml = currentSign.get_full_sigml()
	sigml += currentSigml + '\n'
    #Fetches negation state
	neg = currentSign.neg
	return sigml, neg

'''Finds matches for a target word, uses the sentence for context'''
def find_matches(word, context, dict = infoSigns):
	partly = False
	matches = {}
	#Loops through dict
	for key in dict.keys():
		if word in key:
			partly = True
			#If target word in key give score of 2
			matches[key] = 2
			#Target word equal to key give score of 3
			if word == key:
				matches[key] = 3
				# break # Will stop looking for other words if it finds the full key: uncommenting will save time but not good for recall

			#Loops through words in context sentence
			for con in context:
				contextword = str(con[0]).upper()
				#Don't give extra points to target word
				if contextword != word:
					#Different types of points for different options
					word1 = contextword + '_'
					word2 = '_' + contextword
					word3 = '(' + contextword + ')'
					#Word1 in key:
					if re.search(r"\b" + re.escape(word1), key):
                        #Adds 1.5 to score
						if key in matches:
							matches[key] = matches[key]+1.5
						else:
							matches[key] = 1.5
                    #Word2 in key:
					if re.search(re.escape(word2) + r"\b", key):
                        #Adds 1.25 to score
						if key in matches:
							matches[key] = matches[key]+1.25
						else:
							matches[key] = 1.25
                    #Word3 in key:
					if re.search(re.escape(word3) + r"\b", key):
                        #Adds 1.25 to score
						if key in matches:
							matches[key] = matches[key]+1.25
						else:
							matches[key] = 1.25
	return partly, matches

'''Fingerspells a word'''
def fingerspell(word, neg, WH, sigml):
	letters = []
	num = 1
	#Loops through word and adds letter to list
	for i in range(0, len(word)-1, 1):
		currletter = word[i]
		#If the next letter is the same as the current letter, adds counter
		if currletter == word[i+1]:
			num+=1
		else:
			#If more letters than 2 are next to each other, joins in groups of 2
			while num > 2:
				letters.append("".join([currletter,]*2))
				num = num - 2
			#Joins last letter(s)
			letters.append("".join([currletter,]*num))
			num = 1
	letters.append(word[-1])
	#Fingerspells each letter
	for letter in letters:
		if letter == '_':
			continue
		letter += '_VINGERSPELLEN'
		sigml, neg = get_sigml_neg(letter, '', neg, WH, [], {}, sigml)
	return sigml, neg

'''Only puts out true when at the left side of the OR
	alt = True: means left side of OR
	alt = False: means right side of OR
	alt = None: means it isn't an alternative question at all'''
def leftsideOr(alt, i, word, pos, context):
	#Ignores queries that aren't alternative questions
	if alt == True:
		#Signs OR in the middle
		if word == 'OF':
			alt = False
			return (False, alt)

		#Signs the first word, as well as the optional index in the middle
		next = context[i+1][0]
		nextnext = context[i+2][0]
		#First noun without index or first noun with index or index of first noun
		if ((i == 0 and pos == 'NOUN' and next != 'of') or
		(i == 0 and pos == 'NOUN' and next == 'INDEX_A' and nextnext != 'of') or
		(i == 1 and word == 'INDEX_3A' and next != 'OF')):
			return (False, alt)

		#Otherwise signs on the left side
		else:
			return (True, alt)

	return (False, alt)

'''Only puts out true when at the right side of the OR
    alt = True: means left side of OR
	alt = False: means right side of OR
	alt = None: means it isn't an alternative question at all'''
def rightsideOr(alt, i, word, pos, context):
	# ignore queries that aren't alternative questions
	if alt == False and word != 'Q_PART_ALT':
		#Signs the verb at the end in the middle
		next = context[i+1][0]
		prev = context[i-1][0]
		if pos == 'VERB' and next == ',' and prev != 'of':
			return (None, None)
		#Otherwise signs on the right side
		else:
			return (True, alt)
	return (False, alt)
