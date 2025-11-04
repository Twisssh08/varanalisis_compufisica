import pandas as pd
import streamlit as st
from PIL import Image
import numpy as np
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Monitoreo de Nivel de Agua - Tanque Principal",
    page_icon="💧",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Título y descripción general
st.title('💧 Monitoreo y Análisis del Nivel de Agua en el Tanque Principal')
st.markdown("""
    Esta aplicación permite visualizar y analizar los datos capturados por un potenciómetro
    que mide el nivel de agua en un tanque de almacenamiento.
""")

# Ubicación del sensor (ejemplo: Universidad EAFIT)
ubicacion_sensor = pd.DataFrame({
    'lat': [6.2006],
    'lon': [-75.5783],
    'location': ['Universidad EAFIT - Tanque Principal']
})

st.subheader("📍 Ubicación del Sensor - Universidad EAFIT")
st.map(ubicacion_sensor, zoom=15)

# Carga del archivo CSV
uploaded_file = st.file_uploader('Seleccione el archivo CSV con los datos del potenciómetro', type=['csv'])

if uploaded_file is not None:
    try:
        # Cargar y procesar los datos
        df1 = pd.read_csv(uploaded_file)
        
        # Renombrar columna a 'nivel_agua'
        if 'Time' in df1.columns:
            other_columns = [col for col in df1.columns if col != 'Time']
            if len(other_columns) > 0:
                df1 = df1.rename(columns={other_columns[0]: 'nivel_agua'})
        else:
            df1 = df1.rename(columns={df1.columns[0]: 'nivel_agua'})
        
        # Procesar columna de tiempo si existe
        if 'Time' in df1.columns:
            df1['Time'] = pd.to_datetime(df1['Time'])
            df1 = df1.set_index('Time')

        # Crear pestañas
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Visualización", "📊 Estadísticas", "🔍 Filtros", "🗺️ Información del Sistema"])

        # --- TAB 1: Visualización ---
        with tab1:
            st.subheader('Visualización del Nivel de Agua')
            
            chart_type = st.selectbox(
                "Seleccione el tipo de gráfico para visualizar el nivel de agua",
                ["Línea", "Área", "Barra"]
            )
            
            if chart_type == "Línea":
                st.line_chart(df1["nivel_agua"])
            elif chart_type == "Área":
                st.area_chart(df1["nivel_agua"])
            else:
                st.bar_chart(df1["nivel_agua"])

            if st.checkbox('Mostrar datos originales'):
                st.write(df1)

        # --- TAB 2: Estadísticas ---
        with tab2:
            st.subheader('Análisis Estadístico del Nivel de Agua')
            
            stats_df = df1["nivel_agua"].describe()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(stats_df)
            
            with col2:
                st.metric("Nivel Promedio", f"{stats_df['mean']:.2f} unidades")
                st.metric("Nivel Máximo", f"{stats_df['max']:.2f} unidades")
                st.metric("Nivel Mínimo", f"{stats_df['min']:.2f} unidades")
                st.metric("Desviación Estándar", f"{stats_df['std']:.2f} unidades")

        # --- TAB 3: Filtros ---
        with tab3:
            st.subheader('Filtrado de Datos de Nivel de Agua')
            
            min_value = float(df1["nivel_agua"].min())
            max_value = float(df1["nivel_agua"].max())
            mean_value = float(df1["nivel_agua"].mean())
            
            if min_value == max_value:
                st.warning(f"⚠️ Todos los valores registrados son iguales: {min_value:.2f}")
                st.info("No es posible aplicar filtros cuando no hay variación en los datos.")
                st.dataframe(df1)
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    min_val = st.slider(
                        'Nivel mínimo (filtrar valores por encima de este)',
                        min_value,
                        max_value,
                        mean_value,
                        key="min_val"
                    )
                    filtrado_df_min = df1[df1["nivel_agua"] > min_val]
                    st.write(f"Registros con nivel de agua superior a {min_val:.2f}:")
                    st.dataframe(filtrado_df_min)
                    
                with col2:
                    max_val = st.slider(
                        'Nivel máximo (filtrar valores por debajo de este)',
                        min_value,
                        max_value,
                        mean_value,
                        key="max_val"
                    )
                    filtrado_df_max = df1[df1["nivel_agua"] < max_val]
                    st.write(f"Registros con nivel de agua inferior a {max_val:.2f}:")
                    st.dataframe(filtrado_df_max)

                if st.button('Descargar datos filtrados'):
                    csv = filtrado_df_min.to_csv().encode('utf-8')
                    st.download_button(
                        label="Descargar CSV",
                        data=csv,
                        file_name='nivel_agua_filtrado.csv',
                        mime='text/csv',
                    )

        # --- TAB 4: Información del Sistema ---
        with tab4:
            st.subheader("Información del Sistema de Medición")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Ubicación del Sensor")
                st.write("**Universidad EAFIT - Tanque Principal**")
                st.write("- Latitud: 6.2006")
                st.write("- Longitud: -75.5783")
                st.write("- Altitud: ~1,495 msnm")
            
            with col2:
                st.write("### Detalles del Sistema")
                st.write("- Tipo de Sensor: Potenciómetro (lectura analógica)")
                st.write("- Variable medida: Nivel de agua del tanque")
                st.write("- Unidad de medida: Escala analógica o centímetros (según calibración)")
                st.write("- Frecuencia de medición: Configurable en el ESP32")
                st.write("- Procesador: ESP32")

    except Exception as e:
        st.error(f'Error al procesar el archivo: {str(e)}')
        st.info('Verifique que el archivo CSV tenga al menos una columna con datos válidos.')
else:
    st.warning('Por favor, cargue un archivo CSV con los datos del nivel de agua.')

# Footer
st.markdown("""
    ---
    Desarrollado para el monitoreo de nivel de agua en sistemas de almacenamiento.  
    Ubicación: Universidad EAFIT, Medellín, Colombia
""")
