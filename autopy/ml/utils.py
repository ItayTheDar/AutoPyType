import threading
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

class LazyClassifier:
    def __init__(self, model, params, X_train, y_train, X_test, y_test):
        self.model = model
        self.params = params
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def evaluate(self):
        grid_search = GridSearchCV(self.model, self.params, cv=5)
        grid_search.fit(self.X_train, self.y_train)
        score = grid_search.score(self.X_test, self.y_test)
        return grid_search.best_params_, score

def find_best_model(X, y):
    # Preprocess data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Define models and their respective hyperparameter grids
    models = [
        (LogisticRegression(), {'C': [0.1, 1, 10]}),
        (SVC(), {'C': [0.1, 1, 10], 'kernel': ['linear', 'rbf']}),
        (RandomForestClassifier(), {'n_estimators': [10, 100, 1000]})
    ]

    # Run grid search in a separate thread for each model
    threads = []
    results = {}
    classifiers = []
    for model, params in models:
        classifier = LazyClassifier(model, params, X_train, y_train, X_test, y_test)
        classifiers.append(classifier)
        thread = threading.Thread(target=classifier.evaluate)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Collect results from each thread
    for classifier in classifiers:
        results[classifier.model] = classifier.evaluate()

    # Choose the model with the highest score
    best_model = max(results, key=lambda x: results[x]['score'])
    return best_model, results[best_model]['params']



if __name__ == "__main__":
    # Load data
    from sklearn.datasets import load_iris
    X, y = load_iris(return_X_y=True)

    # Find the best model
    best_model, best_params = find_best_model(X, y)

    # Print the best model and its hyperparameters
    print(f"Best model: {best_model}")
    print(f"Best parameters: {best_params}")