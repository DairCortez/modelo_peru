import numpy as np
import streamlit as st

# Coeficientes del modelo recalibrado
intercept = -8.1153447
coef_age = 0.0529949
coef_imc = 0.0573427
coef_sbp = 0.0206094
coef_smoke = 0.6654545
coef_diabetes = 1.7310607
coef_abdominal = 0.0002902

# Función para calcular el riesgo de hipertensión
def calculate_hypertension_risk(age, weight, height, sbp, smoker, diabetes, abdominal):
    # Calcular el IMC
    imc = weight / (height / 100) ** 2
    
    # Calcular el puntaje de riesgo
    risk_score = (
        intercept +
        (coef_age * age) +
        (coef_imc * imc) +
        (coef_sbp * sbp) +
        (coef_smoke * smoker) +
        (coef_diabetes * diabetes) +
        (coef_abdominal * abdominal)
    )
    
    # Convertir el puntaje de riesgo a probabilidad
    risk_probability = 1 / (1 + np.exp(-risk_score))
    return risk_probability * 100  # Convertir a porcentaje

# Interfaz de usuario con Streamlit
st.title("Calculadora de Riesgo de Hipertensión")
st.write("Ingrese los datos requeridos para calcular el riesgo:")

# Entradas del usuario
age = st.number_input("Edad", min_value=1, max_value=120, value=30)
weight = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=70.0)
height = st.number_input("Altura (cm)", min_value=120.0, max_value=210.0, value=170.0)
sbp = st.number_input("Presión Sistólica (mmHg)", min_value=60.0, max_value=180.0, value=120.0)
smoker = st.selectbox("¿Es fumador?", ["No", "Sí"])
diabetes = st.selectbox("¿Tiene diabetes?", ["No", "Sí"])
abdominal = st.number_input("Perímetro Abdominal (cm)", min_value=60.0, max_value=150.0, value=90.0)

# Conversión de opciones seleccionadas a valores numéricos
smoker_value = 1 if smoker == "Sí" else 0
diabetes_value = 1 if diabetes == "Sí" else 0

# Botón para calcular el riesgo
if st.button("Calcular Riesgo"):
    risk = calculate_hypertension_risk(age, weight, height, sbp, smoker_value, diabetes_value, abdominal)
    st.write(f"El riesgo estimado de hipertensión es: {risk:.2f}%")
