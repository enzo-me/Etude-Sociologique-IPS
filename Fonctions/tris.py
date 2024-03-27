import pandas as pd
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def float_to_string(cell):
    if type(cell) == float:
        cell = 'rien'
    return cell

def tri_questionnaire(questionnaire):
    académie = "Sélectionnez l'académie dans laquelle vous exercez. "
    etablissements = "Renseignez le nom de votre lycée et la ville dans laquelle il se situe.  Si vous exercez dans plusieurs établissements, merci de ne renseigner que celui dans lequel vous effectuez la majorité de votre service. "

    questionnaire[académie] = questionnaire[académie].str.lower()
    questionnaire[académie] = questionnaire[académie].str.replace("académie de ", "")
    questionnaire[académie] = questionnaire[académie].str.replace("académie d'", "")

    a_remplacer_par_vide = ["général et technologique ","Lycée ","général ","technologique ","privé ","polyvalent ","professionnel ","LPO ","- ","à "]
    for remplacement in a_remplacer_par_vide:
        questionnaire[etablissements] = questionnaire[etablissements].str.replace(remplacement, "")

    a_remplacer_par_espace = [", ","-",'\n','  ']
    for remplacement in a_remplacer_par_espace:
        questionnaire[etablissements] = questionnaire[etablissements].str.replace(remplacement, "  ")

    questionnaire[etablissements] = questionnaire[etablissements].str.lower()
    questionnaire[etablissements] = questionnaire[etablissements].apply(lambda x: re.sub(r'\d', '', str(x)))
    questionnaire = questionnaire.dropna(subset=[etablissements])

    questionnaire = questionnaire[questionnaire["Sélectionnez l'académie dans laquelle vous exercez. "].notna()]  
    questionnaire.reset_index(drop=True, inplace=True)

    return questionnaire

def tri_uai(uai):
    conditions_denomination = ['COLLEGE','COLLEGE PRIVE','ECOLE ELEMENTAIRE PUBLIQUE','ECOLE PRIMAIRE PUBLIQUE','SEGPA','LYCEE PROFESSIONNEL PRIVE','CENTRE DES JEUNES ADOLESCENTS','ECOLE MATERNELLE PUBLIQUE','ECOLE PRIMAIRE PRIVEE','GOD','CETAD','MAISON FAMILIALE RURALE','GROUPE SCOLAIRE PRIMAIRE','CENTRE SCOLAIRE PRIMAIRE','LYCEE PROFESSIONNEL','ECOLE PRIMAIRE','ECOLE MATERNELLE PRIVEE','ANIMATION','GROUPE SCOLAIRE','ECOLE PRIMAIRE PRIVEE SAINT JEAN-BAPTISTE','ECOLE PRIMAIRE  PRIVEE','ECOLE ELEMENTAIRE PRIVEE','LEGT AGRICOLE','LYCEE TECHNOLOGIQUE PRIVE','INSTITUT AGRICOLE PRIVE','SEGPA PRIVEE','SECTION ENSEIGNT PROFESSIONNEL','ETABLISSEMENT EXPERIMENTAL','SECTION ENSEIGT PROFES PRIVEE']
    for condition in conditions_denomination:
        uai = uai.drop(uai[uai["Dénomination principale"] == condition].index)

    conditions_academie = ['Polynésie Française','Nouvelle Calédonie','Mayotte','Martinique']
    for condition in conditions_academie:
        uai = uai.drop(uai[uai["Académie"] == condition].index)

    conditions_nature = ['COLLEGE','ECOLE DE NIVEAU ELEMENTAIRE','LYCEE PROFESSIONNEL','ECOLE SANS EFFECTIFS PERMANENTS']
    for condition in conditions_nature:
        uai = uai.drop(uai[uai["Nature"] == condition].index)

    colonnes_minuscules = ["Localite d'acheminement","Patronyme uai","Académie"]
    for colonne in colonnes_minuscules:
        uai[colonne] = uai[colonne].str.lower()
    
    uai = uai.dropna(subset=["Appellation officielle"])

    uai['Patronyme uai'] = uai['Patronyme uai'].apply(float_to_string)

    return uai

