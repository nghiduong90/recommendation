import gzip
import re
from collections import defaultdict
import itertools
import numpy
from sklearn import linear_model 

def readGz(f):
  for l in gzip.open(f):
    yield eval(l)

DataSetSize = 1000000
trainData = []
validateData = []
dataCount = 0
sumOfRatio = 0.0
ratio = 0.0
countNotZero = 0
reviewDict = {}

for l in readGz('train.json.gz'):
  if dataCount < DataSetSize:
  	if l['helpful']['outOf'] == 0:
  		l['helpful']['ratio'] = 0
  	else:
  		ratio = l['helpful']['nHelpful'] * 1.0 / l['helpful']['outOf']
  		l['helpful']['ratio'] = ratio
  		sumOfRatio += ratio
  		countNotZero += 1
  	trainData.append(l)

  if dataCount > 900000:
  	if l['helpful']['outOf'] == 0:
  		l['helpful']['ratio'] = 0
  	else:
  		l['helpful']['ratio'] = l['helpful']['nHelpful'] * 1.0 / l['helpful']['outOf']
  		validateData.append(l)

  dataCount += 1

alpha = sumOfRatio / countNotZero
print "alpha = ", alpha

MAE = 0.0
for data in validateData:
	MAE += abs(data['helpful']['ratio'] - alpha)
MAE /= len(validateData)

print "MAE = ", MAE

feature = []
ratio = []

for data in trainData:
	feature.append([1, len(data['reviewText'].split()), data['rating']])
	ratio.append(data['helpful']['ratio'])

clf = linear_model.Ridge(1.0, fit_intercept=False)
clf.fit(feature, ratio)
theta = clf.coef_


theta,residuals,rank,s = numpy.linalg.lstsq(feature,ratio)

print "set of theta = ", theta

MAE = 0.0
for data in validateData:
	wc = len(data['reviewText'].split())
	rating = data['rating']
	predictVal = theta[0] + theta[1] * wc + theta[2] * rating
	MAE += abs(data['helpful']['ratio'] - predictVal)

MAE /= len(validateData)
print "MAE of new model = ", MAE


predictions = open("predictions_Helpful.txt", 'w')
predictions.write("userID-itemID-outOf,prediction")
for l in readGz('helpful.json.gz'):
	wc = len(l['reviewText'].split())
	rating = l['rating']
	'''
	if (l['helpful']['outOf'] == 0):
		predictVal = 0
	else:
		predictVal = theta[0] + theta[1] * wc + theta[2] * rating
	'''
	predictVal = clf.predict([1, len(l['reviewText'].split()), l['rating']])[0] * l['helpful']['outOf']
	predictions.write(l['reviewerID'] + '-' + l['itemID'] + '-' + str(l['helpful']['outOf']) +',' + str(predictVal) +'\n') 
    

predictions.close()