from datetime import date
import numpy as np
import pandas as pd


'''Devuelve un valor promedio medido en el día actual y un valor promedio para la medición de los días anteriores
al actual de cada una de las variables de medición agrupados por códigos de estación.'''
def return_avg(df_final,var_sensor):
        
    #Obtener última fecha obtenida en el df
    today = df_final.iloc[0]['fechaobservacion'].date()

    
    # Filtrar el DataFrame por la fecha actual y la descripción del sensor
    df_filtered = df_final[(df_final['fechaobservacion'].dt.date == today) & (df_final['descripcionsensor'] == (var_sensor))]
    # Agrupar por código de sensor y calcular el promedio de los valores observados
    avg_data_today = df_filtered.groupby('codigoestacion').agg({
    'valorobservado': 'mean'
    }).reset_index()

    #Eliminar datos nulos
    avg_data_today.dropna(axis = 0, how = "any")
    avg_data_today = avg_data_today.rename(columns={'valorobservado': 'vo_today'})

    # Filtrar el DataFrame por la fecha anterior a hoy y la descripción del sensor
    df_filtered = df_final[(df_final['fechaobservacion'].dt.date < today) & (df_final['descripcionsensor'] == (var_sensor))]
    # Agrupar por código de sensor y calcular el promedio de los valores observados
    avg_data_bef_today = df_filtered.groupby('codigoestacion').agg({
    'valorobservado': 'mean'
    }).reset_index()

   
    #Eliminar datos nulos
    avg_data_bef_today.dropna(axis = 0, how = "any")
    avg_data_bef_today = avg_data_bef_today.rename(columns={'valorobservado': 'vo_bef_today'})
    
    return pd.merge(avg_data_today, avg_data_bef_today, on='codigoestacion', how='inner')


def fill_table(codstation, df_variation, var, value):
    # Verificar si el código de estación ya está en el DataFrame nuevo
    if codstation in df_variation['codigoestacion'].values:
        df_variation.loc[df_variation['codigoestacion'] == codstation, var] = value
    else:
        # Crear un nuevo DataFrame con la fila actual y concatenarlo al DataFrame nuevo
        nuevo_registro = pd.DataFrame({'codigoestacion': [codstation], var: [value]})
        nuevo_registro = nuevo_registro.fillna(0)
        df_variation = pd.concat([df_variation, nuevo_registro], ignore_index=True)

    return(df_variation)

# Retorna el valor de la correlación entre dos variables de medición
def find_corr(df_final, des_var_a, des_var_b, cod_estation):

    correlation = 0
   
    try:
        serie_a = df_final['valorobservado'].loc[(df_final['codigoestacion'] == cod_estation) & (df_final['descripcionsensor'] == des_var_a)].tolist()
        serie_b = df_final['valorobservado'].loc[(df_final['codigoestacion'] == cod_estation) & (df_final['descripcionsensor'] == des_var_b)].tolist()
        
        serie_a = pd.Series(serie_a)
        serie_b = pd.Series(serie_b)

        
        if len(serie_a) != len(serie_b):
            min_len = min(len(serie_a), len(serie_b))
            serie_a = serie_a[:min_len]
            serie_b = serie_b[:min_len]

        if validate_series(serie_a, serie_b):            
            correlation = serie_a.corr(serie_b)  

    except IndexError:
        correlation = 0

    
    return correlation if not pd.isna(correlation) else 0


# Validar que al realizar correlaciones no se generen errores
def validate_series(serie_a, serie_b):
      

    # Verificar que ambas series no estén vacías
    if serie_a.empty or serie_b.empty:
        return False
  
    if any(not isinstance(elemento, float) for elemento in serie_a) or any(not isinstance(elemento, float) for elemento in serie_b):        
        return False    
    
    # Convertir las listas en arrays de NumPy
    array_a = np.array(serie_a)
    array_b = np.array(serie_b)

    # Verificar que ninguna de las desviaciones estándar sea cero
    if np.std(array_a) == 0 or np.std(array_b) == 0:
        return False
    
    return True


# Retorna el valor dado a cada varaible de medición, de acuerdo con el comportamiento sugerido en cada delito

def assign_value(var_value, value):

    factor = 0
    #value /= 100
    
    if var_value == 0:
        factor = abs(value)
    elif var_value > 0:
        factor = value
    else:
        factor = -(value)
    
    return factor


