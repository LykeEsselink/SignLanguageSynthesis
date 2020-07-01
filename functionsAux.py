''' Auxiliary functions: functions that are used in sign.py or offer extra functionality'''
import pickle
infoSigns = pickle.load(open("dictFile.p", "rb")) #signdict

'''Adds a new gloss to the dictionary, accepts complete input and returns the
(new) dict entry'''
def addSign(gloss, hamnosys, sampa, dictionary = infoSigns):
	for entry in dictionary:
		if gloss == entry:
			print("This word is already in the dictionary")
			return dictionary
	dictionary[gloss] = (hamnosys, sampa)
	print("Success!", gloss, dictionary[gloss])
	pickle.dump(dictionary, open("dictFile.p", "wb"))
	return dictionary

'''Accepts a written HamNoSys notation and returns the category it belongs to'''
def findCategory(hamnosys, dictionary = cat):
	#Loops over the categories in the dictionary and searches their corresponding
	#values for a match with the HamNoSys notation
	for key in dictionary.keys():
		for notation in dictionary[key]:
			if notation == hamnosys:
				return key
	#Lets the user know if the HamNoSys notation can't be found
	print("The HamNoSys notation \""+ hamnosys+"\" does not exist in the dictionary")
	return None

'''Shows what hamnosys categories belong to parts of a sign and in what order'''
def explainSign(gloss, show = True, dictionary = infoSigns):
	#Puts all hamnosys-characters in a list
	characters = []
	if gloss in dictionary:
		characters = re.split(",", dictionary[gloss][0])

	sigml = ''
	spacing = ''
	sigmllist = []
	prev = None
	#Goes through all characters of the gloss
	for char in characters:
		#Finds current category
		current = findCategory(char)

		#Assigns 'between'-character to whatever class encountered previously
		if char == 'hambetween':
			current = prev

		#Deletes indentation whenever a closing parenthesis is encountered
		if 'end' in char and current == 'structure/grammar':
			spacing = ''

		#When the category changes
		if current != prev:
			#Saves previous category
			sigmllist.append(sigml)
			sigml = ''

			#Adds current category as a comment
			sigml += '\n{}<!-- {} -->\n'.format(spacing, current)
			prev = current

		#Adds character to sigml notation
		sigml += spacing + '<' + char + '/>\n'

		#Adds indentation when encountering a parenthesis of any type
		if 'begin' in char:
			spacing = '    '

	#Appends last category
	sigmllist.append(sigml)

	#Shows everyting
	if show:
		print('HamNoSys-notation of {} decomposed:\n'.format(gloss), ' '.join(map(str, sigmllist)))
	return sigmllist

'''Returns the new direction of HamNoSys notations based on the indexes'''
def direction(letters,hamtype,indexes,steps=0):
	axes = ["o","or","r","ir","i","il","l","ol"]
	if "hampalm" in hamtype:
		axes = ["u","ur","r","dr","d","dl","l","ul"]
		if hamtype == "hampalmu":
			axes.reverse()

	#Returns the letters unchanged if they are not in the selected list
	try:
		i = axes.index(letters)
	except:
		return letters

	#Calculates the index of the new direction based on the index of the
	#current direction and the indexes of the verb
	if steps > 0:
		i = i + steps
	elif indexes[0] == "3B":
		if indexes[1] == "1":
			i = i + 3
		elif indexes[1] == "2":
			i = i + 1
		elif indexes[1] == "3A":
			i = i + 2
	elif indexes[0] == "3A":
		if indexes[1] == "1":
			i = i + 5
		elif indexes[1] == "2":
			i = i + 7
		elif indexes[1] == "3B":
			i = i + 6
	elif indexes[0] == "2":
		if indexes[1] == "1":
			i = i + 4
		elif indexes[1] == "3A":
			i = i + 3
		elif indexes[1] == "3B":
			i = i + 5
	elif indexes[0] == "1":
		if indexes[1] == "2":
			i = i
		elif indexes[1] == "3A":
			i = i + 1
		elif indexes[1] == "3B":
			i = i + 7

	#Makes a correction in the case that the index is higher than the max index of the list
	if i > 7:
		i = i - 8

	return axes[i]

'''Accepts a direction and returns its opposite'''
def opposite(direction):
	opposites = ["d","u","l","r","o","i"]
	m = len(opposites)
	o = ""

	for c in direction:
		p = opposites.index(c)
		#Checks whether the index of the character is an odd or even number and
		#gets the opposite character from opposites accordingly
		if (p % 2) == 0 and p != m:
			o += opposites[p + 1]
		else:
			o += opposites[p - 1]
	return o