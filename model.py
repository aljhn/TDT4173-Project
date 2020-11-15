import random
import numpy as np
import pickle
import matplotlib.pyplot as plt

from tensorflow.random import set_seed
random.seed(0)
np.random.seed(0)
set_seed(0)

from tensorflow.keras import Sequential
from tensorflow.keras.layers import LSTM, GRU, Bidirectional, Attention, Concatenate
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Embedding
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.utils import class_weight, shuffle
from sklearn.metrics import classification_report
#import tensorflowjs as tfjs

import tensorflow.compat.v1 as tf

tf.disable_v2_behavior()  #disable for tensorFlow V2
physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)


max_comment_length = 100
word_amount = 10000
embedding_dim = 128
lstm_dim = 192
learning_rate = 0.001

reddit_file0 = open("formated_data/reddit0.pickle", "rb")
reddit_data0 = pickle.load(reddit_file0)
reddit_file0.close()
reddit_file1 = open("formated_data/reddit1.pickle", "rb")
reddit_data1 = pickle.load(reddit_file1)
reddit_file1.close()
reddit_file2 = open("formated_data/reddit2.pickle", "rb")
reddit_data2 = pickle.load(reddit_file2)
reddit_file2.close()
reddit_file3 = open("formated_data/reddit3.pickle", "rb")
reddit_data3 = pickle.load(reddit_file3)
reddit_file3.close()

reddit_data = reddit_data0 + reddit_data1 + reddit_data2 + reddit_data3 # Combine lists

hackernews_file = open("formated_data/hacker_news.pickle", "rb")
hackernews_data = pickle.load(hackernews_file)
hackernews_file.close()

youtube_file = open("formated_data/youtube.pickle", "rb")
youtube_data = pickle.load(youtube_file)
youtube_file.close()

reddit_samples = len(reddit_data)
hackernews_samples = len(hackernews_data)
youtube_samples = len(youtube_data)
samples = reddit_samples + hackernews_samples + youtube_samples

"""
reddit_data = np.load("reddit.npy")
hackernews_data = np.load("hacker_news_test.npy")
youtube_data = np.load("youtube_test.npy")

reddit_samples = reddit_data.shape[0]
hackernews_samples = hackernews_data.shape[0]
youtube_samples = youtube_data.shape[0]
samples = reddit_samples + hackernews_samples + youtube_samples
"""

reddit_labels = [0 for i in range(reddit_samples)]
hackernews_labels = [1 for i in range(hackernews_samples)]
youtube_labels = [2 for i in range(youtube_samples)]

data = reddit_data + hackernews_data + youtube_data
#data = np.concatenate((reddit_data, hackernews_data, youtube_data), axis=0)
labels = reddit_labels + hackernews_labels + youtube_labels
data, labels = shuffle(data, labels, random_state=0)

x_train = data[0 : samples * 70 // 100]
x_val = data[samples * 70  // 100 : samples * 85 // 100]
x_test = data[samples * 85 // 100 : samples]

y_train = labels[0 : samples * 70 // 100]
y_val = labels[samples * 70  // 100 : samples * 85 // 100]
y_test = labels[samples * 85 // 100 : samples]

class_weights = class_weight.compute_class_weight("balanced", classes=[0, 1, 2], y=y_train)
class_weights = dict(enumerate(class_weights))

tokenizer = Tokenizer(num_words=word_amount, oov_token=1)
tokenizer.fit_on_texts(x_train)

#f = open("tokenizer.txt", "w")
#f.write(str(tokenizer.word_index))
#f.close()

x_train = tokenizer.texts_to_sequences(x_train)
x_val = tokenizer.texts_to_sequences(x_val)
x_test = tokenizer.texts_to_sequences(x_test)

x_train = pad_sequences(x_train, maxlen=max_comment_length)
x_val = pad_sequences(x_val, maxlen=max_comment_length)
x_test = pad_sequences(x_test, maxlen=max_comment_length)

y_train = np.array(list(map(lambda x: [int(i == x) for i in range(3)], y_train)))
y_val = np.array(list(map(lambda x: [int(i == x) for i in range(3)], y_val)))
y_test = np.array(list(map(lambda x: [int(i == x) for i in range(3)], y_test)))

models = []

# Logistic regression
model = Sequential()
#model.add(Embedding(word_amount, embedding_dim, input_length=max_comment_length))
model.add(Dense(3, activation="softmax"))
#models.append(model)

# LSTM
model = Sequential()
model.add(Embedding(word_amount, embedding_dim, input_length=max_comment_length))
model.add(LSTM(lstm_dim))
model.add(Dense(3, activation="softmax"))
#models.append(model)

# Bidirectional LSTM
model = Sequential()
model.add(Embedding(word_amount, embedding_dim, input_length=max_comment_length))
model.add(Bidirectional(LSTM(lstm_dim)))
model.add(Dense(3, activation="softmax"))
models.append(model)

# GRU
model = Sequential()
model.add(Embedding(word_amount, embedding_dim, input_length=max_comment_length))
model.add(GRU(lstm_dim))
model.add(Dense(3, activation="softmax"))
#models.append(model)

# Bidirectional GRU
model = Sequential()
model.add(Embedding(word_amount, embedding_dim, input_length=max_comment_length))
model.add(Bidirectional(GRU(lstm_dim)))
model.add(Dense(3, activation="softmax"))
#models.append(model)

for i in range(len(models)):
	model = models[i]
	model.compile(loss="categorical_crossentropy", optimizer=Adam(learning_rate=learning_rate), metrics=["accuracy"])
	epochs=10
	history = model.fit(x_train, y_train, validation_data=(x_val, y_val), class_weight=class_weights, epochs=epochs, batch_size=128, verbose=1)

	axis = [i + 1 for i in range(epochs)]
	plt.figure(0)
	plt.plot(axis, history.history["acc"])
	plt.plot(axis, history.history["val_acc"])
	plt.ylim(0, 1)
	plt.xticks(axis, axis)
	plt.title("Model Accuracy")
	plt.ylabel("Accuracy")
	plt.xlabel("Epoch")
	plt.legend(["Train", "Validation"], loc="upper left")
	plt.savefig("model_acc")

	plt.figure(1)
	plt.plot(axis, history.history["loss"])
	plt.plot(axis, history.history["val_loss"])
	plt.ylim(0, max(history.history["loss"] + history.history["val_loss"]) + 0.3)
	plt.xticks(axis, axis)
	plt.title("Model loss")
	plt.ylabel("Loss")
	plt.xlabel("Epoch")
	plt.legend(["Train", "Validation"], loc="upper left")
	plt.savefig("model_loss")

	model.save("model.hdf5")
	#tfjs.converters.save_keras_model(model, "model")

	f = open("model.txt", "w")

	#loss, accuracy = model.evaluate(x_val, y_val, verbose=1)
	#f.write("Validation: [loss: " + str(loss) + ", accuracy: " + str(accuracy) + "]\n")
	#y_val_pred = model.predict(x_val)
	#f.write(classification_report(np.argmax(y_val, axis=1), np.argmax(y_val_pred, axis=1), target_names=["Reddit", "Hacker News", "YouTube"]))

	loss, accuracy = model.evaluate(x_test, y_test, verbose=1)
	f.write("Test: [loss: " + str(loss) + ", accuracy: " + str(accuracy) + "]\n")
	y_test_pred = model.predict(x_test)
	f.write(classification_report(np.argmax(y_test, axis=1), np.argmax(y_test_pred, axis=1), target_names=["Reddit", "Hacker News", "YouTube"]))

	f.close()