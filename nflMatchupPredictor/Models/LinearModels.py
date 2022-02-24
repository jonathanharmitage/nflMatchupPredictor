import pandas as pd
from sklearn.linear_model import LogisticRegression

# import numpy as np


class LinearModels:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def define_clf(self, clf_type="lr"):
        if clf_type == "lr":
            clf_lr = LogisticRegression()
        return clf_lr

    def logistic_regr(self, design_matrix, response):
        clf_lr = self.define_clf()
        clf_lr.fit(X=design_matrix, y=response)
        return clf_lr

    def get_wgts(self, model_object):
        # intercept = model_object.intercept_
        bias = model_object.intercept_
        wgts = model_object.coef_
        bias_tbl = pd.DataFrame(bias, columns=["bias"])
        wgts_tbl = pd.DataFrame(wgts, columns=model_object.feature_names_in_)
        return pd.concat([bias_tbl, wgts_tbl], axis=1)

    def make_inference(self, model_object, data):
        pred_cls = model_object.predict(data)
        pred_probs = model_object.predict_proba(data)

        return pred_cls, pred_probs
