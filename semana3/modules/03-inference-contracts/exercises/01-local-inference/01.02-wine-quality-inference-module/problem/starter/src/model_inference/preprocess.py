"""TODO: transformación de una muestra validada en el vector del modelo."""
#Como preparo los datos para que los entienda el modelo?
from dataclasses import dataclass

from model_inference.contracts import WineQualityRequest
PREPROCESSING_VERSION = "wine-red-features-v1"

# Este contrato se entrega ya decidido: no cambies ni los nombres ni el orden.
FEATURE_NAMES = (
    "fixed_acidity",
    "volatile_acidity",
    "citric_acid",
    "residual_sugar",
    "chlorides",
    "free_sulfur_dioxide",
    "total_sulfur_dioxide",
    "density",
    "ph",
    "sulphates",
    "alcohol",
)

# Implementa WineFeatures y preprocess_wine_request(). El orden anterior debe
# coincidir con el artefacto, no con un orden arbitrario del CSV.

@dataclass(frozen=True, slots=True) #Por que los datos son internos y ya validados
class WineFeatures:
    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    ph: float
    sulphates: float
    alcohol: float

    def as_vector(self)-> list[float]: #self es WineFeatures en este caso
        #para pasar de una estructura con nombres a una lista ordenada
        #Esto se llama en inference.py
         return [getattr(self, name) for name in FEATURE_NAMES]
     
        
def preprocess_wine_request(
    request: WineQualityRequest,
) -> WineFeatures:
    return WineFeatures(
        fixed_acidity=request.fixed_acidity,
        volatile_acidity=request.volatile_acidity,
        citric_acid=request.citric_acid,
        residual_sugar=request.residual_sugar,
        chlorides=request.chlorides,
        free_sulfur_dioxide=request.free_sulfur_dioxide,
        total_sulfur_dioxide=request.total_sulfur_dioxide,
        density=request.density,
        ph=request.ph,
        sulphates=request.sulphates,
        alcohol=request.alcohol,
    )