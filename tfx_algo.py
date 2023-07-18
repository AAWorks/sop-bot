import numpy as np
import tensorflow as tf

class DNNModel:
    def __init__(self, records):
        training_set_frac = 0.7

        self._features = list(records.columns)
        self._features.remove("result")

        train_len = int(training_set_frac * records.shape[0])
        train = records.head(train_len)
        self._test = records.tail(records.shape[0] - train_len)

        self._train = {
            'data': np.array(train[self._features]), 
            'labels': np.array(train["result"])
        }

        self._init_layer = records.shape[1] - 1

        self._model = tf.keras.Sequential()

        self._hist_obj = None
    
    def _get_test_data(self, val=None):
        if val:
            test = self._test.loc[self._test['result'] == val]
        else:
            test = self._test
        return {
            'data': np.array(test[self._features]), 
            'labels': np.array(test["result"])
        }
    
    def build(self):
        self._model.add(tf.keras.layers.Dropout(0.2, input_shape=[self._init_layer,]))
        self._model.add(tf.keras.layers.Dense(units=self._init_layer, activation='relu', input_shape=[self._init_layer,]))
        self._model.add(tf.keras.layers.Dropout(0.2))
        self._model.add(tf.keras.layers.Dense(units=22, activation='relu'))
        self._model.add(tf.keras.layers.Dense(units=1, activation='sigmoid'))#, activation='relu'))
        opt = tf.keras.optimizers.Adam(learning_rate=0.001) #learning_rate=1e-7
        self._model.compile(loss=tf.keras.losses.BinaryCrossentropy(from_logits=False), optimizer=opt, metrics=['accuracy']) # from_logits?

    def train(self):
        test = self._get_test_data()
        self._hist_obj = self._model.fit(self._train["data"], self._train['labels'], validation_data=(test["data"], test["labels"]), verbose=1, epochs=200, batch_size=16, shuffle=True)#, callbacks=[earlystopping])
        # self._test["data"], self._test['labels']
    
    def train_analytics(self):
        if self._hist_obj:
            return self._hist_obj.history
        return None
    
    def evaluate(self):
        test = self._get_test_data(0)
        eval = self._model.evaluate(test["data"], test['labels'], verbose=1, return_dict=True, batch_size=32)     
        return eval
    
    def get_test_predictions(self):
        test = self._get_test_data()
        eval = self._model.predict(test["data"], verbose=1, batch_size=32)
        
        return eval
    
    def evaluate_on_confidence(self):
        test = self._get_test_data()
        evals = self.get_test_predictions()

        eval_map = zip(test['labels'], evals)

        acc_list = []
        for label, eval in eval_map:
            if eval > 0.6:
                acc_list.append(1 if label == 1 else 0)
            elif eval < 0.4:
                acc_list.append(1 if label == 0 else 0)
        
        return sum(acc_list)/len(acc_list)
            
