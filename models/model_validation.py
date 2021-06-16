import pandas as pd
import numpy as np
from tqdm import tqdm
import collections
from sklearn.model_selection import KFold
import itertools

default_k = lambda x: 5 if x > 1000 else 10

def predict_label(df, model, label, k_function = default_k):
    """
    df must have input & labels columns (labels are a tab separated list)
    models must have .fit & .predict method that returns numpy array
    and a function k that takes in the number of samples and returns the number of folds
        for k-fold cross-validation
    """
    df['label'] = df['labels'].apply(lambda x: 1 if label in x.split('\t') else 0)
    bug = df.query("label == 1")
    try:
        nug = df.query("label == 0").sample(len(bug))
    except:
        # if theres not enough negative samples
        nug = df.query('label == 0')
        bug = bug.sample(len(nug))
    both = pd.concat([bug, nug]).sample(frac = 1)
    k = k_function(len(both))
    kf = KFold(n_splits=k, random_state=None, shuffle=False)
    X = both['input'].values.reshape(-1, 1)
    y = both['label'].values
    accuracy = []
    precision = []
    recall = []
    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        accuracy.append(np.mean(preds == y_test))
        precision.append(np.mean(preds[preds == 1] == y_test[preds == 1]))
        recall.append(np.mean(preds[y_test == 1] == y_test[y_test == 1]))
    return pd.DataFrame([[label, len(bug), np.mean(accuracy), np.mean(precision), np.mean(recall)]], columns = ['label' ,'n', 'accuracy', 'precision', 'recall'])

def predict_top_n(df, model_constructor, k_function = default_k, n = 20, ignore_labels = []):
    """
    wrapper for predict_label to predict top n labels
    df is the issue dataframe
    model_constructor creates a new untrained model
    """
    model = model_constructor() 
    labels_lists = [labels.split('\t') for labels in df['labels'].dropna()]
    all_items = list(itertools.chain.from_iterable(labels_lists))
    counter = collections.Counter(all_items)
    dfs = []
    for label, num in tqdm(counter.most_common(n)):
        if label in ignore_labels:
            continue
        dfs.append(predict_label(df, model, label, k_function))
    results_df = pd.concat(dfs)
    results_df.sort_values('precision', ascending = False)
    return results_df