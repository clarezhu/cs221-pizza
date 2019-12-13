import pandas as pd
import tensorflow as tf
from bert_serving.client import BertClient


bc = BertClient()

new_train_set = pd.read_csv("new_data/train_all.csv")
new_val_set = pd.read_csv("new_data/val_all.csv")


old_train_set = pd.read_csv("data/train_all.csv")
old_val_set = pd.read_csv("data/val_all.csv")

def get_encodes(df):
    samples = list(df['request_text'])
    text = [s[:50] + s[-50:] for s in samples]
    features = bc.encode(text)
    return features

def input(df):
    features = get_encodes(df)
    return features, np.array(df['requester_received_pizza'].astype(np.int32))

from sklearn.linear_model import LogisticRegression

train_features, train_y = input(new_train_set)
logreg = LogisticRegression()
logreg.fit(train_features, train_y)

val_features, val_y = input(new_val)
y_pred = logreg.predict(val_features)

score = accuracy_score(val_y,y_pred)
print(score)
