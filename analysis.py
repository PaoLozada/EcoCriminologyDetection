import pandas as pd
import matplotlib.pyplot as plt
from sodapy import Socrata
from datetime import date
from calculations import *
from test_and_train import *
import folium
from folium.plugins import MarkerCluster
import itertools
from mpld3 import fig_to_html

def main_process():

    cliente=Socrata('www.datos.gov.co', None)

    df_final = pd.DataFrame()  # Inicializar DataFrame vacío

    # Definir las columnas que se usaran para consolidar la información
    columns = "codigoestacion, codigosensor, fechaobservacion, valorobservado, "\
            "nombreestacion, departamento, municipio, zonahidrografica, latitud, "\
            "longitud, descripcionsensor, unidadmedida"           


    '''Definir APIs para importar datos, importar los datos de 
    cada una de ellas y consolidarlas en el mismo DF'''

    url_api = [
    "vfth-yucv",
    "57sv-p2fu",
    "uext-mhny",
    "sgfv-3yp8",
    "sbwg-7ju4",
    "s54a-sgyg",
    "pt9a-aamx",
    "kiw7-v9ta",
    "ccvq-rp9s",
    "bdmn-sqnh",
    "afdg-3zpb",
    "62tk-nxj5"
    ]

    # Crear consuta para filtrar por demparmento y fecha retrocediendo un año desde la fecha actual
    today = date.today()
    date_inf = today.replace(year=today.year - 1)
    departamentos = "'CUNDINAMARCA', 'BOYACÁ'"
    query = f"departamento in ({departamentos}) AND fechaobservacion >= '{date_inf}'"
    cantidad_filas = 500

    for set_data in url_api:

        result=cliente.get(
            set_data, 
            where = query, 
            order = 'fechaobservacion DESC', 
            select = columns, 
            limit = cantidad_filas
            )
        
        df=pd.DataFrame.from_records(result)
        df_final = pd.concat([df_final, df], ignore_index=True)

    del df

    # Eliminar duplicados
    df_final.drop_duplicates(inplace = True)

    # Convertir la columna 'valorobservado' a tipo numerico y la columna 'fechaobservacion' a tipo fecha
    df_final['valorobservado'] = pd.to_numeric(df_final['valorobservado'], errors='coerce')
    df_final['fechaobservacion'] = pd.to_datetime(df_final['fechaobservacion'], errors='coerce')
    df_final['codigoestacion'] = pd.to_numeric(df_final['codigoestacion'], errors='coerce')

    # Eliminar datos nulos
    df_final.dropna(axis = 0, how = "any")

    # Eliminar filas con valor '0' en 'valorobservado'
    df_final = df_final[df_final['valorobservado'] != 0]

    df_final.sort_values(by='fechaobservacion', ascending=False, inplace=True)

    # Estandarizar nombres de variables en la columna "descripcionsensor"

    df_final['descripcionsensor'] = df_final['descripcionsensor'].replace({
        'Nivel Maximo':                         'nivel_max_rio', 
        'NIVEL MÁXIMO':                         'nivel_max_rio',                  
        'GPRS - HUMEDAD DEL AIRE A 2 m':        'humedad_aire',
        'Humedad del aire 2 mt':                'humedad_aire',
        'GPRS - VELOCIDAD DEL VIENTO':          'vel_viento',
        'VELOCIDAD DEL VIENTO':                 'vel_viento',
        'Velocidad Viento(10 min)':             'vel_viento',
        'GPRS - TEMPERATURA DEL AIRE A 2 m':    'temperatura',
        'Temp Aire 2 m':                        'temperatura',
        'TEMPERATURA DEL AIRE A 2 m':           'temperatura',
        'GPRS - PRECIPITACIÓN':                 'precipitacion',
        'Precipitacion':                        'precipitacion',
        'PRECIPITACIÓN':                        'precipitacion',
        'Nivel Minimo':                         'nivel_min_rio',
        'NIVEL MÍNIMO':                         'nivel_min_rio',
        'DIRECCIÓN DEL VIENTO':                 'dir_viento',
        'Direccion Viento (10 min)':            'dir_viento',
        'Temp Max Aire 2 m':                    'temp_max_aire',
        'TEMPERATURA DEL AIRE MÁXIMA A 2 m':    'temp_max_aire',
        'GPRS - NIVEL':                         'nivel_inst_rio',
        'NIVEL INSTANTANEO':                    'nivel_inst_rio',
        'Nivel Instantaneo':                    'nivel_inst_rio',
        'Temp Min Aire 2 m':                    'temp_min_aire',
        'TEMPERATURA MÍNIMA DEL AIRE A 2 m':    'temp_min_aire',
        'GPRS - PRESIÓN ATMOSFÉRICA':           'pres_atmosferica',
        'PRESIÓN ATMOSFÉRICA':                  'pres_atmosferica',
        'Presión Atmosferica (1h)':             'pres_atmosferica'
        }) 


    df_final.to_csv('static/df_final.csv', index=False) 

    #Obtener última fecha obtenida en el df
    last_day = df_final.iloc[0]['fechaobservacion'].date()
    flag_day = last_day.replace(day = last_day.day - 1)
    flag_month = last_day.replace(month = last_day.month - 1)

    df_hist_data = df_final[(df_final['fechaobservacion'].dt.date < flag_day)]
    df_new = df_final[(df_final['fechaobservacion'].dt.date >= flag_day)]



    # Definir los items sobre las cuales se realizaran las mediciones
    measure_var = [
        'nivel_max_rio',  
        'humedad_aire',
        'vel_viento',
        'temperatura',
        'precipitacion',
        'nivel_min_rio',
        'dir_viento',
        'temp_max_aire',
        'nivel_inst_rio',
        'temp_min_aire',
        'pres_atmosferica'
    ]



    def obtain_processed_data(df_final_data):

        # Crear nuevo DF para incluir mediciones por 'codigoestacion'
        var_new_df = measure_var + ['codigoestacion']
        df_variation = pd.DataFrame(columns = var_new_df)

        # Recorrer todas las variables de medición y asignar a cada una de ellas un valor de variación
        for var in measure_var:

            columns_avg = ['descripcionsensor','fechaobservacion','valorobservado','codigoestacion']
            # Obtener los promedios del día y de los días anteriores a hoy agrupados por 'codigoestacion'
            df_data_station = return_avg(df_final_data.loc[:,columns_avg], var) # Solo analizar las columnas de columns_avg
            data_today, data_aft_today = df_data_station['vo_today'], df_data_station['vo_bef_today']
            df_data_station['variation'] = 0 if data_aft_today.empty else (data_today - data_aft_today) / data_aft_today

            #df_data_station.to_csv(f'df_data {var}.csv', index=False) 


            '''Para cada uno de los códigos de estación, se calcula la difrencia entre los valores observados el día actual y
            los valores observados en días anteriores, para cada una de las varaibles medidas'''

            for codstation in df_final_data['codigoestacion'].unique():
                        
                val_variation = 0

                if codstation in df_data_station['codigoestacion'].values:

                    val_variation = round(df_data_station.loc[df_data_station['codigoestacion'] == codstation, 'variation'].iloc[0],3)
                    
                    #Asegurar que el valor máximo de probabilidad sea del 100%, siendo este el más alto
                    if not(-1 < val_variation < 1):
                        val_variation = -1 if val_variation < 0 else 1
                    
                df_variation = fill_table(codstation, df_variation, var, val_variation)


        # Obtener Correlación agrupada por códigos de estaciones, para los diferentes pares de variables de medición

        corr_station = {}

        for station in df_variation['codigoestacion']:
            corr_variables = {}
            correlation_return = 0
            for i in range(len(measure_var)):
                for j in range(len(measure_var)):

                    if i != j:                
                        # Retorna la correlación
                        correlation_return = find_corr(df_final_data, measure_var[i], measure_var[j], station)
                    
                    if correlation_return != 0:
                        corr_variables[measure_var[i] + measure_var[j]] = round(correlation_return, 3)
            if corr_variables:
                '''El diccionario obtenido muestra todas las estaciones que obtuvieron datos con sus respectivas
                parejas de par de variables de medición y el valor de su correlación'''            
                corr_station[station] = corr_variables
        
        return df_variation, corr_station

    

    # Obtener datos historicos procesados
    df_hist, dic_corr_hist = obtain_processed_data(df_hist_data)


    '''De acuerdo con el análisis de causas y efectos, se obtiene un valor para cada uno de los delitos ambientales
    propuestos para seguimiento y se incluyen en el df_variation, con el nombre del delito y un valor que indica el nivel
    de posible presencia de cada uno de ellos, en cada uno de los municipios.'''
    df_historical_data = environment_crimes(df_hist, dic_corr_hist)

    # Obtener datos nuevos procesados
    df_new_data, dic_corr_new = obtain_processed_data(df_new)

    new_columns_corr = []
    for i, j in itertools.combinations(range(len(measure_var)), 2):
        new_columns_corr.append(measure_var[i] + measure_var[j]) 

    df_historical_data = insert_correl(df_historical_data, dic_corr_hist, new_columns_corr)
    df_new_data = insert_correl(df_new_data, dic_corr_new, new_columns_corr)


    df_new_data.to_csv('static/df_new_data.csv', index=False) 
    df_historical_data.to_csv('static/df_historical_data.csv', index=False) 

    df_predictions = train_predict(df_historical_data, df_new_data, measure_var, new_columns_corr)

    # Incluir en el df latitud y longitud
    for i in df_predictions['codigoestacion'].unique():
        df_predictions.loc[df_predictions['codigoestacion'] == i, 'latitud'] = df_final.loc[df_final['codigoestacion'] == i, 'latitud'].iloc[0]
        df_predictions.loc[df_predictions['codigoestacion'] == i, 'longitud'] = df_final.loc[df_final['codigoestacion'] == i, 'longitud'].iloc[0]
        df_predictions.loc[df_predictions['codigoestacion'] == i, 'municipio'] = df_final.loc[df_final['codigoestacion'] == i, 'municipio'].iloc[0]


    
    return df_predictions