def tri_final(dataframe):
    dataframe = dataframe.replace({"Oui": 1, "Non": 0})


    column_name0 = "Renseignez votre parcours académique avant d’exercer dans l’éducation nationale. Plusieurs cases peuvent être sélectionnées, merci d’être le plus précis.e possible. [Autre]"
    dataframe = dataframe[dataframe[column_name0].isnull()]

    choix_possibles = ['Non imposé',"Pas pour le moment mais je souhaite le faire d'ici quelques années",'Non, par choix','Autre']
    for choix in choix_possibles:
        dataframe = dataframe.drop(dataframe[dataframe["Enseignez-vous la spécialité histoire-géographie, géopolitique, sciences politiques ?"] == choix].index)

    remplacements0 = {"Non et je souhaite demander une formation": 0, "Non et je ne souhaite pas demander de formation": 0, "Oui, avant que je l’enseigne et je n'ai pas demandé cette formation" : 1, "Oui, après avoir commencé à l'enseigner et je n'ai pas demandé cette formation" : 1, "Oui, avant que je l’enseigne et j’ai demandé cette formation" : 1, "Oui, avant que je l’enseigne et je n'ai demandé cette formation" : 1, "Oui, après avoir commencé à l'enseigner et j’ai demandé cette formation" : 1}
    dataframe['Avez-vous reçu une formation à l’enseignement de spécialité ?'] = dataframe['Avez-vous reçu une formation à l’enseignement de spécialité ?'].replace(remplacements0)

    condition7 = (dataframe["Avez-vous reçu une formation à l’enseignement de spécialité ?"] == 'Autre')
    dataframe = dataframe.drop(dataframe[condition7].index)

    condition0 = (dataframe["Vous vous identifiez comme : "] == 'Je ne souhaite pas partager cette information')
    dataframe = dataframe.drop(dataframe[condition0].index)

    dataframe['Sexe_Homme'] = dataframe['Vous vous identifiez comme : '].apply(lambda x: 1 if x == 'Un homme' else 0)

    dataframe['Sexe_Femme'] = dataframe['Vous vous identifiez comme : '].apply(lambda x: 1 if x == 'Une femme' else 0)

    condition10 = (dataframe["Quelles méthodologies mettez-vous principalement en œuvre dans votre enseignement de la spécialité ?  [Autres, merci de préciser.]"] == 'Oui')
    dataframe = dataframe.drop(dataframe[condition10].index)

    condition11= (dataframe["Parmi les thèmes de spécialité en classe de Première, quels sont les thèmes les plus appréciés par vos élèves ? [Je n'enseigne pas la spécialité HGGSP en classe de première.]"] == 'Oui')
    dataframe = dataframe.drop(dataframe[condition11].index)

    condition12 = (dataframe["Parmi les thèmes de spécialité en Terminale, quels sont les thèmes les plus appréciés par vos élèves ? [Je n'enseigne pas la spécialité HGGSP en classe de terminale.]"] == 'Oui')
    dataframe = dataframe.drop(dataframe[condition12].index)

    dataframe['Renseignez votre âge. '] = dataframe['Renseignez votre âge. '].str.replace(r'(\d+)\s*ans', r'\1', regex=True)

    colonnes_a_supprimer = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 28, 29, 30, 31, 32, 34, 35, 36, 41, 76, 77, 78, 79, 80, 81, 82, 83, 94, 95, 108, 109, 110]
    dataframe = dataframe.drop(dataframe.columns[colonnes_a_supprimer], axis=1)
    dataframe = dataframe.reset_index(drop=True)
    colonnes_a_supprimer = [44,46,48,50,52,53,54]
    dataframe = dataframe.drop(dataframe.columns[colonnes_a_supprimer], axis=1)
    colonnes_a_supprimer = [52,62]
    dataframe = dataframe.drop(dataframe.columns[colonnes_a_supprimer], axis=1)


    condition999 = (dataframe["IPS voie GT"] == '0170440L')
    dataframe = dataframe.drop(dataframe[condition999].index)
    dataframe = dataframe.dropna(subset=["IPS voie GT"])
    dataframe = dataframe.dropna(subset=['Renseignez votre âge.\xa0'])

    colonnes_a_vider = ['Avez-vous reçu une formation à l’enseignement de spécialité\xa0?','A ce jour, vous considérez vous comme formé.e à la géopolitique et à son enseignement ? [Oui, grâce à ma formation initiale.]','A ce jour, vous considérez vous comme formé.e à la géopolitique et à son enseignement ? [Oui, grâce à la formation continue reçue.]',
                        "A ce jour, vous considérez vous comme formé.e à la géopolitique et à son enseignement ? [Oui, par mon travail d'auto-formation]",'A ce jour, vous considérez vous comme formé.e à la géopolitique et à son enseignement ? [Non, pas assez]',
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes le plus à l'aise à enseigner : [Thème 1 première - Comprendre un régime politique : la démocratie]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes le plus à l'aise à enseigner : [Thème 2 première - Analyser les dynamiques des puissances internationales]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes le plus à l'aise à enseigner : [Thème 3 première - Étudier les divisions politiques du monde : les frontières]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes le plus à l'aise à enseigner : [Thème 4 première - S’informer : un regard critique sur les sources et modes de communication]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes le plus à l'aise à enseigner : [Thème 5 première - Analyser les relations entre États et religions]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes le plus à l'aise à enseigner : [Thème 1 terminale - De nouveaux espaces de conquête]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes le plus à l'aise à enseigner : [Thème 2 terminale - Faire la guerre, faire la paix : formes de conflits et modes de résolution]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes le plus à l'aise à enseigner : [Thème 3 terminale - Histoire et mémoires]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes le plus à l'aise à enseigner : [Thème 4 terminale - Identifier, protéger et valoriser le patrimoine : enjeux géopolitiques]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes le plus à l'aise à enseigner : [Thème 5 terminale - L’environnement, entre exploitation et protection : un enjeu planétaire]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes le plus à l'aise à enseigner : [Thème 6 terminale -  L’enjeu de la connaissance]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes les moins à l’aise à enseigner : [Thème 1 première - Comprendre un régime politique : la démocratie]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes les moins à l’aise à enseigner : [Thème 2 première - Analyser les dynamiques des puissances internationales]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes les moins à l’aise à enseigner : [Thème 3 première - Étudier les divisions politiques du monde : les frontières]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes les moins à l’aise à enseigner : [Thème 4 première - S’informer : un regard critique sur les sources et modes de communication]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes les moins à l’aise à enseigner : [Thème 5 première - Analyser les relations entre États et religions]",
                        'Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes les moins à l’aise à enseigner : [Thème 1 terminale -  De nouveaux espaces de conquête]',
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes les moins à l’aise à enseigner : [Thème 2 terminale - Faire la guerre, faire la paix : formes de conflits et modes de résolution]",
                        'Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes les moins à l’aise à enseigner : [Thème 3 terminale -  Histoire et mémoires]',
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes les moins à l’aise à enseigner : [Thème 4 terminale - Identifier, protéger et valoriser le patrimoine : enjeux géopolitiques]",
                        "Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes les moins à l’aise à enseigner : [Thème 5 terminale - L’environnement, entre exploitation et protection : un enjeu planétaire]",
                        'Parmi les thèmes de la spécialité suivants, sélectionnez ceux pour lesquels vous êtes les moins à l’aise à enseigner : [Thème 6 terminale - L’enjeu de la connaissance]',
                        'Quelles méthodologies mettez-vous principalement en œuvre dans votre enseignement de la spécialité\xa0?\xa0 [Travail de recherche en autonomie]',
                        'Quelles méthodologies mettez-vous principalement en œuvre dans votre enseignement de la spécialité\xa0?\xa0 [Travail de recherche en groupe]',
                        'Quelles méthodologies mettez-vous principalement en œuvre dans votre enseignement de la spécialité\xa0?\xa0 [Présentation orale individuelle]',
                        'Quelles méthodologies mettez-vous principalement en œuvre dans votre enseignement de la spécialité\xa0?\xa0 [Présentation orale en groupe]',
                        'Quelles méthodologies mettez-vous principalement en œuvre dans votre enseignement de la spécialité\xa0?\xa0 [Cours magistral]']

    for colonne in colonnes_a_vider:
        dataframe[colonne].fillna(0, inplace=True)

    return dataframe