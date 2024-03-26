#!/usr/bin/env python
# coding: utf-8

# import packages
# Note: You cannot import any other packages!
import numpy as np
import matplotlib.pyplot as plt
import csv
import math
import random



# Global attributes
# Do not change anything here except TODO 1 
StudentID = '108062203' # TODO 1 : Fill your student ID here
input_dataroot = 'drive/MyDrive/input.csv' # Please name your input csv file as 'input.csv'
output_dataroot = StudentID + '_basic_prediction.csv' # Output file will be named as '[StudentID]_basic_prediction.csv'

input_datalist =  [] # Initial datalist, saved as numpy array
output_datalist =  [] # Your prediction, should be 20 * 2 matrix and saved as numpy array
                      # The format of each row should be [Date, TSMC_Price_Prediction] 
                      # e.g. ['2021/10/15', 512]

# You can add your own global attributes here
m = []
# Read input csv to datalist
with open(input_dataroot, newline='') as csvfile:
    input_datalist = np.array(list(csv.reader(csvfile)))

# From TODO 2 to TODO 6, you can declare your own input parameters, local attributes and return parameters
train_datalist = []
validation_datalist = []
test_datalist = []
def SplitData():
# TODO 2: Split data, 2021/10/15 ~ 2021/11/11 for testing data, and the other for training data and validation data
  global train_datalist,test_datalist,test,validation_datalist
  train_datalist = input_datalist[0:160,1:3]
  validation_datalist = input_datalist[160:189,1:3]
  test = input_datalist[189:209,1:2]
  test_datalist = np.zeros(20)
  for j in range(20):
   test_datalist[j] = int(test[j]) 

def PreprocessData():
# TODO 3: Preprocess your data  e.g. split datalist to x_datalist and y_datalist
    global x_datalist,y_datalist
    x_datalist = np.zeros(160)
    y_datalist = np.zeros(160)
    for i in range(160):
      x_datalist[i] = int(train_datalist[i,0])
      y_datalist[i] = int(train_datalist[i,1])

def Regression():
# TODO 4: Implement regression
  global m
  global c
  m = 0
  c = 0
  L = 0.0000005
  n = 160
  for i in range(100):
    Y_pred = m*x_datalist + c
    D_m = (-2/n)*sum(x_datalist*(y_datalist - Y_pred))
    D_c = (-2/n)*sum(y_datalist - Y_pred)
    m = m - L*D_m
    c = c - L*D_c
def CountLoss():
# TODO 5: Count loss of training and validation data
  vx = np.zeros(29)
  loss = 0
  for i in range(29):
      vx[i] = int(validation_datalist[i,0])
  Vali = m*vx + c
  for j in range(29):
    loss += abs(Vali[j]-int(validation_datalist[j,1]))/int(validation_datalist[j,1])
  loss /=29
  print(loss*100)
def MakePrediction():
  global output_datalist
  Y_pred = m*test_datalist+c
  out = np.ndarray([20,2],dtype=object)
  for i in range(20):
      out[i][0] = input_datalist[i+189][0]
      out[i][1] = int(Y_pred[i])
  output_datalist = out

SplitData()
PreprocessData()
Regression()
MakePrediction()
CountLoss()
# Write prediction to output csv
with open(output_dataroot, 'w', newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    for row in output_datalist:
        writer.writerow(row)
