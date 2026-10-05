import numpy as np
import pandas as pd

def find_values(
        keyword : str,
        lists: pd.Series
) -> list:
    """
    Encuentra el valor de una característica de cada lista de características de cada inmueble.

    :param keyword: palabra referente a la característica, i.e, baño, habitación.... (en singular siempre)
    :param lists: listas de características de los inmuebles
    :returns values: valores para la característica
    """
    values = []
    for list in lists:
        dummy = 0
        for feature in list:
            to_find = feature.lower().split()
            if keyword in to_find:
                try:
                    value = int(feature.split()[0].strip())
                    values.append(value)
                    dummy += 1
                    break
                except:
                    value = 0
                    values.append(0)
                    dummy += 1
                    break
        if dummy == 0:
            values.append(0)
    return np.array(values)

def find_binary(
    keyword : str,
    lists: pd.Series   
) -> np.ndarray:
    values = []
    for list in lists:
        dummy = 0
        for feature in list:
            to_find = feature.lower().split()
            if keyword in to_find:
                value = 0 if "sin" in to_find or "no" in to_find else 1
                values.append(value)
                dummy += 1
                break
            else:
                continue
        if dummy == 0:
            values.append(0)
    return np.array(values)

def clean_df(
        json_path : str,
        save : bool = True
) -> pd.DataFrame:
    """
    Lee el archivo json de los datos en crudo, y devuelve el dataframe limpio

    :param json_path: ruta del archivo
    :returns clean df: datos limpios
    """
    df = pd.read_json(json_path)

    # Como en algunas características hay plural y singular, tenemos en cuenta las dos opciones
    m2 = find_values("m²", df["caracteristicas"])
    habs = find_values("habitación", df["caracteristicas"]) + find_values("habitaciones", df["caracteristicas"])
    baños = find_values("baño", df["caracteristicas"]) + find_values("baños", df["caracteristicas"])
    ascensor = find_binary("ascensor", df["caracteristicas"])
    garaje = find_binary("garaje", df["caracteristicas"])
    calefa = find_binary("calefacción", df["caracteristicas"])

    # Asignamos las columnas al dataframe
    df["m²"] = m2
    df["habitaciones"] = habs
    df["baños"] = baños
    df["ascensor"] = ascensor
    df["garaje"] = garaje
    df["calefacción"] = calefa

    # Se elimina la columna que contiene las listas
    df.drop(columns = "caracteristicas", inplace = True)

    # Se obtuvo 0 m² para solo 2 inmuebles, así que se eliminan
    df.drop(df.loc[df["m²"] == 0].index, axis = 0, inplace = True)
    if save == True:
        df.to_csv(json_path[11:-5] + "_clean.csv")
    return df