import gzip
from collections import defaultdict
import re
import random
import numpy

def readGz(f):
  for l in gzip.open(f):
    yield eval(l)

### Purchasing baseline: just rank which items are popular and which are not, and return '1' if an item is among the top-ranked

itemCount = defaultdict(int)
userCount = defaultdict(int)
totalPurchases = 0
trainData = []
validateData = []
numOfPairs = 0
validatedItems = []
validatedUsers = []
ListOfCreatedPairs = {}
entryCount = 0
totalPurchases = 100000

for l in readGz("train.json.gz"):
  if (entryCount < 100000):
    trainData.append((l['reviewerID'], l['itemID']))
  if (entryCount >= 950000):
    validateData.append((l['reviewerID'], l['itemID']))
  user,item = l['reviewerID'],l['itemID']
  itemCount[item] += 1
  userCount[user] += 1
  entryCount += 1

mostPopular = [(itemCount[x], x) for x in itemCount]
mostPopular.sort()
mostPopular.reverse()
print "length of trainData", len(trainData) 
### create 50000 random pair of 
while (numOfPairs < 50000):
  randomUser = random.randint(0,99999)
  randomItem = random.randint(0,99999)

  
  if ((trainData[randomUser][0], trainData[randomItem][1]) not in trainData):
    
    #ListOfCreatedPairs.append([trainData[randomUser]['reviewerID'], trainData[randomItem]['itemID']])
    #ListOfCreatedPairs[trainData[randomUser]['reviewerID']].append(trainData[randomItem]['itemID'])
    validateData.append((trainData[randomUser][0], trainData[randomItem][1]))
    validatedUsers.append(trainData[randomUser]['reviewerID'])
    validatedItems.append(trainData[randomItem]['itemID'])
    numOfPairs += 1
      
    
goodBuyers = [(userCount[x], x) for x in userCount]
goodBuyers.sort()
goodBuyers.reverse()

### classification accuracy = 1 - hammingLoss
### hammingLoss = the fraction of labels that are incorrectly predicted
### use popularity of item to get the better prediction

hamming = []
for n in range(1, 100):
  return1 = set()
  count = 0
  for ic, i in mostPopular:
    count += ic
    return1.add(i)
    if count > totalPurchases/n: break

  numOfCorrect = 0
  total = 0

  for item in validatedItems:
    if (item not in return1):
      numOfCorrect += 1
    total += 1
  for review in validateData:
    if (review['itemID'] in return1):
        numOfCorrect += 1
    total += 1
  hamming.append(numOfCorrect / 2.0 / totalPurchases)
  print "Hamming loss at n = ", n, " is ", (numOfCorrect / 2.0 / totalPurchases)

print "min hamming is ", min(hamming), " at n = ", numpy.argmin(hamming)

userHamming = []
for n in range(1, 100):
  return2 = set()
  count = 0
  for ic, i in goodBuyers:
    count += ic
    return2.add(i)
    if count > totalPurchases/n: break

  numOfCorrect = 0
  total = 0

  for item in validatedItems:
    if (item not in return2):
      numOfCorrect += 1
    total += 1
  for review in validateData:
    if (review['reviewerID'] in return2):
        numOfCorrect += 1
    total += 1
  hamming.append(numOfCorrect / 2.0 / totalPurchases)
  print "Hamming loss at n = ", n, " is ", (numOfCorrect / 2.0 / totalPurchases)

print "min hamming is ", min(userHamming), " at n = ", numpy.argmin(userHamming)


predictions = open("predictions_Purchase.txt", 'w')
predictions.write("userID-itemID,prediction\n")
for l in open("pairs_Purchase.txt"):
  if l.startswith("userID"):
    #header
    predictions.write(l)
    continue
  u,i = l.strip().split('-')
  if u in return2:
    predictions.write(u + '-' + i + ",1\n")
  else:
    predictions.write(u + '-' + i + ",0\n")

predictions.close()