'''Presentar de manera gráfica en un mapa, cada uno de los municipios con el nivel obtenido para cada uno de 
    los delitos. Por el momento, se omitieron los municipios sin datos obtenidos durante el proceso.'''
def create_map():

    df_predictions = pd.read_csv('static/df_predictions.csv')

    columns_level = [
        'Level Environment Pollution', 
        'Level Ecocidios', 
        'Level Illicit Use', 
        'Level Deforestation'
    ]


    # Crear un mapa centrado en la región de Cundinamarca y Boyacá
    mapa = folium.Map(location=[5.0, -74.0], zoom_start = 10)

    # Definir colores para diferentes rangos de temperatura
    color_rojo = '#FF0000'  # Temperaturas más altas
    color_yellow = '#f27600'  # Rango intermedio
    color_verde = '#008000'  # Temperaturas más bajas

    # Crear un grupo de marcadores
    marker_cluster = MarkerCluster().add_to(mapa)

    # Iterar sobre los datos y agregar marcadores al grupo con colores basados en las columnas de nivel
    for _, row in df_predictions.iterrows():
        
        municipio = row['municipio']
        
        for i in columns_level:

            if row[i] != 0:    
                descripcion = f"{i}: {row[i]}%" if row[i] > 0 else f"{i}: % de ocurrencia nulo"
                
                if row[i] > 20:
                    color = color_rojo
                    color_ico = 'red'
                elif row[i] > 10:
                    color = color_yellow
                    color_ico = 'orange'
                else:
                    color = color_verde
                    color_ico = 'green'

                

                popup_html = f"""
                <div style="background-color: {color}; color: #ffffff; border-radius: 5px; padding: 10px;">
                    <h4>{i}</h4>
                    <h6>{municipio}<h6>
                    <p>{descripcion}</p>
                </div>
                """

                marcador = folium.Marker(location=[row['latitud'], row['longitud']], popup=folium.Popup(popup_html, max_width=300),
                                        icon=folium.Icon(color = color_ico, icon = 'leaf'))

                # Agregar el marcador al grupo
                marcador.add_to(marker_cluster)

        # Guardar el mapa como un archivo HTML
        mapa.save('static/map.html')

    
