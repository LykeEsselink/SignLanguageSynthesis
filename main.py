'''
Signs NGT sentence using the JASigning avatar

input(str): glossed NGT sentence, separated by spaces
output(sigml-player open): avatar movement
'''
import tempfile
import sys
import functionsGrammar as fg
import functionsMain as fm
import functionsAux as fa
import sendsigml as ss
import sign
import pickle
infoSigns = pickle.load(open("dictFile.p", "rb")) #signdict

def main(sentence, flag = False):

    #General info to make a sigml text work
    xml_version = '1.0'
    encoding = 'utf-8'
    preamble = '<?xml version="{}" encoding="{}"?>\n<sigml>\n\n'.format(xml_version, encoding)
    postamble = '\n</sigml>'

    #Approximates and adds indeces, negation scope and affirmation scope (preferably replaced by a grammar in the future)
    context = fg.preprocess(sentence)

    #Creates the SiGML of the signs
    sigml = fm.processSentence(context, flag)

    #Creates the contents of the SiGML file
    sigmlsentence = preamble + sigml + postamble

    #Creates temporary file
    tempSigmlFile = tempfile.NamedTemporaryFile(suffix = '.sigml')
    tempSigmlFile.write(sigmlsentence.encode())
    tempSigmlFile.read()

    #Feeds it to sigml-player
    ss.sendsigml([tempSigmlFile.name])

    #Delete temporary file
    tempSigmlFile.close()

if __name__ == '__main__':
    #User did not specify glossed sentence
    if len(sys.argv) == 1:
        print("Please specify a glossed sentence to be signed")

    #Explains sign
    elif sys.argv[1] == 'explain':
        #User did not specify sign to be explained
        if len(sys.argv) == 2:
            print("Please specify a sign to be explained")
        #Sign is specified by user
        else:
            #Sign is not in the database
            if not sys.argv[2] in infoSigns:
                print("Please specify a sign that is in the database ()")
            #Sign is in the database
            else:
                fm.explainSign(sign.Sign(str(sys.argv[2])).get_gloss())

    #Fingerspells input
    elif sys.argv[1] == 'spell':
        #User did not specify input to be fingerspelled
        if len(sys.argv) == 2:
            print("Please specify input to be fingerspelled")
        #Input is specified by user
        else:
            main(sys.argv[2], str(sys.argv[1]))

    #Adds a sign to dictionary
    elif sys.argv[1] == 'add':
        #User did not specify all values
        if len(sys.argv) < 5:
            print("Please specify gloss, HamNoSys-SiGML, and SAMPA, in that order")
        #All values are specified
        else:
            #Gloss is already present in dictionary
            if sys.argv[2] in infoSigns:
                #Ask if user is reaaally sure about their decision
                var = input("Gloss already in dictionary\nAre you sure you want to overwrite it?\n(Y/N) ")
                print()
                #Only changes dict entry when answer is Y, y or yes
                if var == 'Y' or var == 'y' or var == 'yes':
                    fa.addSign(sys.argv[2], sys.argv[3], sys.argv[4])
                #Reassures user nothing has been changed in the dictionary.
                else:
                    print("Nothing added to or changed in the dictionary")
            #Gloss not present in dictionary
            else:
                fa.addSign(sys.argv[2], sys.argv[3], sys.argv[4])

    #Processes sentence
    else:
        main(sys.argv[1])
