import sgmllib
import string
import re
import pprint

# http://www.programcreek.com/python/example/837/sgmllib.SGMLParser
# http://effbot.org/librarybook/sgmllib.htm

class FoundTitle(Exception):
    pass

class FoundBody(Exception):
    pass

class ExtractText(sgmllib.SGMLParser):

    contents = {}
    reuterCtr = 0

    def __init__(self, count_body, verbose=0):
        sgmllib.SGMLParser.__init__(self, verbose)
        self.count_body = count_body        # this is the number of body's in the file
        self.body = self.data = None

    def handle_data(self, data):
        if self.data is not None:
            self.data.append(data)

    def start_reuters(self, attrs):
        self.id = attrs[4][1]

    def start_title(self, attrs):
        self.data = []

    def end_title(self):
        self.title = string.join(self.data, "")
        #print(self.title)
        self.contents[self.title] = ''


    def start_body(self, attrs):
        self.data = []

    def end_body(self):

        self.body = string.join(self.data, "")
        # self.contents[self.title] = self.body
        self.contents[self.id] = self.title + "\n" +self.body  # combine title with body 
        self.reuterCtr += 1
        # print self.reuterCtr

        if self.reuterCtr == self.count_body:      # if number of body's in file reached, finish parsing
            raise FoundBody # abort parsing!

 # number of body tags in the file
def count_body(file1):
    f = open(file1.name,'r')
    total = 0
    for line in f:
        if "<BODY>" in line:
            total += 1
    f.close()
    return total

def extract(file):
    countbody = count_body(file)
    dict_term = {}
    ctr = 0

    while True:
        # extract title and body from an HTML/SGML stream
        b = ExtractText(countbody)

        try:
            while 1:
                # read small chunks
                s = file.read(1024)
                if not s:
                    break
                b.feed(s)
            b.close()
        except FoundBody:
            return b.contents
            ctr += 1
    return docs

#docs = extract(open("./reut2-021.sgm"))
#pprint.pprint(docs)
