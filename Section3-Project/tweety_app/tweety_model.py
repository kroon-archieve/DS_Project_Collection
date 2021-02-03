import os
import numpy as np
from sklearn.linear_model import LogisticRegression
from embedding_as_service_client import EmbeddingClient

en = EmbeddingClient(host='54.180.124.154', port=8989)


def predict_value(model, val):
    result = model.predict(val)
    return result


def embed_values(raw_values):
    vecs = en.encode([raw_values])
    return vecs


def get_input():
    val_X = input("Input for X : ")
    val_y = input("Input for y : ")
    return val_X, val_y


def train_model(X, y):
    classifier = LogisticRegression()
    classifier.fit(X, y)

    return classifier


if __name__ == "__main__":
    X_1, y_1 = get_input()
    X_2, y_2 = get_input()

    embedded_X_1 = embed_values(X_1)
    embedded_X_2 = embed_values(X_2)

    trained_model = train_model(np.concatenate(
        embedded_X_1,  embedded_X_2), [y_1, y_2])

    val_to_predict = input("Value to predict : ")

    predicted_value = predict_value(trained_model, val_to_predict)

    print(predicted_value)
