"""
Train a Random Forest classifier on the labeled ADHD dataset.
Evaluates against the rules-based classifier for comparison.

Run with: uv run python dataset/train.py
"""

import json
import sys
import csv
from pathlib import Path

# Add backend root to path so we can import app services
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.classifier import classify

try:
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.preprocessing import LabelEncoder
except ImportError:
    print("Run: uv add scikit-learn pandas")
    sys.exit(1)

FEATURES = ["mood", "focus", "energy", "overwhelm", "anxiety"]
LABEL = "stage"
DATA_PATH = Path(__file__).parent / "adhd_checkins_labeled.csv"

STAGE_LABELS = {
    1: "Initiation Failure",
    2: "Decision Paralysis",
    3: "Overwhelm Freeze",
    4: "Urgency Dependency",
}


def load_data() -> tuple:
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES].values
    y = df[LABEL].values
    return df, X, y


def evaluate_rules_classifier(df: pd.DataFrame) -> dict:
    """Run every row through the existing rules-based classifier and measure accuracy."""
    correct = 0
    per_stage = {s: {"correct": 0, "total": 0} for s in range(1, 5)}

    for _, row in df.iterrows():
        checkin = {f: int(row[f]) for f in FEATURES}
        result = classify(checkin)
        predicted = result["stage"]
        actual = int(row[LABEL])
        per_stage[actual]["total"] += 1
        if predicted == actual:
            correct += 1
            per_stage[actual]["correct"] += 1

    accuracy = correct / len(df)
    return {"overall_accuracy": accuracy, "per_stage": per_stage}


def train_random_forest(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        random_state=42,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)
    return clf, X_train, X_test, y_train, y_test


def print_results(clf, X_train, X_test, y_train, y_test, rules_eval: dict):
    y_pred = clf.predict(X_test)
    cv_scores = cross_val_score(clf, X_train, y_train, cv=5)

    print("\n" + "=" * 60)
    print("RULES-BASED CLASSIFIER (current baseline)")
    print("=" * 60)
    rules_acc = rules_eval["overall_accuracy"]
    print(f"  Overall accuracy: {rules_acc:.1%}")
    print(f"  {'Stage':<5} {'Label':<25} {'Accuracy'}")
    print("  " + "-" * 50)
    for stage, stats in rules_eval["per_stage"].items():
        acc = stats["correct"] / stats["total"] if stats["total"] else 0
        print(f"  {stage:<5} {STAGE_LABELS[stage]:<25} {acc:.1%}  ({stats['correct']}/{stats['total']})")

    print("\n" + "=" * 60)
    print("RANDOM FOREST CLASSIFIER")
    print("=" * 60)
    print(f"  Training set:       {len(X_train)} rows")
    print(f"  Test set:           {len(X_test)} rows")
    print(f"  5-fold CV accuracy: {cv_scores.mean():.1%} ± {cv_scores.std():.1%}")
    print(f"  Test accuracy:      {(y_pred == y_test).mean():.1%}")

    print("\n  Classification report:")
    target_names = [STAGE_LABELS[s] for s in sorted(set(y_test))]
    report = classification_report(y_test, y_pred, target_names=target_names, digits=3)
    for line in report.split("\n"):
        print("    " + line)

    print("  Confusion matrix (rows=actual, cols=predicted):")
    cm = confusion_matrix(y_test, y_pred, labels=sorted(set(y_test)))
    header = "       " + "  ".join(f"S{s}" for s in sorted(set(y_test)))
    print("    " + header)
    for i, row in enumerate(cm):
        stage = sorted(set(y_test))[i]
        print(f"    S{stage} actual  " + "  ".join(f"{v:3d}" for v in row))

    print("\n  Feature importances:")
    importances = sorted(
        zip(FEATURES, clf.feature_importances_), key=lambda x: x[1], reverse=True
    )
    for feat, imp in importances:
        bar = "█" * int(imp * 40)
        print(f"    {feat:<12} {imp:.3f}  {bar}")

    print("\n" + "=" * 60)
    delta = (y_pred == y_test).mean() - rules_acc
    direction = "better" if delta > 0 else "worse"
    print(f"  Random Forest is {abs(delta):.1%} {direction} than rules-based on test set.")
    print("=" * 60)


if __name__ == "__main__":
    print(f"Loading data from {DATA_PATH} ...")
    df, X, y = load_data()
    print(f"  {len(df)} rows, {len(set(y))} classes, {len(FEATURES)} features")

    print("\nEvaluating rules-based classifier ...")
    rules_eval = evaluate_rules_classifier(df)

    print("Training Random Forest ...")
    clf, X_train, X_test, y_train, y_test = train_random_forest(X, y)

    print_results(clf, X_train, X_test, y_train, y_test, rules_eval)
