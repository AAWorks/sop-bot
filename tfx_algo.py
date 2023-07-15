import numpy as np
import tensorflow as tf
import tensorflow.keras as keras # pylance raises <Import "tensorflow.keras" could not be resolved> - Ignore
from sklearn import preprocessing


class DNNModel:
    def __init__(self, records):
        training_set_frac = 0.80

        features = list(records.columns)
        features.remove("result")

        train_len = int(training_set_frac * records.shape[0])
        train = records.head(train_len)
        test = records.tail(records.shape[0] - train_len)

        self._train = {
            'data': np.array(train[features]), 
            'labels': np.array(train["result"])
        }

        self._test = {
            'data': np.array(test[features]), 
            'labels': np.array(test["result"])
        }

        self._init_layer = records.shape[1] - 1

        self._model = tf.keras.Sequential()

        self._hist_obj = None
    
    def build(self):
        self._model.add(tf.keras.layers.Dense(units=self._init_layer, activation='relu', input_shape=[self._init_layer,]))
        self._model.add(tf.keras.layers.Dense(units=100, activation='relu'))
        self._model.add(tf.keras.layers.Dense(units=1000, activation='relu'))
        #self._model.add(tf.keras.layers.Dense(units=self._init_layer * 3, activation='relu'))
        self._model.add(tf.keras.layers.Dense(units=1, activation='softmax'))
        opt = tf.keras.optimizers.Adam(learning_rate=1e-7) #
        self._model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['acc'])

    def train(self):
        # standardized_train = preprocessing.scale(self._train["data"])
        # standardized_test = preprocessing.scale(self._test["data"])
        # self._hist_obj = self._model.fit(standardized_train, self._train['labels'], validation_data=(standardized_test, self._test['labels']), verbose=False, epochs=100, batch_size=256)
        self._hist_obj = self._model.fit(self._train["data"], self._train['labels'], validation_data=(self._test["data"], self._test['labels']), verbose=False, epochs=100, batch_size=256)
    
    def train_analytics(self):
        if self._hist_obj:
            return self._hist_obj.history
        return None

