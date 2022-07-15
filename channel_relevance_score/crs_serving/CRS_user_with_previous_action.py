import pandas as pd
import numpy as np
import dateutil.parser


# Matrix factorization algorithm
def matrix_factorization(input_matrix, random_matrix_hours, random_matrix_days, distance, steps=5000, alpha=0.0002,
                         beta=0.0002):
    """
      -Initialize two random matrices(random_matrix_hours, random_matrix_days) and multiplied two matrices,
       their dimension should match the input matrix.
      -Iterate through each value in the input matrix and compare it with the values in the
       random matrix(random_matrix_a*random_matrix_b) to evaluate how far off the estimate is from
       the real matrix(error calculation).
      -Use gradient descent formulas to adjust each of the values in random_matrix_hours and random_matrix_days
       to find the appropriate direction to reduce the error based on the given loss function until
       it finds the minimum error rate.
    """
    random_matrix_days = random_matrix_days.T
    for step in range(steps):
        for row in range(len(input_matrix)):
            for columns in range(len(input_matrix[row])):
                if input_matrix[row][columns] > 0:

                    # calculate error
                    error = input_matrix[row][columns] - np.dot(random_matrix_hours[row, :], random_matrix_days[:, columns])

                    for values in range(distance):
                        # calculate gradient with alpha and beta parameter
                        random_matrix_hours[row][values] = random_matrix_hours[row][values] + alpha * (
                                2 * error * random_matrix_days[values][columns]
                                - beta * random_matrix_hours[row][values])
                        random_matrix_days[values][columns] = random_matrix_days[values][columns] + alpha * (
                                2 * error * random_matrix_hours[row][values]
                                - beta * random_matrix_days[values][columns])
        error = 0
        for row in range(len(input_matrix)):
            for columns in range(len(input_matrix[row])):
                if input_matrix[row][columns] > 0:
                    error = error + pow(
                        input_matrix[row][columns] - np.dot(random_matrix_hours[row, :], random_matrix_days[:, columns]), 2)
                    for values in range(distance):
                        error = error + (beta / 2) * (
                                pow(random_matrix_hours[row][values], 2) + pow(random_matrix_days[values][columns], 2))
        # 0.001: local minimum
        if error < 0.001:
            break
    return random_matrix_hours, random_matrix_days.T


# Calculating the channel relevance score for user with previous action
def crs_with_previous_action(user, pattern_level):
    res_predictions = {user.get("clientId"): dict()}
    channels = user.get("channels", [])

    # Calculating the channel relevance score for the each channels
    for channel in channels:
        click_dates, delivered_dates, opens_dates = [], [], []
        # Getting the click date for a single channel and convert to datetime format
        if "clicks" in channel:
            click_dates = [dateutil.parser.parse(date) for date in channel.get("clicks")]
        # Getting the delivered date for a single channel and convert to datetime format
        if "delivered" in channel:
            delivered_dates = [dateutil.parser.parse(date) for date in channel.get("delivered")]
        # Getting the opens date for a single channel and convert to datetime format
        if "opens" in channel:
            opens_dates = [dateutil.parser.parse(date) for date in channel.get("opens")]
        # Combine the list of click, open and delivered dates into single list
        dates = click_dates + opens_dates + delivered_dates
        # Calculating the CRS values for day_of_week pattern
        if pattern_level == 'day-of-week':
            hours = list(range(24))
            week_day = list(range(7))
            input_matrix = np.zeros((len(hours), len(week_day)))
            for date in dates:
                input_matrix[date.hour, date.weekday()] += 1
        # Calculating the CRS values for day_of_month pattern
        elif pattern_level == 'day-of-month':
            month_day = list(range(32))
            hours = list(range(24))
            input_matrix = np.zeros((len(hours), len(month_day)))
            input_matrix = np.delete(input_matrix, 0, 1)
            for date in dates:
                input_matrix[date.hour, date.day - 1] += 1
        # if user have no previous action timestamp then the CRS score will be zero
        if int(input_matrix.sum()) != 0:
            num_of_hours = len(input_matrix)
            num_of_days = len(input_matrix[0])
            distance = 1
            random_matrix_hours = np.random.rand(num_of_hours, distance)
            random_matrix_days = np.random.rand(num_of_days, distance)

            # Calculating CRS score using thr Matrix factorization
            predicted_a, predicted_b = matrix_factorization(input_matrix, random_matrix_hours, random_matrix_days,
                                                            distance)
            predicted_values = np.dot(predicted_a, predicted_b.T)
            prediction = pd.DataFrame(predicted_values)
            prediction = prediction.apply(lambda x: x / np.max(prediction.values) * 99, axis=1)
            prediction = prediction.astype('int')
            res_predictions[user.get("clientId")][channel['channel']] = prediction.to_dict()
        else:
            res_predictions[user.get("clientId")][channel['channel']] = pd.DataFrame(
                input_matrix). \
                astype('int').to_dict()


    return res_predictions
