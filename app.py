import streamlit as st
import numpy as np

# Título de la aplicación
st.title("Calculadora de Riesgo de Hipertensión")

# Descripción
st.write("Ingresa tus datos y presiona 'Calcular' para obtener tu probabilidad de riesgo.")

# Entrada de datos del usuario
edad = st.number_input("Edad", min_value=18, max_value=120, step=1, value=30)
peso = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, step=0.1, value=70.0)
altura = st.number_input("Altura (cm)", min_value=100.0, max_value=250.0, step=0.1, value=170.0)
presion_sistolica = st.number_input("Presión Arterial Sistólica (mmHg)", min_value=60, max_value=250, step=1, value=120)
fumador = st.selectbox("¿Fumas?", options=["No", "Sí"])
diabetes = st.selectbox("¿Tienes diabetes?", options=["No", "Sí"])
perimetro_abdominal = st.number_input("Perímetro Abdominal (cm)", min_value=50, max_value=150, step=1, value=90)

# Cálculo del IMC
imc = peso / ((altura / 100) ** 2)

# Mensaje informativo
st.write(f"Tu IMC calculado es: {imc:.2f}")

# Configuración de los coeficientes del modelo
coef_intercept = -5.6402540
coef_edad = 0.0536644
coef_imc = 0.0574671
coef_presion_sistolica = 0.0208382
coef_fumador = 0.6622481
coef_diabetes = -1.2706217
coef_perimetro_abdominal = 0.0007416

# Función para calcular la probabilidad de riesgo
def calcular_riesgo(edad, imc, presion_sistolica, fumador, diabetes, perimetro_abdominal):
    fumador_val = 1 if fumador == "Sí" else 0
    diabetes_val = 1 if diabetes == "Sí" else 0
    score = (coef_intercept
             + coef_edad * edad
             + coef_imc * imc
             + coef_presion_sistolica * presion_sistolica
             + coef_fumador * fumador_val
             + coef_diabetes * diabetes_val
             + coef_perimetro_abdominal * perimetro_abdominal)
    probabilidad = 1 / (1 + np.exp(-score))
    return probabilidad * 100  # Convertir a porcentaje

# Botón para calcular el riesgo
if st.button("Calcular"):
    riesgo = calcular_riesgo(edad, imc, presion_sistolica, fumador, diabetes, perimetro_abdominal)
    st.success(f"Tu probabilidad de riesgo de hipertensión es aproximadamente: {riesgo:.2f}%")

