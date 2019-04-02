"""
Author: Zachary Shaffer

This program creates and trains a Keras model on the MNIST hand-drawn digits
dataset. The model created by this program will be used as the model for
Caster while in development, prior to proper data acquisition.

Honor Code; This work is mine unless otherwise cited. I have used several
Keras tutorials to attempt to isolate the best values used for the layers.
Most tutorials were found on either GitHub repositories or various blogs.
"""

# Import relevant modules
# numpy is used to convert image data into matrices
import numpy

# mnist is the public-use data set of hand-drawn digits
from keras.datasets import mnist

# A sequential CNN model will be used
from keras.models import Sequential

# Dense, Dropout, and Flatten layers needed as hidden layers in CNN
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Flatten

# 2D Convolution and 2D Pooling layers needed
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D

# Adam is the most popular optimizer for this task
from keras.optimizers import Adam

# Keras has a utility module for working with numpy arrays/matrices
from keras.utils import np_utils

# Import time to record the time it takes to run the training from beginning to
# end.
import time

# Import os to disable Tensorflow warnings
import os

# Import TensorFlow to disable its warnings
import tensorflow as tf

# Filter out "INFO" and "WARNING" logs in TensorFlow to clean up output
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
tf.logging.set_verbosity(tf.logging.ERROR)

# Record starting time
start_time = time.time()

# Load data from mnist. Images are 28x28. Of the 70,000 pieces of data,
# 10,000 will be used to test and the rest will be used to train the model
# X_train and X_test are specific to mnist, and have the shapes
# (60000, 28, 28) and (10000, 28, 28) respectively.
(X_train, y_train), (X_test, y_test) = mnist.load_data()

# X_train and X_test are the inputs. They must have the shape of a 4D array as
# (batchsize, height, width, channels). Channels tells Keras whether or not
#  the image is black and white (1 channel, either black or white) or colorful
# (3 channels, Red Green and Blue). The astype function converts the data
# to float values that can have division performed on them for normalization.
X_train = X_train.reshape(
    X_train.shape[0], X_train.shape[1], X_train.shape[2], 1
).astype("float32")
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[2], 1).astype(
    "float32"
)

# The value of each pixel may not be exactly black or exactly white. A value of
# 0.0-255.0 will represent the color value. We will normalize this value to a
# range between 0 and 1.
X_train = X_train / 255
X_test = X_test / 255

# We now have a number of classifications for the model, and we use
# to_categorical() to make sure that the format for each output is a list
# of 0's with a single 1, where 1 is in the indext of the associated drawn
# digit. E.g., 7 would be [0, 0, 0, 0, 0, 0, 0, 1, 0, 0]. When making
# predictions later, the output will be a list of values from 0-1 indicating
# the probability for that index to be the drawn digit that was given as input.
classifications = 10
y_train = np_utils.to_categorical(y_train, classifications)
y_test = np_utils.to_categorical(y_test, classifications)

# Initialize the model
model = Sequential()
# The first layer is our first convolutional layer. 32 filters, 5x5 filter size,
# input shape given as (height, width, channels), and ReLU activation. ReLU
# activation normalizes unwanted data types (such as negative values) to a
# standard (such as 0s).
model.add(
    Conv2D(
        32,
        (5, 5),
        input_shape=(X_train.shape[1], X_train.shape[2], 1),
        activation="relu",
    )
)
# Pooling layer, wherein the model takes each concurrent 2x2 area of the matrix
# and saves the highest value into a corresponding element of a smaller sized
# matrix, reducing overall runtime.
model.add(MaxPooling2D(pool_size=(2, 2)))
# Convolution and pooling performed again.
model.add(Conv2D(32, (3, 3), activation="relu"))
model.add(MaxPooling2D(pool_size=(2, 2)))
# Dropout layer randomly removes a percentage of the nodes in the network
# to reduce over-fitting to the training set. This value can be increased or
# reduced, depending on whether or not you have an overfitting problem (likely
# from a lack of data, if using non-mnist data)
model.add(Dropout(0.2))
# Flatten 2D matrix into a 2D vector
model.add(Flatten())
# Condense data into a 128 long vector, removing unwanted values with relu
model.add(Dense(128, activation="relu"))
# Condense data into desired output size, using softmax to give us values 0-1
# that represent probabilities for which classification we have
model.add(Dense(classifications, activation="softmax"))

# Compile the layers of the model. Loss is categorical_crossentropy because we
# have multiple classifications. Adam is a popular optimizer for Keras in many
# of these problems. Accuracy is the overall goal of, and thus the metric for,
# our neural network model.
model.compile(loss="categorical_crossentropy", optimizer=Adam(), metrics=["accuracy"])

# Now we fit our model to our training data. We use the test values to validate
# the model as it learns. Epochs is the number of front to back passes of the
# data, in this case 10. The batch size is the number of images used, in this
# case 128 images used to train in each epoch. Silence the output with verbose=0
# to keep output clean and legible
model.fit(
    X_train,
    y_train,
    validation_data=(X_test, y_test),
    epochs=10,
    batch_size=128,
    verbose=0,
)

# Evaluate the model performance with remaining test data. Verbosity set to 0
# for ease of data recording. Timing of the program is done independently of
# Keras, so progress and ETA is not necessary output
eval_results = model.evaluate(X_test, y_test)

# Record ending time
end_time = time.time()

# Display output in terms of percent loss and percent accuracy.
print("Loss: " + str(eval_results[0] * 100) + "%.")
print("Accuracy: " + str(eval_results[1] * 100) + "%.")

# Display total runtime in seconds.
print("Total runtime: " + str(end_time - start_time) + " seconds.")

# Save the model we have trained.
model.save("src/static/file/mnistModel.h5")
