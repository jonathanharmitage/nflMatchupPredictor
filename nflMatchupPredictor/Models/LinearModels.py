import pandas as pd
from sklearn.linear_model import LogisticRegression

# import numpy as np


class LinearModels:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def define_clf(self, clf_type="lr"):
        """
        Define a logisitic regression model.

        Parameters
        ----------
        clf_type : str, optional
            _description_, by default "lr"

        Returns
        -------
        _type_
            _description_
        """
        if clf_type == "lr":
            clf_lr = LogisticRegression()
        return clf_lr

    def logistic_regr(self, design_matrix, response):
        """
        Fit a logistic regression model to data.

        Parameters
        ----------
        design_matrix : DataFrame
            _description_
        response : Vector
            _description_

        Returns
        -------
        _type_
            _description_
        """
        clf_lr = self.define_clf()
        clf_lr.fit(X=design_matrix, y=response)
        return clf_lr

    def get_wgts(self, model_object):
        """
        Generate bias and weights (coefficients) from a linear model.

        Parameters
        ----------
        model_object : _type_
            _description_

        Returns
        -------
        DataFrame
            _description_
        """
        # intercept = model_object.intercept_
        bias = model_object.intercept_
        wgts = model_object.coef_
        bias_tbl = pd.DataFrame(bias, columns=["bias"])
        wgts_tbl = pd.DataFrame(wgts, columns=model_object.feature_names_in_)
        return pd.concat([bias_tbl, wgts_tbl], axis=1)

    def make_inference(self, model_object, data):
        """
        Produce estimates for data.

        Parameters
        ----------
        model_object : _type_
            _description_
        data : DataFrame or array-like object
            _description_

        Returns
        -------
        Array
            _description_
        Array
            _description_
        """
        pred_cls = model_object.predict(data)
        pred_probs = model_object.predict_proba(data)

        return pred_cls, pred_probs