#Distribución de Predicciones

def create_histogram():

    df_predictions = pd.read_csv('static/df_predictions.csv')

    plt.figure(figsize=(10, 6))
    plt.hist(df_predictions['Level Deforestation'], bins=20, alpha=0.5, label='Deforestación')
    plt.hist(df_predictions['Level Illicit Use'], bins=20, alpha=0.5, label='Uso Ilícito')
    plt.hist(df_predictions['Level Ecocidios'], bins=20, alpha=0.5, label='Ecocidios')
    plt.hist(df_predictions['Level Environment Pollution'], bins=20, alpha=0.5, label='Contaminación')
    plt.xlabel('Probabilidad (%)')
    plt.ylabel('Frecuencia')
    plt.legend()
    # Convert the Matplotlib figure to interactive HTML
    html_content = fig_to_html(plt.gcf())

    # Write the HTML content to a file (optional)
    with open('static/interactive_histogram.html', 'w') as f:
        f.write(html_content)


# Gráfico de barras con probabilidades por estación

def create_bar_chart():
    df_predictions = pd.read_csv('static/df_predictions.csv')

    # Configuración para la gráfica
    plt.figure(figsize=(10, 6))
    bar_width = 0.3
    opacity = 0.8

    # Posiciones de las barras en el eje x
    station_indices = range(len(df_predictions))

    # Graficar la deforestación
    bars1 = plt.bar(station_indices, df_predictions['Level Deforestation'], bar_width, alpha=opacity, color='b', label='Deforestación')

    # Graficar Uso Ilicito
    bars2 = plt.bar([i + bar_width for i in station_indices], df_predictions['Level Illicit Use'], bar_width, alpha=opacity, color='g', label='Uso Ilicito')

    # Graficar los ecocidios
    bars3 = plt.bar([i + 2 * bar_width for i in station_indices], df_predictions['Level Ecocidios'], bar_width, alpha=opacity, color='r', label='Ecocidios')

    # Graficar polución
    bars4 = plt.bar([i + 4 * bar_width for i in station_indices], df_predictions['Level Environment Pollution'], bar_width, alpha=opacity, color='y', label='Polución')

    # Etiquetas de estaciones en el eje x
    plt.xlabel('Municipio')
    plt.ylabel('Probabilidad/Valor')
   

    municipio_grap = []
    for _, row in df_predictions.iterrows():    
        municipio_grap.append(row['municipio'])

    plt.xticks([i + bar_width for i in station_indices], municipio_grap, rotation=80, color='white')
    plt.legend()

    # Añadir líneas verticales entre las barras
    for i in range(len(df_predictions)):
        plt.axvline(x=i + bar_width, color='gray', linestyle='--', linewidth=0.5)

    # Añadir etiquetas a las barras
    def add_labels(bars):
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.02, round(yval, 2), ha='center', va='bottom', fontsize=7)

    add_labels(bars1)
    add_labels(bars2)
    add_labels(bars3)
    add_labels(bars4)

    plt.tight_layout()

   
    # Convert the Matplotlib figure to interactive HTML
    html_content = fig_to_html(plt.gcf())

    # Write the HTML content to a file (optional)
    with open('static/interactive_bar_chart.html', 'w') as f:
        f.write(html_content)
