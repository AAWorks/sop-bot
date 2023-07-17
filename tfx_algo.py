import numpy as np
import tensorflow as tf
import tensorflow.keras as keras # pylance raises <Import "tensorflow.keras" could not be resolved> - Ignore

class DNNModel:
    def __init__(self, records):
        training_set_frac = 0.90

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
        #self._model.add(tf.keras.layers.Dense(units=100, activation='relu'))
        self._model.add(tf.keras.layers.Dropout(0.8))
        self._model.add(tf.keras.layers.Dense(units=self._init_layer * 2 // 3, activation='relu'))
        self._model.add(tf.keras.layers.Dropout(0.6))
        self._model.add(tf.keras.layers.Dense(units=self._init_layer // 2, activation='relu'))
        self._model.add(tf.keras.layers.Dropout(0.5))
        self._model.add(tf.keras.layers.Dense(units=1, activation='sigmoid'))#, activation='relu'))
        opt = tf.keras.optimizers.Adam(learning_rate=0.001) #learning_rate=1e-7
        self._model.compile(loss=tf.keras.losses.BinaryCrossentropy(), optimizer=opt, metrics=['accuracy']) # from_logits?

    def train(self):
        self._hist_obj = self._model.fit(self._train["data"], self._train['labels'], validation_split=0.15, verbose=1, epochs=500, batch_size=128, shuffle=True)
        # self._test["data"], self._test['labels']
    
    def train_analytics(self):
        if self._hist_obj:
            return self._hist_obj.history
        return None
    
    def evaluate(self):
        eval = self._model.evaluate(self._test["data"], self._test['labels'], verbose=1, return_dict=True, batch_size=64)     
        return eval
    
    def get_test_predictions(self):
        eval = self._model.predict(self._test["data"], verbose=1, batch_size=64)
        
        return eval
