BODY_TYPE_DESCRIPTIONS = {
    "inverted_triangle": "Hombros más anchos que caderas. Cuerpo atlético.",
    "pear": "Caderas más anchas que hombros. Cuerpo en forma de pera.",
    "hourglass": "Hombros y caderas similares con cintura definida.",
    "rectangle": "Proporciones similares en hombros, cintura y caderas.",
    "unknown": "No se pudo determinar el tipo de cuerpo.",
}

RECOMMENDATIONS = {
    "inverted_triangle": {
        "tops": ["Camisas con corte recto", "Playeras sin hombros marcados", "Sudaderas oversized"],
        "bottoms": ["Pantalones con corte recto", "Jeans bootcut", "Pantalones anchos"],
        "avoid": ["Hombreras", "Tops con detalles en hombros", "Chaquetas estructuradas"],
    },
    "pear": {
        "tops": ["Blusas con detalles en hombros", "Tops con cuello en V", "Chaquetas estructuradas"],
        "bottoms": ["Pantalones de corte recto", "Jeans de tiro alto", "Pantalones oscuros"],
        "avoid": ["Pantalones con bolsillos laterales grandes", "Faldas con volumen en cadera"],
    },
    "hourglass": {
        "tops": ["Blusas ajustadas", "Tops con cintura marcada", "Camisas entalladas"],
        "bottoms": ["Jeans skinny", "Pantalones de tiro alto", "Faldas a la cintura"],
        "avoid": ["Ropa oversized", "Prendas sin forma definida"],
    },
    "rectangle": {
        "tops": ["Tops con capas", "Blusas con detalles en pecho", "Chaquetas con cinturón"],
        "bottoms": ["Pantalones con cintura elástica", "Jeans con detalles", "Faldas con volumen"],
        "avoid": ["Ropa completamente recta sin forma"],
    },
    "unknown": {
        "tops": [],
        "bottoms": [],
        "avoid": [],
    },
}


def get_recommendations(body_type: str, measurements: dict) -> dict:
    description = BODY_TYPE_DESCRIPTIONS.get(body_type, BODY_TYPE_DESCRIPTIONS["unknown"])
    recs = RECOMMENDATIONS.get(body_type, RECOMMENDATIONS["unknown"])

    size_estimate = estimate_size(measurements)

    return {
        "body_type": body_type,
        "description": description,
        "recommendations": recs,
        "size_estimate": size_estimate,
    }


def estimate_size(measurements: dict) -> dict:
    shoulder = measurements.get("shoulder_width", 0)
    sizes = {}

    if shoulder > 0:
        if shoulder < 38:
            sizes["top"] = "XS"
        elif shoulder < 42:
            sizes["top"] = "S"
        elif shoulder < 46:
            sizes["top"] = "M"
        elif shoulder < 50:
            sizes["top"] = "L"
        else:
            sizes["top"] = "XL"

    hip = measurements.get("hip_width", 0)
    if hip > 0:
        if hip < 34:
            sizes["bottom"] = "XS"
        elif hip < 38:
            sizes["bottom"] = "S"
        elif hip < 42:
            sizes["bottom"] = "M"
        elif hip < 46:
            sizes["bottom"] = "L"
        else:
            sizes["bottom"] = "XL"

    return sizes