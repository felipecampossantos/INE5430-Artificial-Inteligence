# ndarrys for gridded data
from re import T
import numpy as np
# DataFrames for tabular data
import pandas as pd
import matplotlib.pyplot as plt  # for plotting
import matplotlib.image as mpimg
import seaborn as sns
import h5py as h5


from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

import tensorflow as tf              # Importa TF2
from tensorflow import keras         # Importa Keras
# Ferramentes do Keras mais usadas para acesso mais rápido
from tensorflow.keras import layers
from keras.layers import Dense
from keras.models import Sequential
from tensorflow.keras.utils import to_categorical

from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import accuracy_score

## for callback
def exp_decay(epoch):
   initial_lrate = 1.0
   k = 0.05
   lrate = initial_lrate * np.exp(-k*epoch)
   return lrate


## CONFIGURATION VALUES

# _SHOW_GRAPHS = False
_SHOW_GRAPHS = True
# _SHOW_FITTING_OUTPUT = 1 # TRUE
_SHOW_FITTING_OUTPUT = 0 # 0=FALSE 1=TRUE
_SHOW_EXAMPLES = False
_NUMBER_EXAMPLES_SHOWN_TRAINING_SET = 10
_PRINT_MODEL_SUMMARY = False

_HIDDEN_LAYER_NEURONS_NUMBER = 400
_OUTPUT_LAYER_NEURONS_NUMBER = 2 # binary, must be two

_ADD_LEARNING_RATE_CALLBACK = False
_ADD_EARLY_STOP_CALLBACK = False

_SIGMOID = "sigmoid"
# _SOFTMAX="softmax"
_RANDOM_UNIFORM = "random_uniform"
_TANH = "tanh"
_LEARNING_RATE = 0.03
_TEST_SIZE = 0.3
_EPOCHS = 300
_BATCH_SIZE = 400 #64

## import datasets
trainining_ds = h5.File('../datasets/train_catvnoncat.h5', "r")
testing_ds = h5.File('../datasets/test_catvnoncat.h5', "r")

# creating data for training and testing
Xtrain = np.array(
    trainining_ds["train_set_x"][:])  # train set features
Ytrain = np.array(
    trainining_ds["train_set_y"][:])  # train set labels

Xtest = np.array(
    testing_ds["test_set_x"][:])  # test set features
Ytest = np.array(testing_ds["test_set_y"][:])  # test set labels

# Normalizing values
Xtrain = Xtrain/255.0
Xtest = Xtest/255.0

# Printing examples
if(_SHOW_EXAMPLES):
    print('Showing examples of training set:')
    plt.figure(figsize=(15, 15))
    for i in range(_NUMBER_EXAMPLES_SHOWN_TRAINING_SET):
        ax = plt.subplot(4, 5, i + 1)
        plt.imshow(Xtrain[i+10])
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

    plt.show()

# one-hot-encoding of the output variable
num_classes = 2  # cat or not-cat
ytrain = to_categorical(Ytrain, num_classes)
ytest = to_categorical(Ytest, num_classes)


model = tf.keras.Sequential()
model.add(layers.Flatten())
model.add(layers.Dense(_HIDDEN_LAYER_NEURONS_NUMBER, kernel_initializer=_RANDOM_UNIFORM,
          bias_initializer=_RANDOM_UNIFORM, activation=_TANH))

# activation function for output is chosen as sigmoid because it is an binary classification
model.add(layers.Dense(_OUTPUT_LAYER_NEURONS_NUMBER, kernel_initializer=_RANDOM_UNIFORM,
          bias_initializer=_RANDOM_UNIFORM, activation=_SIGMOID))

# training method defined as SGD (Stochastic Gradient Descent)
opt = tf.keras.optimizers.SGD(learning_rate=_LEARNING_RATE)
model.compile(optimizer=opt, loss="categorical_crossentropy",
              metrics=["accuracy"])

input_shape = Xtrain.shape
model.build(input_shape)

if(_PRINT_MODEL_SUMMARY):
  model.summary()


# To evaluate if our neural network is being well trained, we can choose a subset of
# the training data to validate the model.
Xtr, Xval, ytr, yval = train_test_split(Xtrain, ytrain, test_size=_TEST_SIZE)
num_train = np.size(Xtr, 0)
print('\nNumber of training data: {}'.format(num_train))


# TRAINING THE MODEL
# Now that we have defined a dataset for the network training, and a dataset
# for validation, we can train the model using fit
# Two important parameters are batch_size and epoch (number of iterations)

# CALLBACKS
# This callback will stop the training when the loss reachs a minimum for validation data 
# for fifty consecutive epochs.


callbacks_list = []

if(_ADD_EARLY_STOP_CALLBACK):
  early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                              mode="min",
                              patience=50,
                              verbose=0)

  callbacks_list.append(early_stopping)

if(_ADD_LEARNING_RATE_CALLBACK):
  lrate = tf.keras.callbacks.LearningRateScheduler(exp_decay)
  callbacks_list.append(lrate)

if(_ADD_EARLY_STOP_CALLBACK or _ADD_LEARNING_RATE_CALLBACK):
  results = model.fit(Xtr, ytr, validation_data=(
    Xval, yval), batch_size=_BATCH_SIZE, epochs=_EPOCHS, callbacks=callbacks_list, verbose=_SHOW_FITTING_OUTPUT)
else: 
  results = model.fit(Xtr, ytr, validation_data=(
    Xval, yval), batch_size=_BATCH_SIZE, epochs=_EPOCHS, verbose=_SHOW_FITTING_OUTPUT)


if(_SHOW_GRAPHS):
    # outputing in graphs the performance results
    accuracy = results.history['accuracy']
    accuracy_value = results.history['val_accuracy']
    loss = results.history['loss']
    loss_value = results.history['val_loss']
    epochs = range(1, len(accuracy) + 1)

    plt.figure()
    plt.plot(epochs, accuracy, 'b', label='Training accuracy')
    plt.plot(epochs, accuracy_value, 'r', label='Validation accuracy')
    plt.title('Training and Validation accuracy')
    plt.legend()

    plt.figure()
    plt.plot(epochs, loss, 'b', label='Training loss')
    plt.plot(epochs, loss_value, 'r', label='Validation loss')
    plt.title('Training and Validation loss')
    plt.legend()


# If the performance of the network is not good enough, this may indicate that the network
# is too simple to model the data. To overcome this, we can try improving the number of
# neurons in the hidden layer (_HIDDEN_LAYER_NEURONS_NUMBER) or even adding more hidden layers.

# Checking the network performance for the test dataset
ytestpred = model.predict(Xtest)
print('\nAccuracy: {:.4f}\n'.format(accuracy_score(
    ytest.argmax(axis=1), ytestpred.argmax(axis=1))))

# if(_SHOW_GRAPHS):
    # Your input to confusion_matrix must be an array of int not one hot encodings.
ConfusionMatrixDisplay.from_predictions(
        ytest.argmax(axis=1), ytestpred.argmax(axis=1))

if(_SHOW_GRAPHS):
    plt.show()
