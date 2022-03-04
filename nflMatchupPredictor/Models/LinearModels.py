import pandas as pd
import numpy as np
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
            the outcome of interest

        Returns
        -------
        Logistic Regression (sklearn)
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
        model_object : Logistic Regression (sklearn)
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

    def make_random_sample_test(self, data_object, nbr_sample=2):
        tmp_sample = data_object.sample(n=nbr_sample).reset_index(drop=True)
        # tmp_sample_answer = tmp_sample["home_team_wins"]
        return tmp_sample

    def make_inference(self, model_object, data_object):
        """
        Produce estimates for data.

        Parameters
        ----------
        model_object : Logistic Regression (sklearn)
            _description_
        data_object : DataFrame or array-like object
            _description_

        Returns
        -------
        Dict
            Contains the following:
                1. predicted class --> array
                2. predicted probabilities --> array
                3. standard deviation of the predicted probabilities --> array
                4. absolute difference of the predicted probabilities --> array

        Notes
        -----
        Calculating and returning the standard deviation and absolute difference of the
        predicted probabilities allows for further underestanding of the models decision
        boundary.
        """
        pred_cls = model_object.predict(data_object)
        pred_probs = model_object.predict_proba(data_object)

        std_diff = np.std(pred_probs, axis=1)
        abs_diff = np.abs(np.diff(pred_probs, axis=1))
        abs_diff = abs_diff.reshape(std_diff.shape)

        infer_dt = {
            "pred_cls": pred_cls,
            "pred_probs": pred_probs,
            "std_diff": std_diff,
            "abs_diff": abs_diff,
        }

        return infer_dt
