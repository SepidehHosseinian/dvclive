import copy
from pathlib import Path

from dvclive.serialize import dump_json

from .base import Data


class SKLearnPlot(Data):
    suffixes = [".json"]
    subfolder = "sklearn"

    def __init__(self, name: str, output_folder: str, **kwargs) -> None:  # noqa: ARG002
        super().__init__(name, output_folder)
        self.name = self.name.replace(".json", "")

    @property
    def output_path(self) -> Path:
        _path = Path(f"{self.output_folder / self.name}.json")
        _path.parent.mkdir(exist_ok=True, parents=True)
        return _path

    @staticmethod
    def could_log(val: object) -> bool:
        if isinstance(val, tuple) and len(val) == 2:  # noqa: PLR2004
            return True
        return False

    def get_properties(self):
        raise NotImplementedError


class Roc(SKLearnPlot):
    DEFAULT_PROPERTIES = {
        "template": "simple",
        "x": "fpr",
        "y": "tpr",
        "title": "Receiver operating characteristic (ROC)",
        "x_label": "False Positive Rate",
        "y_label": "True Positive Rate",
    }

    def get_properties(self):
        return copy.deepcopy(self.DEFAULT_PROPERTIES)

    def dump(self, val, **kwargs) -> None:
        from sklearn import metrics

        fpr, tpr, roc_thresholds = metrics.roc_curve(
            y_true=val[0], y_score=val[1], **kwargs
        )
        roc = {
            "roc": [
                {"fpr": fp, "tpr": tp, "threshold": t}
                for fp, tp, t in zip(fpr, tpr, roc_thresholds)
            ]
        }
        dump_json(roc, self.output_path)


class PrecisionRecall(SKLearnPlot):
    DEFAULT_PROPERTIES = {
        "template": "simple",
        "x": "recall",
        "y": "precision",
        "title": "Precision-Recall Curve",
        "x_label": "Recall",
        "y_label": "Precision",
    }

    def get_properties(self):
        return copy.deepcopy(self.DEFAULT_PROPERTIES)

    def dump(self, val, **kwargs) -> None:
        from sklearn import metrics

        precision, recall, prc_thresholds = metrics.precision_recall_curve(
            y_true=val[0], probas_pred=val[1], **kwargs
        )

        prc = {
            "precision_recall": [
                {"precision": p, "recall": r, "threshold": t}
                for p, r, t in zip(precision, recall, prc_thresholds)
            ]
        }
        dump_json(prc, self.output_path)


class Det(SKLearnPlot):
    DEFAULT_PROPERTIES = {
        "template": "simple",
        "x": "fpr",
        "y": "fnr",
        "title": "Detection error tradeoff (DET)",
        "x_label": "False Positive Rate",
        "y_label": "False Negative Rate",
    }

    def get_properties(self):
        return copy.deepcopy(self.DEFAULT_PROPERTIES)

    def dump(self, val, **kwargs) -> None:
        from sklearn import metrics

        fpr, fnr, roc_thresholds = metrics.det_curve(
            y_true=val[0], y_score=val[1], **kwargs
        )

        det = {
            "det": [
                {"fpr": fp, "fnr": fn, "threshold": t}
                for fp, fn, t in zip(fpr, fnr, roc_thresholds)
            ]
        }
        dump_json(det, self.output_path)


class ConfusionMatrix(SKLearnPlot):
    DEFAULT_PROPERTIES = {
        "template": "confusion",
        "x": "actual",
        "y": "predicted",
        "title": "Confusion Matrix",
        "x_label": "True Label",
        "y_label": "Predicted Label",
    }

    def __init__(self, name: str, output_folder: str, **kwargs) -> None:
        super().__init__(name, output_folder)
        self.normalized = kwargs.get("normalized") or False

    def get_properties(self):
        properties = copy.deepcopy(self.DEFAULT_PROPERTIES)
        if self.normalized:
            properties["template"] = "confusion_normalized"
        return properties

    def dump(self, val, **kwargs) -> None:  # noqa: ARG002
        cm = [
            {"actual": str(actual), "predicted": str(predicted)}
            for actual, predicted in zip(val[0], val[1])
        ]
        dump_json(cm, self.output_path)


class Calibration(SKLearnPlot):
    DEFAULT_PROPERTIES = {
        "template": "simple",
        "x": "prob_pred",
        "y": "prob_true",
        "title": "Calibration Curve",
        "x_label": "Mean Predicted Probability",
        "y_label": "Fraction of Positives",
    }

    def get_properties(self):
        return copy.deepcopy(self.DEFAULT_PROPERTIES)

    def dump(self, val, **kwargs) -> None:
        from sklearn import calibration

        prob_true, prob_pred = calibration.calibration_curve(
            y_true=val[0], y_prob=val[1], **kwargs
        )

        _calibration = {
            "calibration": [
                {"prob_true": pt, "prob_pred": pp}
                for pt, pp in zip(prob_true, prob_pred)
            ]
        }
        dump_json(_calibration, self.output_path)
