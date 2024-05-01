import sys
import json
import csv
import argparse
import xml.etree.ElementTree as ET


file = sys.argv[1]
if file == '--help': #Could implement this using argparse but done like this for simplicity here
    print()

extension = file[-4:]
data = [] #List to store the information before 

if extension == '.xml': #Processing for .xml files
    tree = ET.parse(file)
    root = tree.getroot()
    items = []
    for i in root.iter('ENT'):
        entdict = {} #Entity Dictionary, stores the data from each entity
        for j in i:
            text = j.text
            tag = j.tag.lower()
            if text != ' ' and tag != 'country':
                if tag == 'company': #Processing to figure out if it's a name or company
                    tag = 'organization'
                elif tag == 'postal_code':
                    tag = 'zip'
                    if text[-1] == ' ':
                        text = text[:-3]
                entdict.update({tag: text})
        data.append(entdict)
    if len(data) <= 0:
        print('Input file does not conform to format given in example files', file=sys.stderr)
        sys.exit(1)
    

elif extension == '.tsv': #Processing for .tsv files
    fields = ['first', 'middle', 'last', 'organization', 'address', 'city', 'state', 'county', 'zip', 'zip4']
    tsvFile = open(file) 
    input = csv.reader(tsvFile, delimiter='\t')
    #parsed = json.loads(data)
    try:
        for line in input:
            if input.line_num != 1:
                first = ''
                middle = ''
                entdict = {}
                for index, label in enumerate(fields):
                    value = line[index]
                    if label == 'first': #Processing the first, middle, last name fields into one name.
                        first = value
                        continue
                    elif (label == 'middle') or (value == 'N/M/N'):
                        middle = value
                        continue
                    elif label == 'last':
                        if first != '':
                            if middle != '':
                                value = ' '.join([first, middle, value])
                            else:
                                value = ' '.join([first, value])
                            label = 'name'
                        else:
                            label = 'organization'
                    
                    if value != '' and value != 'N/A':
                        if label == 'zip4': #Processing the zip4 and zip fields into one zip code
                            zip = entdict['zip']
                            value = ' '.join([zip, '-', value])
                            label = 'zip'
                        entdict.update({label: value})
                data.append(entdict)
    except:
        print('Input file does not conform to format given in example files', file=sys.stderr)
        sys.exit(1)

elif extension == '.txt': #Processing for .txt files
    txtList = open(file).read().lstrip().split('\n\n') #Read the input file, remove leading newlines, and split into a list of entries
    for i in txtList:
        entdict = {}
        lines = i.split('\n') #Split each entry into it's different lines
        
        if len(lines) > 4: #Checking input for errors
            print('Input file does not conform to format given in example files', file=sys.stderr)
            sys.exit(1)
        lines = [x.lstrip() for x in lines] #remove leading whitespace from entries
        if len(lines) == 4: #For the .txt files, each entry has 4 lines if a county is present or 3 lines otherwise
            county = lines.pop(2) 
            hasCounty = True

        entdict.update({'name': lines[0]})
        entdict.update({'street': lines[1]})
        location = lines[2].split(',') #split this line into [city, state and zip]
        entdict.update({'city': location[0]})

        if hasCounty:
            entdict.update({'county': county})
        location = location[1].split() #splitting into [state, zip]
        entdict.update({'state': location[0]})
        entdict.update({'zip': location[1]})
        data.append(entdict)
    else:
        print('Error in argument list', file=sys.stderr)
        sys.exit(1)

output = json.dumps(data, indent=2) #Convert python dict data into a json string
print(output)
sys.exit(0)
