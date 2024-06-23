import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

    


def train_predict(df_historical, df_new_data, measure_var, new_columns_corr):   

    # Seleccionar las características (X) y la variable objetivo (y)
    X = df_historical[measure_var + ['codigoestacion'] + new_columns_corr]
    y_deforestation = df_historical['Level Deforestation']
    y_illicit_use = df_historical['Level Illicit Use']
    y_ecocidios = df_historical['Level Ecocidios']
    y_environment_pollution = df_historical['Level Environment Pollution']

    # Dividir los datos históricos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train_def, y_test_def = train_test_split(X, y_deforestation, test_size=0.2, random_state=42)
    _, _, y_train_illicit, y_test_illicit = train_test_split(X, y_illicit_use, test_size=0.2, random_state=42)
    _, _, y_train_eco, y_test_eco = train_test_split(X, y_ecocidios, test_size=0.2, random_state=42)
    _, _, y_train_poll, y_test_poll = train_test_split(X, y_environment_pollution, test_size=0.2, random_state=42)

    # Crear y entrenar el modelo RandomForestRegressor
    model_def = RandomForestRegressor(n_estimators=100, random_state=42)
    model_def.fit(X_train, y_train_def)

    model_illicit = RandomForestRegressor(n_estimators=100, random_state=42)
    model_illicit.fit(X_train, y_train_illicit)

    model_eco = RandomForestRegressor(n_estimators=100, random_state=42)
    model_eco.fit(X_train, y_train_eco)

    model_poll = RandomForestRegressor(n_estimators=100, random_state=42)
    model_poll.fit(X_train, y_train_poll)

    # Hacer predicciones en el conjunto de prueba
    y_pred_def = model_def.predict(X_test)
    mse_def = mean_squared_error(y_test_def, y_pred_def)
    print(f'Mean Squared Error for Deforestation: {mse_def}')

    y_pred_illicit = model_illicit.predict(X_test)
    mse_illicit = mean_squared_error(y_test_illicit, y_pred_illicit)
    print(f'Mean Squared Error for Illicit Use: {mse_illicit}')

    y_pred_eco = model_eco.predict(X_test)
    mse_eco = mean_squared_error(y_test_eco, y_pred_eco)
    print(f'Mean Squared Error for Ecocidios: {mse_eco}')

    y_pred_poll = model_poll.predict(X_test)
    mse_poll = mean_squared_error(y_test_poll, y_pred_poll)
    print(f'Mean Squared Error for Environment Pollution: {mse_poll}')

    
    # Hacer predicciones con los nuevos datos
    new_data_predictions_def = model_def.predict(df_new_data)
    new_data_predictions_illicit = model_illicit.predict(df_new_data)
    new_data_predictions_eco = model_eco.predict(df_new_data)
    new_data_predictions_poll = model_poll.predict(df_new_data)

    # Agregar las predicciones al DataFrame de nuevos datos
    
    df_new_data['Level Deforestation'] = new_data_predictions_def.round(1)
    df_new_data['Level Illicit Use'] = new_data_predictions_illicit.round(1)
    df_new_data['Level Ecocidios'] = new_data_predictions_eco.round(1)
    df_new_data['Level Environment Pollution'] = new_data_predictions_poll.round(1)

    
    # Importancia de las Características

    '''importances = model_def.feature_importances_
    features = X.columns
    indices = np.argsort(importances)[::-1]
    plt.figure(figsize=(10, 6))
    plt.title('Importancia de las características')
    plt.bar(range(X.shape[1]), importances[indices], align='center')
    plt.xticks(range(X.shape[1]), [features[i] for i in indices], rotation=90)
    plt.tight_layout()
    plt.show()
'''
    

    return df_new_data
