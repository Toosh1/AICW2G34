import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import  KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd

df = pd.read_csv("../data/2024_service_details_Norwich_to_London.csv")

print(df.head())

def time_to_minutes(t):
    """
    Parses time from HH:MM format to hours and minutes (separated)
    """
    h, m = map(int, t.split(':'))
    return h * 60 + m

# Drops any rows with missing planned_departure_time or actual_arrival_time fields
df.dropna(subset=['planned_departure_time', 'actual_arrival_time'], inplace=True)

df['planned_departure_time'] = df['planned_departure_time'].apply(time_to_minutes)
df['actual_arrival_time'] = df['actual_arrival_time'].apply(time_to_minutes)

df['actual_arrival_time'] = df.apply(
    lambda row: row['actual_arrival_time'] + 1440 if row['actual_arrival_time'] < row['planned_departure_time'] else row['actual_arrival_time'],
    axis=1
)

df['arrival_delay'] = df['actual_arrival_time'] - df['planned_departure_time']

df = df[df['arrival_delay'] < 120]
df = df[df['arrival_delay'] > -60]

X = df[['planned_departure_time']]
y = df['arrival_delay']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

knn_regressor = KNeighborsRegressor(n_neighbors=3)
knn_regressor.fit(X_train, y_train)

y_pred = knn_regressor.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Mean Squared Error: {mse}')
print(f'R-Squared: {r2}')

plt.scatter(X_test, y_test, color='red', label='Actual')
plt.scatter(X_test, y_pred, color='blue', label='Predicted')
plt.title('KNN Regression')
plt.xlabel('Planned Departure (mins)')
plt.ylabel('Arrival Delay (mins)')
plt.title('KNN Regression for Train Delays')
plt.legend()
plt.show()

def predict_delay_for_time(departure_time_str):
    """
    Predicts delay for given departure time (in format HH:MM)
    """
    h, m = map(int, departure_time_str.split(':'))
    departure_minutes = h * 60 + m

    predicted_delay = knn_regressor.predict([[departure_minutes]])
    return predicted_delay[0]