'''Obtener un valor para cada uno de los delitos, de acuerdo con la afectación de cada uno de las
variables de medición y su correlación, sobre ellos'''

def level_variation(df_variation, corr_station, name, wd_ind, wd_corr, var_independent, var_corr):
    
    for station in df_variation['codigoestacion']:  
              
        lev_measure = 0

        values =[]

        for des_var, val_var in var_independent.items(): 

            values.append(assign_value(val_var, df_variation.loc[df_variation['codigoestacion'] == station, des_var].iloc[0]))

        values = [x for x in values if x != 0]    
        wd_independent = 0 if len(values) == 0 else wd_ind / len(values)
        lev_measure = sum([x * wd_independent for x in values])
        
        values.clear()
        
        '''Obtener valor para sumar al nivel de medida de cada delito, de acuerdo con la correlación obtenida para las
         correlaciones sugeridas para cada delito'''
        for corr_sta, corr_val in var_corr.items():

            if station in corr_station:

                des_var = corr_val[0]
                val_var = corr_val[1]
                type_corr = corr_val[2]               
                
                if corr_sta in corr_station[station]:
                   
                    if (type_corr == 'pos' and corr_station[station][corr_sta] > 0) or (type_corr == 'neg' and corr_station[station][corr_sta] < 0):
                        variable_sensor = df_variation.loc[df_variation['codigoestacion'] == station, des_var].iloc[0]
                        
                        if (val_var == 1 and variable_sensor >= 0) or (val_var == -1 and variable_sensor <= 0) or val_var == 0:

                            values.append(abs(corr_station[station][corr_sta]))

        wd_correlation = 0 if len(values) == 0 else wd_corr / len(values)
                            
        lev_measure += sum([x * wd_correlation for x in values])                            
                            
        df_variation.loc[df_variation['codigoestacion'] == station, name] = round(lev_measure, 3)       
        
    return df_variation


# Lista cada uno de los delitos de acuerdo con el análisis de causas y efectos

