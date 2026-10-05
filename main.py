from extract import *
from transform import *
import argparse

parser = argparse.ArgumentParser(
    prog = "ETL Idealista",
    description = "Construcción del ETL para inmuebles de Idealista mediante Web Scrapping, junto a modelo de ML."
)
parser.add_argument("-m", "--mode", type = str, choices = ["E", "T", "M"], help = "Modo de uso")
parser.add_argument("-s", "--st", type = int, default = 4, help = "Tiempo de espera en la extracción")
parser.add_argument("-v", "--verbose", type = bool, default = True, help = "Proporcionar información")
parser.add_argument("-r", "--rawpath", type = str, default = "./data/raw.json", help = "Ruta en la que guardar/cargar los datos sin procesar")
parser.add_argument("-c", "--cleanpath", type = str, default = "./data/clean.csv", help = "Ruta en la que guardar/cargar los datos procesados")

args = parser.parse_args()

if __name__ == "__main__":
    if args.mode == "E":
        ids = extract_IDs(
            sleep_time = args.st,    
            verbose = args.verbose
        )

        cs = extract_features(
            ids = ids,
            sleep_time = args.st,
            json_path = args.rawpath
        )
    
    if args.mode == "T":
        df = pd.read_json(args.rawpath)
        habs = find_values("habitación", df["caracteristicas"]) + find_values("habitaciones", df["caracteristicas"])
        baños = find_values("baño", df["caracteristicas"]) + find_values("baños", df["caracteristicas"])
        m2 = find_values("m²", df["caracteristicas"])
        ascensor = find_binary("ascensor", df["caracteristicas"])
        garaje = find_binary("garaje", df["caracteristicas"])
        calefa = find_binary("calefacción", df["caracteristicas"])

        df["m²"] = m2
        df["habitaciones"] = habs
        df["baños"] = baños
        df["ascensor"] = ascensor
        df["garaje"] = garaje
        df["calefacción"] = calefa
        df.drop(columns = "caracteristicas", inplace = True)
        df.drop(df.loc[df["m²"] == 0].index, axis = 0, inplace = True)

        df.to_csv(args.cleanpath)