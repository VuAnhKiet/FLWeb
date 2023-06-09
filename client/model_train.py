
import numpy as np
import tensorflow as tf
from tensorflow import keras

from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam
from keras.metrics import categorical_crossentropy
from keras.preprocessing.image import ImageDataGenerator
from keras.preprocessing import image
from keras.models import Model
import time 
from keras.applications import imagenet_utils
from sklearn.metrics import confusion_matrix
import itertools
import os
import shutil
import random
import pickle

def train():
	cwd = os.getcwd()
	if os.path.isdir(cwd + '/local_model') == False:
		os.mkdir(cwd + '/local_model')
	object_name = "object_name"
	main_path = './UploadFolder/image_dataset_path'
	train_path = main_path+'/train/'
	valid_path = main_path+'/valid/'
	test_path = main_path+'/test/'

	train_batches = ImageDataGenerator(preprocessing_function=tf.keras.applications.mobilenet.preprocess_input).flow_from_directory(
		directory=train_path, target_size=(224,224), batch_size=10)
	valid_batches = ImageDataGenerator(preprocessing_function=tf.keras.applications.mobilenet.preprocess_input).flow_from_directory(
		directory=valid_path, target_size=(224,224), batch_size=10)
	test_batches = ImageDataGenerator(preprocessing_function=tf.keras.applications.mobilenet.preprocess_input).flow_from_directory(
		directory=test_path, target_size=(224,224), batch_size=10, shuffle=False)
	start = time.time()
	mobile = tf.keras.applications.mobilenet.MobileNet()
	x = mobile.layers[-6].output
	x = Flatten()(x)

	output = Dense(units=2, activation='softmax')(x)
	model = Model(inputs=mobile.input, outputs=output)

	for layer in model.layers[:-5]:
		layer.trainable = False

	model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

	history = model.fit(train_batches,
			  steps_per_epoch=len(train_batches),
			  validation_data=valid_batches,
			  validation_steps=len(valid_batches),
			  epochs=10,
			  verbose=1,use_multiprocessing = False
	)
	model.save(cwd + "/local_model/model1.h5")
	x = history.history
	end = time.time() - start
	return (x,object_name)

