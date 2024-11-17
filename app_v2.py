import streamlit as st
from firebase_admin import credentials, firestore, initialize_app, get_app, delete_app
import datetime

# Cargar las credenciales del archivo JSON
cred = credentials.Certificate("firebase_credentials.json")

# Inicializar Firebase solo si no está ya inicializado
try:
    firebase_app = get_app()
except ValueError:
    firebase_app = initialize_app(cred)

db = firestore.client()  # Conexión con Firestore
collection_name = "survey_data"  # Nombre de la colección en Firestore

# Función para obtener el próximo ID incremental
def get_next_id():
    docs = db.collection(collection_name).stream()
    count = sum(1 for _ in docs)  # Contar documentos
    return f"CX{count + 1:05d}"  # Formato CX00001, CX00002, etc.

# Función para guardar los datos en Firebase con ID personalizado
def save_to_firebase(data, document_id):
    db.collection(collection_name).document(document_id).set(data)

# Inicializar el estado de sesión para probabilidad
if "probabilidad" not in st.session_state:
    st.session_state.probabilidad = None
if "form_reset" not in st.session_state:
    st.session_state.form_reset = False

# Configuración de estilo CSS
st.markdown("""
    <style>
        .main {
            background-color: #f4f4f9;
            font-family: 'Arial', sans-serif;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #8B0000;
            font-family: 'Verdana', sans-serif;
            font-size: 30px;
        }
        .stButton button {
            background-color: #e38471;
            color: white;
            border-radius: 5px;
            padding: 10px;
        }
        .stButton button:hover {
            background-color: #A52A2A;
        }
    </style>
""", unsafe_allow_html=True)

# Título de la aplicación
st.title("Calculadora de Riesgo Cardiovascular")

# Formulario para recolectar datos
if st.session_state.form_reset:
    st.session_state.form_reset = False  # Reiniciar el estado para evitar persistencia

# Formulario para recolectar datos
with st.form("survey_form"):
    edad = st.number_input("Edad (años)", min_value=0, max_value=120, step=1, key="edad")
    peso = st.number_input("Peso (kg)", min_value=10.0, max_value=200.0, step=0.1, key="peso")
    altura = st.number_input("Altura (cm)", min_value=50.0, max_value=250.0, step=0.1, key="altura")
    fumador = st.radio("¿Es fumador?", options=["Sí", "No"], key="fumador")
    diabetes = st.radio("¿Tiene diabetes?", options=["Sí", "No"], key="diabetes")
    presion_sistolica = st.number_input("Presión sistólica (mmHg)", min_value=50, max_value=200, step=1, key="presion_sistolica")
    perimetro_abdominal = st.number_input("Perímetro abdominal (cm)", min_value=50.0, max_value=200.0, step=0.1, key="perimetro_abdominal")
    calcular = st.form_submit_button("Calcular riesgo")

# Cálculo del IMC
imc = peso / ((altura / 100) ** 2) if altura > 0 else 0

# Calcular el riesgo si se presiona el botón "Calcular riesgo"
if calcular:
    fumador_bin = 1 if fumador == "Sí" else 0
    diabetes_bin = 1 if diabetes == "Sí" else 0

    # Coeficientes del modelo recalibrado
    intercept = -8.1153447
    coef_edad = 0.0529949
    coef_imc = 0.0573427
    coef_presion_sistolica = 0.0206094
    coef_fumador = 0.6654545
    coef_diabetes = 1.7310607
    coef_perimetro_abdominal = 0.0002902

    # Cálculo del puntaje de riesgo
    riesgo = (
        intercept
        + coef_edad * edad
        + coef_imc * imc
        + coef_presion_sistolica * presion_sistolica
        + coef_fumador * fumador_bin
        + coef_diabetes * diabetes_bin
        + coef_perimetro_abdominal * perimetro_abdominal
    )
    st.session_state.probabilidad = 1 / (1 + 2.71828 ** (-riesgo))  # Guardar en el estado de sesión
    st.success(f"**Tu probabilidad de hipertensión es: {st.session_state.probabilidad:.2%}**")

# Mostrar el acuerdo de confidencialidad
st.markdown("""
**Acuerdo de confidencialidad**:
- La información recopilada será utilizada exclusivamente con fines de investigación y para mejorar la precisión de esta calculadora de riesgo de hipertensión.
- Sus datos serán anonimizados y protegidos bajo las normativas vigentes de confidencialidad.
- Al participar, usted contribuye a un proyecto orientado a mejorar la salud pública en el Perú y optimizar los modelos predictivos para nuestra población.

**Importante**:
La hipertensión es una enfermedad crónica con serias implicaciones para la salud. Este proyecto busca apoyar a su detección temprana y la prevención en poblaciones vulnerables.
""")

# Checkbox para aceptar los términos
acuerdo_aceptado = st.checkbox("Acepto participar y registrar mis datos para fines de investigación")

# Botón para registrar datos, habilitado solo si se aceptan los acuerdos
if acuerdo_aceptado:
    if st.button("Confirmar Registro"):
        if st.session_state.probabilidad is None:
            st.error("Por favor, calcula primero el riesgo antes de registrar los datos.")
        else:
            # Obtener el próximo ID incremental
            document_id = get_next_id()

            # Agregar la fecha y hora actuales
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
            hora_actual = datetime.datetime.now().strftime("%H:%M:%S")

            # Guardar los datos en Firebase
            user_data = {
                "edad": edad,
                "peso": peso,
                "altura": altura,
                "imc": imc,
                "fumador": fumador,
                "diabetes": diabetes,
                "presion_sistolica": presion_sistolica,
                "perimetro_abdominal": perimetro_abdominal,
                "probabilidad": st.session_state.probabilidad,
                "fecha": fecha_actual,
                "hora": hora_actual,
            }
            save_to_firebase(user_data, document_id)
            st.success(f"Tus datos han sido registrados exitosamente con el ID {document_id}.")
            st.info("Gracias por tu participación y contribución. Esta información será clave para mejorar la precisión del modelo y ayudar en la prevención de la hipertensión en poblaciones vulnerables.")
            
            # Activar limpieza
            st.session_state.datos_limpiar = True
