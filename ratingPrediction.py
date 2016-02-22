import gzip
from collections import defaultdict
from random import random
import gzip
#import simplejson

def parse(filename):
  f = gzip.open(filename, 'r')
  entry = {}
  for l in f:
    l = l.strip()
    colonPos = l.find(':')
    if colonPos == -1:
      yield entry
      entry = {}
      continue
    eName = l[:colonPos]
    rest = l[colonPos+2:]
    entry[eName] = rest
  yield entry

userRatings = defaultdict(list)
nUser = defaultdict(int)
nItem = defaultdict(int)
count = 0
# length = 568462
ratings = []
allRatings = []
for l in parse("finefoods.txt.gz"):
  if (str("review/userId") in l and str("product/productId") in l and str("review/score") in  l):
    if (count < 390000):
      allRatings.append(float(l['review/score']))
      ratings.append((l['review/userId'], l['product/productId'], l['review/score']))
      nUser[l['review/userId']] += 1
      nItem[l['product/productId']] += 1
      userRatings[l['review/userId']].append(float(l['review/score']))
  count += 1


globalAverage = sum(allRatings) / len(allRatings)
userAverage = {}
for u in userRatings:
  userAverage[u] = sum(userRatings[u]) / len(userRatings[u])

print "finishing baseline prediction..."
nTrain = len(ratings)
MSE = 0
lambList = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
for lamb in lambList:
  print "[lamb = ", lamb, "]:"
  alpha = 0
  userBeta = defaultdict(float)
  itemBeta = defaultdict(float)

  objective = None

  while (True):
    #update alpha
    alpha = 0
    for user, item, rating in ratings:
      alpha += (float(rating) - (userBeta[user] + itemBeta[item])) / nTrain
    #update user terms
    userBeta = defaultdict(float)
    for user, item, rating in ratings:
      userBeta[user] += (float(rating) - (alpha + itemBeta[item])) / (lamb + nUser[user])
    #update item terms
    itemBeta = defaultdict(float)
    for user, item, rating in ratings:
      itemBeta[item] += (float(rating) - (alpha + userBeta[user])) / (lamb + nItem[item])
    oldObjective = objective
    objective = 0
    for user, item, rating in ratings:
      objective += (float(rating) - (alpha + userBeta[user] + itemBeta[item]))**2
    for u in userBeta:
      objective += lamb * userBeta[u]**2
    for i in itemBeta:
      objective += lamb * itemBeta[i]**2 
  #  print objective
    if (oldObjective and oldObjective - objective < 0.000001*objective):
      break
  print "finishing latent factor model..."
  print "writing to file..."

  for user, item, rating in ratings:
    predictVal = alpha + userBeta[user] + itemBeta[item]  
    MSE += (float(rating) - predictVal)**2

  print "\t\tMSE of training data is ", MSE / len(ratings)

  lengthOfTestData = 168459
  predictVal = 0
  MSE = 0
  baselineMAE = 0
  for l in open("rating_dataset.txt"):
    if l.startswith("review/userId"):
      continue
    else:
      u,i,rating = l.strip().split('-')
      predictVal = alpha + userBeta[u] + itemBeta[i]
      MSE += (float(rating) - predictVal)**2
  MSE /= lengthOfTestData
  print "                     MSE of validation data = ", MSE
  print "===================================================================================="


















































lengthOfTestData = 168459
predictVal = 0
MAE = 0
baselineMAE = 0
predictions = open("predictions_Rating.txt", 'w')
for l in open("rating_dataset.txt"):
  if l.startswith("review/userId"):
    predictions.write(l)
    continue

  u,i,rating = l.strip().split('-')
  if u in userAverage:
    baselinePrediction = userAverage[u]
  else:
    baselinePrediction = globalAverage

  predictVal = alpha + userBeta[u] + itemBeta[i]
  baselineMAE += abs(float(rating) - baselinePrediction)
  MAE += abs(float(rating) - predictVal)
  predictions.write(u + '-' + i + '-' + rating + ', ' + str(predictVal) + ', ' + str(baselinePrediction) + '\n')
  #print "=======================================\n"
MAE /= lengthOfTestData
baselineMAE /= lengthOfTestData
print "MAE = ", MAE
predictions.write("MAE = " + str(MAE))
print "baselineMAE = ", baselineMAE
predictions.write("baselineMAE = " + str(baselineMAE))
predictions.close()
print "Done..."
