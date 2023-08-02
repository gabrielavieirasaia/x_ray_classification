# -*- coding: utf-8 -*-
"""Algoritmo para Classificação de Pneumonia Utilizando Radiografias de Tórax

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dGQiT5Ggol4LPgZMO3hrUqBs8SkSavBf
"""

!git clone https://github.com/thegiftofgabi/x_ray_classification.git

import os
import cv2
import tensorflow as tf
import numpy as np
from tensorflow.keras import layers,optimizers
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Input, Dense, AveragePooling2D, Dropout, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint
import matplotlib.pyplot as plt
import seaborn as sns

from google.colab import drive
drive.mount ('/content/drive')

xray_directory = '/content/drive/MyDrive/DATA SET/chest_xray/train'

os.listdir(xray_directory)

image_generator = ImageDataGenerator(rescale=1./255)

train_generator = image_generator.flow_from_directory(batch_size=40, directory=xray_directory, shuffle=True,
                                                      target_size=(256,256), class_mode='categorical', subset='training')

train_images, train_labels = next(train_generator)

train_images.shape

train_labels

#100 Normal
#010 Bateriana
#001 Viral
labels_names = {0: 'Normal', 1:'Bacteriana', 2: 'Viral' }

"""Visualização dos Dados"""

np.arange(0,36)

np.argmax(train_labels[1])

labels_names[1]

fig, axes = plt.subplots(4, 4, figsize=(12,12))
axes = axes.ravel()
for i in np.arange(0,16):
  axes [i].imshow(train_images[i])
  axes[i].set_title(labels_names[np.argmax(train_labels[i])])
  axes[i].axis('off')
  plt.subplots_adjust(wspace=0.5)

"""Carregamento da rede neural pré treinada"""

base_model = ResNet50(weights='imagenet', include_top=False,
                      input_tensor = Input(shape=(256,256,3)))

base_model.summary()

len(base_model.layers)

for layer in base_model.layers[:-10]:
  layers.trainable = False

"""Construção e treinamento da rede"""

head_model = base_model.output
head_model = AveragePooling2D()(head_model)
head_model = Flatten()(head_model)
head_model = Dense(256, activation='relu')(head_model)
head_model = Dropout(0.2)(head_model)
head_model = Dense(256, activation='relu')(head_model)
head_model = Dropout(0.2)(head_model)
head_model = Dense(3, activation='softmax')(head_model)

model = Model (inputs = base_model.input , outputs = head_model)

model.compile(loss = 'categorical_crossentropy',
              optimizer=optimizers.RMSprop(learning_rate =1e-4, decay=1e-6), metrics = ['accuracy'])

checkpointer = ModelCheckpoint(filepath='weights.hdf5')

train_generator = image_generator.flow_from_directory(batch_size= 4, directory=xray_directory, shuffle=True,
                                                      target_size=(256,256), class_mode='categorical', subset='training')

history = model.fit_generator(train_generator, epochs = 25, callbacks=[checkpointer])

"""Avaliação da rede"""

history.history.keys()

plt.plot(history.history['accuracy'])
plt.plot(history.history['loss'])
plt.title('Erro e taxa de acerto durante o treinamento')
plt.xlabel('Época')
plt.ylabel('Taxa de acerto e erro')
plt.legend(['Taxa de acerto','Erro']);

test_directory = '/content/drive/MyDrive/DATA SET/chest_xray/test'

os.listdir(test_directory)

test_gen = ImageDataGenerator(rescale=1./255)
test_generator = test_gen.flow_from_directory(batch_size = 40, directory = test_directory,
                                              shuffle = True, target_size = (256,256),
                                              class_mode = 'categorical')

evaluate = model.evaluate(test_generator)

evaluate

len(os.listdir(test_directory))

os.listdir(test_directory)

"""Matrix de Confusão"""

prediction = []
original = []
image = []

for i in range(len(os.listdir(test_directory))):
  for item in os.listdir(os.path.join(test_directory, str(i))):
    #print(os.listdir(os.path.join(test_directory, str(i))))
    img = cv2.imread(os.path.join(test_directory, str(i), item))
    img = cv2.resize(img, (256, 256))
    image.append(img)
    img = img / 255
    img = img.reshape(-1, 256, 256, 3)
    predict = model.predict(img)
    predict = np.argmax(predict)
    prediction.append(predict)
    original.append(i)

print(prediction)

print(original)

from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

accuracy_score(original, prediction)

fig, axes = plt.subplots(4, 4, figsize=(12,12))
axes = axes.ravel()
for i in np.arange(0, 16):
  axes[i].imshow(image[i])
  axes[i].set_title('Previsão={}\nValor Original={}'.format(str(labels_names[prediction[i]]), str(labels_names[original[i]])))
  axes[i].axis('off')
plt.subplots_adjust(wspace = 1.2)

labels_names

cm = confusion_matrix(original, prediction)
sns.heatmap(cm, annot=True)

print(classification_report(original, prediction))

"""Classificação de somente uma imagem"""

from keras.models import load_model
model_loaded = load_model('/content/weights.hdf5')

img = cv2.imread('/content/drive/MyDrive/DATA SET/chest_xray/test/1/person78_bacteria_386.jpeg')

img, img.shape

from google.colab.patches import cv2_imshow
cv2_imshow(img)

img = cv2.resize(img, (256,256))
cv2_imshow(img)

img = img / 255
img

img.shape

img = img.reshape(-1, 256, 256, 3)
img.shape

predict = model_loaded(img)
predict

predict = np.argmax(predict)
predict

labels_names[predict]