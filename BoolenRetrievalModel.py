from nltk.stem import PorterStemmer      #Stemmer for normalizing words
from nltk.tokenize import word_tokenize #break stream into tokens
from collections import OrderedDict     #Dict in unordered thats why I preferred OrderedDict
import json                            #wrting and reading index from json file
import os.path                            
# import nltk
# nltk.download('punkt')                 #punkt need to be downloaded once

ps = PorterStemmer()
class BooleanRetrievalModel:
    dict = OrderedDict()    #Inverted Index (key = Terms , Values = List Of Docs in which they occured)
    posi = OrderedDict()     #positional Index (key = term , value = ordereddict(key = docid , value = positions))
    NumberOfDocs = 448      #total number of provided Documents
    stopwordslist = []       #provided stopwords
    def __init__(self):
       self.read()           #reading Positional Index from File if exists else creating and writing to file
  
    def write(self):      #writng index to file
      towrite = (json.dumps(list(self.posi.items())))  #transforming in json format
      f= open("/mnt/d/Academics/6th/IR/Assignment#1/Index.json" , "w") 
      f.write(towrite)
      f.close()
    def read(self):    #reading index
      if os.path.isfile("/mnt/d/Academics/6th/IR/Assignment#1/Index.json"): #if index already exists then read
        f = open("/mnt/d/Academics/6th/IR/Assignment#1/Index.json" , "r")
        toread = json.loads(f.read()) #json data 
        i = 0
        x = self.posi       #creating positional index
        while( i < len(toread)):
          y = toread[i][1]          #toread[i][1] = list of positions
          z = {int(K) : V for K,V in y.items()}
          x[toread[i][0]] = OrderedDict(z)    #toread[i][0] is a term
          i += 1
        self.createInvertedIndex()
        f.close()
      else:   #if index doesnt exist
        self.createPositionalIndex()
        self.write()
  


    def createPositionalIndex(self):
      sf = open("/mnt/d/Academics/6th/IR/Assignment#1/provided/Stopword-List.txt" , "r")
      for line in sf:
        for sword in line.split():
          self.stopwordslist.append(sword)  #getting stop words from file
      sf.close()
      for i in range(self.NumberOfDocs):
        f = open("/mnt/d/Academics/6th/IR/Assignment#1/static/Documents/" + str(i + 1) + ".txt")

        index = 1
        line = " "
        for line in f:
          for word in line.split():
            word = word.strip(".,?:)(%'1234567890#$!{}") #removing there characters if they are at the begining
            word = word.replace("/" , " ")        #cluster/classification => claster classification
            word = word.replace("-" , " ")        #bag-of-patterns => bag of patterns
            tokenizedword = word_tokenize(word)    #chopping on spaces
            for word in tokenizedword:
              if word in self.stopwordslist:
                continue
              word = ps.stem(word)              #stemming
              if( word in self.posi):           #if term already exists in index then append doct id to list
                x = self.posi[word]
                if i + 1 not in x.keys():     
                  x[i + 1] = OrderedDict()
                  x[i + 1] = [index]
                else:
                  x[i + 1].append(index)
              else:
                self.posi[word] = OrderedDict()
                self.posi[word][i + 1] = [index]
              index += 1
          
        f.close()
      self.createInvertedIndex()


    def createInvertedIndex(self):
      for K , V in self.posi.items():          #creating inverted index from positional index
        self.dict[K] = list(V.keys())
      

    def ProximityQuery(self , term1 , term2 , k):
      p1 = OrderedDict()                      #posting list of term1
      p2 = OrderedDict()    #posting list of term2
      term1 = ps.stem(term1)
      term2 = ps.stem(term2)
      if( term1 in self.posi):
        p1 =  self.posi[term1]
      if( term2 in self.posi):
        p2 =  self.posi[term2]
      result = self.PositionalIntersect( list(p1.keys()) , list(p2.keys()),k , term1 , term2)
      print(result)
      return result

    def Query(self , query):  #Query Processing starts
      x = query.split(' ')    #splitting query on spaces
      # k = int(query[query.index('/') : len(query)])
      u = query.find('/')
      k = 0
      if u != -1:
          k = int(query[query.index('/') + 1 : len(query)])
      if(x[-1] == str("/" + str(k))):         #query like feature track /5
        return self.ProximityQuery(x[0] , x[1] , int(k) + 1)
      else:
        return self.preprocessQuery(query)
    def preprocessQuery(self , query):   #separating terms and queries into lists
      i = 0
      # print("in pre processing")
      terms = []
      operators = []
      tokenizedquery = word_tokenize(query)
      while (i < len(tokenizedquery)):
        if(tokenizedquery[i] == "and" or tokenizedquery[i] == "AND"):
          operators.append("and")
          i += 1
        elif(tokenizedquery[i] == "or" or tokenizedquery[i] == "OR"):
          operators.append("or")
          i += 1
        elif(tokenizedquery[i] == "not" or tokenizedquery[i] == "NOT"):
          terms.append(tokenizedquery[i + 1])
          terms.append("not")       #to identify if it a not applied on term
          i += 2
        else:
          terms.append(tokenizedquery[i])
          terms.append("zz")
          i += 1        
      return self.process(terms , operators)
    def process(self , terms , operators):  
      # print("in porcess")
      allpostings = self.allpostings(terms)
      # print(type(allpostings))
      # print(operators)
      while( operators):
        operation = operators.pop(0)
        p1 = allpostings.pop(0)
        # allpostings.pop(0)
        p2 = allpostings.pop(0)
        allpostings.insert(0 , self.processinvertedindex(p1 , p2 , operation))
      matchedDocs = allpostings.pop(0)
      # print(sorted(self.dict))
      print("Documents Retrieved = " , matchedDocs)
      return matchedDocs

    def allpostings(self , terms):   #returning posting lists of all terms in query
      postings = []
      i = 0
      while ( terms ):
        term = terms.pop(0)
        term = ps.stem(term)
        if(terms[0] == "not"):    
          postings.append(self.Complement(term))
        else:
           postings.append(self.postingsofterm(term))
        terms.pop(0)
      return postings
    def postingsofterm(self , term): #return posting list of single term
      ret = []
      if(term in self.dict):
        ret = self.dict[term]
      print("posting list of " + term + ":" , ret)
      return ret

    def processinvertedindex(self , p1 , p2 , operator): # Taking two postings and operator from terms and operators list and calculating them
      result = []
      if(operator == 'and'):
         result = self.Intersection(p1 , p2) 
      elif(operator == 'or'):
        result = self.Merge(p1 , p2)
      return result
 

    def PositionalIntersect(self , p1 , p2 , k , term1 , term2):  #Algorithm ko find at most k terms common docs
      i , j = 0 , 0
      result = []
      while( i < len(p1) and j < len(p2)):
        x = p1[i]
        y = p2[j]
        if(x == y):
          pp1 = self.posi[term1][x]
          pp2 = self.posi[term2][y]
          i1 , j1  = 0 , 0
          flag = False

          while ( i1 < len(pp1) ):
            while(j1 < len(pp2) ):
              if(abs( pp1[i1] - pp2[j1]) <= k):
                # print(p1[i])
                result.append(p1[i])
                flag = True
                break
              j1 += 1
            if(flag):
              break
            i1 += 1

          i += 1
          j += 1
          
        elif (x <= y):
          i += 1
        else:
          j += 1
      # print("Result")
      # print(result)
      return result
      
    def Intersection(self , postinglist1 , postinglist2):  #And Query by intersecting two posting lists
      i , j = 0 , 0
      result = []
      while i != len(postinglist1) and j != len(postinglist2):
        if postinglist1[i] == postinglist2[j]:
          result.append(postinglist1[i])
          i += 1 
          j += 1
        elif postinglist1[i] < postinglist2[j]:
          i += 1
        else:
          j += 1 
      return result


    def Merge(self , postinglist1 , postinglist2):    #solving Or query merging two posting list
      result = list(set(postinglist1 + postinglist2))
      result = sorted(result)
      return result

    
    def Complement(self , term): #Not Query
      postinglist = []
      term = ps.stem(term)
      if term in self.dict:
        postinglist = self.dict[term]
      # print(postinglist)
      return self.NotQuery(postinglist)

    def NotQuery(self , postinglist1):
      totalDocIds = list(range (1 ,1 + self.NumberOfDocs))
      result = [item for item in totalDocIds if item not in postinglist1]

      return result
b = BooleanRetrievalModel()
b.Query("feature track /5")