import pandas as pd
import requests
import zipfile


def import_cheptel():
    url_cheptel = "https://www.insee.fr/fr/statistiques/fichier/2012795/TCRD_073.xlsx"

    cheptel2022 = pd.read_excel(url_cheptel, header=3, na_values="nd")
    type_cheptel = cheptel2022.columns[~cheptel2022.columns.str.startswith("Unnamed")]
    cheptel2022.loc[:, type_cheptel] = cheptel2022.loc[:, type_cheptel].mul(1000)
    cheptel2022 = cheptel2022.rename(
        {
            "Unnamed: 0": "code",
            "Unnamed: 1": "departement",
            "Volailles gallus": "Volailles",
        },
        axis="columns",
    )
    type_cheptel = type_cheptel.str.replace(" gallus", "")
    return cheptel2022, type_cheptel


def import_population():
    # URL of the zip file
    url_population = "https://www.insee.fr/fr/statistiques/fichier/7739582/ensemble.zip"

    # Local path to save the downloaded zip file
    zip_path = "ensemble.zip"

    # Download the file
    response = requests.get(url_population)
    with open(zip_path, "wb") as file:
        file.write(response.content)

    # Unzip the file
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall("unzipped_files")

    population2021 = pd.read_csv("./unzipped_files/donnees_departements.csv", sep=";")

    return population2021


def create_dataset(cheptel2022=None, population2021=None, type_cheptel=None):
    if cheptel2022 is None or type_cheptel is None:
        cheptel2022, type_cheptel = import_cheptel()
    if population2021 is None:
        population2021 = import_population()

    data_departement = cheptel2022.merge(
        population2021, right_on="DEP", left_on="code"
    ).drop(["departement", "DEP"], axis="columns")

    type_cheptel = type_cheptel.str.replace(" Gallus", "")
    data_departement["ratio_" + type_cheptel] = data_departement.loc[
        :, type_cheptel
    ].div(data_departement["PTOT"], axis=0)
    data_departement["more_" + type_cheptel] = (
        data_departement["ratio_" + type_cheptel] > 1
    )
    return data_departement


cheptel2022, type_cheptel = import_cheptel()
population2021 = import_population()
create_dataset(
    cheptel2022=cheptel2022, population2021=population2021, type_cheptel=type_cheptel
)