def environment_crimes(df_variation, corr_station):

    var_indep = 70 # Asigna un peso a la medición de variables independientemente
    var_corr = 30 # Asigna un peso a la medición de variables en conjunto


    '''Para cada uno de los delitos, se asigna a las varaibles independientes,
    el valor de 1 si el análisis de casusas y efectos sugiere que la varaible 
    debió subir, -1 si sugiere que debio bajar y 0 si solo sugiere que debio cambiar. 
    Para las correlaciones, se indican los mmismo valores solo para la primera variable usada
    en la correlación y se indica si la correción se sugirió como positiva o negativa.'''
    
    env_crimes={
        'deforestation': {
            'name': 'Level Deforestation',
            'wd_var': {
                'wd_independent': var_indep, 
                'wd_corr': var_corr 
            },
            'var_independent': {
                'dir_viento': 0,  # La deforestación puede afectar la dirección del viento.
                'humedad_aire': -1,  # La deforestación reduce la humedad del aire.
                'nivel_inst_rio': 1,  # Aumenta debido a la erosión.
                'nivel_max_rio': 1,  # Aumenta por la escorrentía.
                'precipitacion': 0,  # Puede variar.
                'pres_atmosferica': -1,  # Disminuye debido a la falta de vegetación.
                'temperatura': 1,  # Aumenta por la falta de sombra.
                'temp_max_aire': 1,  # Aumenta.
                'temp_min_aire': 0,  # Puede variar.
                'vel_viento': 1,  # Aumenta debido a la falta de barreras naturales.
            },    
            'var_corr': {
                'pres_atmosfericavel_viento': [
                    'pres_atmosferica', -1, 'neg'
                ],
                'temperaturapres_atmosferica': [
                    'temperatura', 1, 'neg'
                ],
                'temperaturahumedad_aire': [
                    'temperatura', 1, 'neg'
                ],
                'temperaturavel_viento': [
                    'temperatura', 1, 'pos'
                ],
                'vel_vientohumedad_aire': [
                    'vel_viento', 1, 'neg'
                ],
                'dir_vientotemp_max_aire': [
                    'dir_viento', 1, 'pos'
                ]        
            }
        },
        'illicit_use': {
            'name': 'Level Illicit Use',
            'wd_var': {
                'wd_independent': var_indep,
                'wd_corr': var_corr
            },
            'var_independent': {
                'humedad_aire': 0,
                'nivel_inst_rio': -1,
                'nivel_min_rio': -1,
                'temperatura': 1,
                'precipitacion': 0,
                'vel_viento': 1,
                'pres_atmosferica': -1, 
                'dir_viento': 0,  
                'temp_max_aire': 1,  
                'nivel_max_rio': -1,  
                'temp_min_aire': -1 
            },    
            'var_corr': {
                'humedad_airetemperatura': [
                    'humedad_aire', -1, 'neg'
                ],
                'humedad_aireprecipitacion': [
                    'humedad_aire', -1, 'neg'
                ],
                'nivel_inst_rionivel_min_rio': [
                    'nivel_inst_rio', -1, 'pos'
                ],
                'temperaturaprecipitacion': [
                    'temperatura', 1, 'neg'
                ],
                'temperaturanivel_min_rio': [
                    'temperatura', 1, 'neg'
                ],
                'pres_atmosfericavel_viento': [
                    'pres_atmosferica', -1, 'neg'
                ],
                'temp_max_airevel_viento': [
                    'temp_max_aire', 1, 'pos'
                ]    
            }
        },
        'ecocidios': {
            'name': 'Level Ecocidios',
            'wd_var': {
                'wd_independent': var_indep,
                'wd_corr': var_corr
            },
            'var_independent': {
                'dir_viento': 0,
                'humedad_aire': -1,
                'nivel_max_rio': 1,
                'precipitacion': 0,
                'pres_atmosferica': 1,
                'temperatura': 1,
                'temp_max_aire': 1,
                'temp_min_aire': 1, 
                'nivel_min_rio': 0,  
                'nivel_inst_rio': 1, 
                'vel_viento': 1
            },    
            'var_corr': {
                'precipitacionnivel_max_rio': [
                    'precipitacion', 1, 'pos'
                ],
                'temperaturanivel_min_rio': [
                    'temperatura', 1, 'neg'
                ],
                'temperaturapres_atmosferica': [
                    'temperatura', 1, 'pos'
                ],
                'temperaturahumedad_aire': [
                    'temperatura', 1, 'neg'
                ],
                'temperaturavel_viento': [
                    'temperatura', 1, 'pos'
                ],
                'nivel_inst_rioprecipitacion': [
                    'nivel_inst_rio', 1, 'pos'
                ]   
            }
        },
        'env_pollution': {
            'name': 'Level Environment Pollution',
            'wd_var': {
                'wd_independent': var_indep,
                'wd_corr': var_corr
            },
            'var_independent': {
                'precipitacion': 0,
                'pres_atmosferica':1,
                'temperatura': 1,
                'temp_max_aire': 1,
                'nivel_inst_rio':0,
                'nivel_min_rio':1,
                'vel_viento': 0,  
                'dir_viento': 0,  
                'humedad_aire': -1,  
                'temp_min_aire': 1, 
                'nivel_max_rio': 0 
            },    
            'var_corr': {
                'pres_atmosfericanivel_inst_rio': [
                    'pres_atmosferica', 1, 'pos'
                ],
                'temperaturapres_atmosferica': [
                    'temperatura', 1, 'pos'
                ],
                'temperaturaprecipitacion': [
                    'temperatura', 1, 'neg'
                ],
                'temperaturanivel_min_rio': [
                    'temperatura', 1, 'pos'
                ],
                'temperaturavel_viento': [
                    'temperatura', 1, 'pos'
                ],
                'dir_vientohumedad_aire': [
                    'dir_viento', 0, 'neg'
                ]    
            }
        }
    }

    
    for env_cr, det_crime in env_crimes.items():
        
        name = det_crime['name']
        wd_ind = det_crime['wd_var']['wd_independent']
        wd_corr = det_crime['wd_var']['wd_corr']
        var_indep = det_crime['var_independent']
        var_corr = det_crime['var_corr']

        # Obtener un valor representativo para cada uno de los delitos en una nuva columna
        df_variation = level_variation(df_variation, corr_station, name, wd_ind, wd_corr, var_indep, var_corr)
     
        
    return df_variation


def insert_correl(df_initial, dic_corr, new_columns):

    zeros_data = pd.DataFrame(0.0, index = df_initial.index, columns = new_columns)
    df_initial = pd.concat([df_initial, zeros_data], axis=1)

    for station in df_initial['codigoestacion']:
        if station in dic_corr:
            for col, value in dic_corr[station].items():
                if col in new_columns:
                    df_initial.loc[df_initial['codigoestacion'] == station, col] = value

    return df_initial
        