import numpy as np
import tensorflow as tf

class DNNModel:
    def __init__(self, records):
        training_set_frac = 0.8

        self._features = list(records.columns)
        self._features.remove("result")

        train_len = int(training_set_frac * records.shape[0])
        train = records.head(train_len)
        self._test = records.tail(records.shape[0] - train_len)

        print(f"***DIAG: {train.loc[train['result'] == 1].shape[0]}, {train.loc[train['result'] == 0].shape[0]}")

        self._train = {
            'data': np.array(train[self._features]), 
            'labels': np.array(train["result"])
        }

        self._init_layer = records.shape[1] - 1

        self._model = tf.keras.Sequential()

        self._hist_obj = None
    
    def _get_test_data(self, val=None):
        if val is not None:
            test = self._test.loc[self._test['result'] == val]
        else:
            test = self._test
        return {
            'data': np.array(test[self._features]), 
            'labels': np.array(test["result"])
        }
    
    def build(self):
        self._model.add(tf.keras.layers.Dense(units=self._init_layer, activation='relu', input_shape=[self._init_layer,]))
        self._model.add(tf.keras.layers.Dropout(0.2))
        self._model.add(tf.keras.layers.Dense(units=self._init_layer * 2 // 3, activation='relu'))
        self._model.add(tf.keras.layers.Dropout(0.2))

        self._model.add(tf.keras.layers.Dense(units=1, activation='sigmoid'))
        opt = tf.keras.optimizers.Adam(learning_rate=0.0001)
        self._model.compile(loss=tf.keras.losses.BinaryCrossentropy(from_logits=False), optimizer=opt, metrics=[
        tf.keras.metrics.BinaryAccuracy(name='accuracy'),
        tf.keras.metrics.Precision(name='precision'),
        tf.keras.metrics.Recall(name='recall')
    ])

    def train(self):
        test = self._get_test_data()
        self._hist_obj = self._model.fit(self._train["data"], self._train['labels'], validation_data=(test["data"], test["labels"]), epochs=50, batch_size=32, verbose=1, shuffle=True)#, callbacks=[earlystopping])
        # self._test["data"], self._test['labels']
    
    def train_analytics(self):
        if self._hist_obj:
            return self._hist_obj.history
        return None
    
    def evaluate(self):
        test = self._get_test_data(0)
        eval = self._model.evaluate(test["data"], test['labels'], return_dict=True, batch_size=32, verbose=0)     
        return eval
    
    def get_test_predictions(self, mode=None):
        test = self._get_test_data(mode)
        eval = self._model.predict(test["data"], batch_size=32, verbose=0)
        
        return eval
    
    def evaluate_train_on_confidence(self):
        evals = self._model.predict(self._train["data"], batch_size=32, verbose=0)

        eval_map = zip(self._train['labels'], evals)

        acc_list = []
        for label, eval in eval_map:
            if eval > 0.50:
                acc_list.append(1 if label == 1 else 0)
            elif eval < 0.50:
                acc_list.append(1 if label == 0 else 0)
        
        if not acc_list: return 0

        return sum(acc_list)/len(acc_list)
    
    def evaluate_on_confidence(self, mode=None):
        test = self._get_test_data(mode)
        evals = self.get_test_predictions(mode)

        eval_map = zip(test['labels'], evals)

        acc_list = []
        for label, eval in eval_map:
            if eval > 0.50:
                acc_list.append(1 if label == 1 else 0)
            elif eval < 0.50:
                acc_list.append(1 if label == 0 else 0)
        
        if not acc_list: return 0

        return sum(acc_list)/len(acc_list), len(acc_list) / len(evals), len(test['labels']) / len(self._get_test_data()['labels'])
    
    def raw_prediction(self, aggregate_stats):
        return self._model.predict(aggregate_stats, batch_size=32, verbose=0)[0][0]
    
    def pretty_prediction(self, aggregate_stats, home_team, away_team):
        probability = float(str(self.raw_prediction(aggregate_stats)))
        probability *= 100
        winning_team, losing_team = (home_team, away_team) if probability >= 50 else (away_team, home_team)
        
        return probability, str(f":gear: SOP Bot is predicting a {probability}% chance that {winning_team} will beat {losing_team}")
            
