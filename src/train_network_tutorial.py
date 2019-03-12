import numpy as np
import keras
import itertools
import matplotlib.pyplot as plt
from keras import backend as K
from keras.models import Sequential
from keras.layers import Activation
from keras.layers.core import Dense
from keras.optimizers import Adam
from keras.metrics import categorical_crossentropy
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import confusion_matrix

import random as gen

def plot_confusion_matrix(cm, classes, normalize=False, title='Confusion Matrix', cmap=plt.cm.Blues):
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print("Confusion matrix w/o normalization")

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j], horizontalalignment="center", color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True')
    plt.xlabel('Predicted')
    plt.show()


train_labels = []
train_data = []

for x in range(0, 2100):
    train_data.append(gen.randint(13,100))

for d in train_data:
    if d < 65:
        if gen.random() > 0.95:
            train_labels.append(1)
        else:
            train_labels.append(0)
    else:
        if gen.random() <= 0.95:
            train_labels.append(1)
        else:
            train_labels.append(0)

train_labels = np.array(train_labels)
train_data = np.array(train_data)

scaler = MinMaxScaler(feature_range=(0,1))
scaled_train_data = scaler.fit_transform((train_data).reshape(-1,1))

model = Sequential([
    Dense(16, input_shape=(1,), activation='relu'), # layers, input data shape, activation
    Dense(32, activation='relu'), # layers, activation
    Dense(2, activation='softmax') # output size
])

model.summary()
model.compile(Adam(lr=.0001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(scaled_train_data, train_labels, validation_split=0.1, batch_size=10, epochs=20, shuffle=True, verbose=2)

predictions = model.predict(scaled_train_data, batch_size=5, verbose=0)
rounded_predictions = model.predict_classes(scaled_train_data, batch_size=5, verbose=0)

cm = confusion_matrix(train_labels, rounded_predictions)
cm_plot_labels = ['no_side_effect', 'side_effect']
plot_confusion_matrix(cm, cm_plot_labels, title='Confusion Matrix')
