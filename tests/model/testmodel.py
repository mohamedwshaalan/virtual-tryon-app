from sklearn.linear_model import LinearRegression
import numpy as np

class SimpleModel:
    def __init__(self):
        # Sample data for demonstration
        self.X_train = np.array([[1], [2], [3], [4], [5]])
        self.y_train = np.array([2, 4, 5, 4, 5])

        # Create and fit a simple linear regression model
        self.model = LinearRegression()
        self.model.fit(self.X_train, self.y_train)

    def predict(self, input_value):
        input_data = np.array([[input_value]])
        prediction = self.model.predict(input_data)
        return prediction[0]
