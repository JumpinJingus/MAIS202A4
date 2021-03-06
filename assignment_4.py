# -*- coding: utf-8 -*-
"""Assignment 4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10WCt-a0oyozhT5DE2UbbLJ9lv2K3TRcE

## Assignment 4 - Andy Lee & Monami Waki

# Imports
"""

# Import modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import keras
import os
import io
import cv2
from PIL import Image, ImageEnhance
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, ReLU
from keras.layers import Conv2D, MaxPooling2D, AveragePooling2D
from keras.layers.normalization import BatchNormalization
from keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split
from google.colab import files
from skimage import data
from skimage import filters
import skimage.color 
import matplotlib.image as mpimg
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior() 
from math import ceil, floor

"""# Download Data"""

# Install Kaggle
!pip install -q kaggle

# Upload .json
json_upload = files.upload()

# Create directory
!mkdir ../root/.kaggle
!cp ../content/kaggle.json ../root/.kaggle

# Download Dataset
!kaggle competitions download -c mais-202-fall-2020-kaggle-competition

"""# Unzip Data"""

# Unzip .npy.zip files
!unzip test_x.npy.zip
!unzip train_x.npy.zip

"""# Data Preprocessing

"""

# Load Data
train_x_raw = np.load("train_x.npy")
train_y_raw = pd.read_csv("train_y.csv")
test_x = np.load("test_x.npy")

# Demo Function
def show_image(arr):
    two_d = (np.reshape(arr, (128, 128)) * 255).astype(np.uint8)
    plt.imshow(two_d, interpolation='nearest', cmap='gray')
    plt.show()

# Check shapes of images
# Should be 40000 128x128 images
# First coordinate is image
# Second coordinate is x_coord
# Third coordinate is y_coord
print("Size of train_x_raw:")
print(train_x_raw.shape)
print()

# Isolate Label from Train_y
train_y_nparray = np.array(train_y_raw)[:,1]
train_y_labels = to_categorical(train_y_nparray)

# Apply Threshold Function
result, train_x_raw = cv2.threshold(train_x_raw,240,255, cv2.THRESH_BINARY)
result, test_x = cv2.threshold(test_x,240,255, cv2.THRESH_BINARY)

# Split Training Data to Training and Validation Sets (75:25)
train_x, val_x, train_y, val_y = train_test_split(train_x_raw, train_y_labels, test_size=0.25)

# Convert data type and normalize
train_x = train_x.astype('float32')
val_x = val_x.astype('float32')
test_x = test_x.astype('float32')
train_x /= 255
val_x /= 255
test_x /= 255

# Check set sizes
print("Size of train_x:")
print(train_x.shape)
print()
print("Size of val_x:")
print(val_x.shape)
print()
print("Size of train_y:")
print(train_y.shape)
print()
print("Size of val_y:")
print(val_y.shape)
print()
print("Size of test_x:")
print(test_x.shape)
print()

# Show first 5 images
show_image(train_x[0])
show_image(train_x[1])
show_image(train_x[2])
show_image(train_x[3])
show_image(train_x[4])

"""# Creation of CNN Model"""

# Declare Sequential Model
model = Sequential()

# 5 Conv2D Layers each with ReLU, MaxPooling2D, and Dropout Layers added
model.add(Conv2D(16, kernel_size = (3,3), input_shape = (128,128,1), activation='relu'))
model.add(MaxPooling2D(pool_size=2))

model.add(Conv2D(32, kernel_size = (3,3), activation='relu'))
model.add(MaxPooling2D(pool_size=2))
model.add(Dropout(0.25))

model.add(Conv2D(64, kernel_size = (3,3), activation='relu'))
model.add(MaxPooling2D(pool_size=2))
model.add(Dropout(0.25))

model.add(Conv2D(128, kernel_size = (3,3), activation='relu'))
model.add(MaxPooling2D(pool_size=2))
model.add(Dropout(0.25))

model.add(Conv2D(256, kernel_size = (3,3), activation='relu'))
model.add(MaxPooling2D(pool_size=2))
model.add(Dropout(0.25))

# Flatten and Dense at the end
model.add(Flatten())
model.add(Dense(120, activation = 'relu'))
model.add(Dropout(0.3))
model.add(Dense(84, activation = 'relu'))
model.add(Dropout(0.3))
model.add(Dense(10, activation = 'softmax'))

# Compile model with Adam
model.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])

# Show Summary
model.summary()

"""# Training of CNN Model"""

################################################################
# Dataset Arrays to Use for the Model:                         #
# train_x, val_x, train_y, val_y for training and validation   #
# test_x for testing                                           #
################################################################

# Hyperparameters
batch_size = 128
epochs = 10

# Reshape train_x, val_x, and test_x
train_x = train_x.reshape(30000, 128, 128,1)
val_x = val_x.reshape(10000, 128, 128, 1)
test_x = test_x.reshape(10000, 128, 128, 1)

# Verify Shapes of train, val, test sets
# Should be (30000x128x128x1)
print("Shape for train_x:")
print(train_x.shape, "\n")

# Should be (10000x128x128x1)
print("Shape for val_x:")
print(val_x.shape, "\n")

# Should be (10000x128x128x1)
print("Shape for test_x:")
print(test_x.shape, "\n")

# Train the model
model.fit(train_x, train_y, validation_data = (val_x, val_y), epochs = epochs, batch_size=batch_size)

"""# Testing of CNN Model"""

# Predict on Test set
test_y = model.predict(test_x)

# Find the largest probabilities of the result
test_y_max_probs = np.amax(test_y, axis=1, keepdims=True)# finding max probabilities

# Generate ID (0 to 10000)
y_ID = np.arange(10000)

# Generate Labels
test_y_labels = np.zeros(len(test_y))

# Assign Labels
for i,x in np.ndenumerate(test_y_max_probs):
  test_y_labels[i[0]] = np.where(test_y[i[0]] == x)[0]
test_y_labels = test_y_labels.astype('int')

print(test_y_labels)

# Create Dataframe for CSV
submission_csv = pd.DataFrame()

# Add ID and Label columns to CSV
submission_csv['ID'] = y_ID
submission_csv['label'] = test_y_labels
submission_csv.to_csv('submission.csv', index=False)
print(submission_csv)

"""# Submission of Results"""

Submit results
!kaggle competitions submit -c mais-202-fall-2020-kaggle-competition -f submission.csv -m "test"