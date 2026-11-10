
import os

import requests

API_KEY = os.environ["AEMET_API_KEY"]

url = (
    "https://opendata.aemet.es/opendata/api/"
    "valores/climatologicos/inventarioestaciones/todasestaciones/"
)

# Primera petición: solicitar la URL de los datos.
respuesta = requests.get(
    url,
    params={"api_key": API_KEY},
    timeout=30,
)
respuesta.raise_for_status()

contenido = respuesta.json()
url_datos = contenido["datos"]

# Segunda petición: descargar el inventario de estaciones.
respuesta_datos = requests.get(url_datos, timeout=30)
respuesta_datos.raise_for_status()

estaciones = respuesta_datos.json()

# Localizar la estación que pide el enunciado.
for estacion in estaciones:
    if "MADRID, CIUDAD UNIVERSITARIA" in estacion["nombre"].upper():
        print("Estación:", estacion["nombre"])
        print("Indicativo:", estacion["indicativo"])


# Consultar las climatologías diarias de octubre de 2019.
indicativo = "3194U"

url_climatologia = (
    "https://opendata.aemet.es/opendata/api/"
    "valores/climatologicos/diarios/datos/"
    "fechaini/2019-10-01T00:00:00UTC/"
    "fechafin/2019-10-30T23:59:59UTC/"
    f"estacion/{indicativo}"
)

# Primera petición: obtener la URL de descarga.
respuesta = requests.get(
    url_climatologia,
    params={"api_key": API_KEY},
    timeout=30,
)
respuesta.raise_for_status()

url_datos = respuesta.json()["datos"]

# Segunda petición: recuperar los datos climatológicos.
respuesta_datos = requests.get(url_datos, timeout=30)
respuesta_datos.raise_for_status()

datos_diarios = respuesta_datos.json()

print("\nClimatología diaria de octubre de 2019:")
print("Número de registros:", len(datos_diarios))

for dia in datos_diarios:
    print(
        "Fecha:", dia.get("fecha"),
        "| Temperatura media:", dia.get("tmed", "Sin dato"),
        "| Precipitación:", dia.get("prec", "Sin dato"),
    )