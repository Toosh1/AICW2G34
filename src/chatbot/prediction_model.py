import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.neighbors import  KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd

df = pd.read_csv("../data/2024_service_details_Norwich_to_London.csv")

print(df.head())

def time_to_minutes(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

df['planned_departure_time'] = df['planned_departure_time'].apply(time_to_minutes)
df['actual_arrival_time'] = df['actual_arrival_time'].apply(time_to_minutes)
df['arrival_delay'] = df['actual_arrival_time'] - df['planned_departure_time']

X = df[['planned_departure_time']]
y = df['arrival_delay']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

knn_regressor = KNeighborsRegressor(n_neighbors=5)
knn_regressor.fit(X_train, y_train)

y_pred = knn_regressor.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Mean Squared Error: {mse}')
print(f'R-Squared: {r2}')

plt.scatter(X_test, y_test, color='hotpink', label='Actual')
plt.scatter(X_test, y_pred, color='orange', label='Predicted')
plt.title('KNN Regression')
plt.xlabel('Planned Departure (mins)')
plt.ylabel('Arrival Delay (mins)')
plt.title('KNN Regression for Train Delays')
plt.legend()
plt.show()
