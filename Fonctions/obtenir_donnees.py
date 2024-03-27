import pandas as pd

def obtenir_uai(df, tout):
    def get_uai(row):
        for cell, cell_academie, uai, ville in zip(tout['Patronyme uai'], tout['Académie'], tout['UAI'], tout["Localite d'acheminement"]):
            if cell in row["Renseignez le nom de votre lycée et la ville dans laquelle il se situe.  Si vous exercez dans plusieurs établissements, merci de ne renseigner que celui dans lequel vous effectuez la majorité de votre service. "]:
                if row["Sélectionnez l'académie dans laquelle vous exercez. "] == cell_academie:
                    return uai
                elif ville in row["Renseignez le nom de votre lycée et la ville dans laquelle il se situe.  Si vous exercez dans plusieurs établissements, merci de ne renseigner que celui dans lequel vous effectuez la majorité de votre service. "]:
                    return uai
        return None
    df_avant = df.copy()
    df['UAI'] = df.apply(get_uai, axis=1)
    df_final = df_avant.merge(df[['UAI']], left_index=True, right_index=True)
    return df_final

def obtenir_ips(df_ips,dataframe_sans_ips):
    df_ips["Académie"] = df_ips["Académie"].str.lower()
    ips_moyen_par_academie = df_ips.groupby('Académie')['IPS voie GT'].mean()
    df_ips_moyen_par_academie = pd.DataFrame(ips_moyen_par_academie)
    df_ips_moyen_par_academie = df_ips_moyen_par_academie.rename(columns={'IPS voie GT': 'IPS_moyen'})

    df_final = dataframe_sans_ips.merge(df_ips_moyen_par_academie, how='left', left_on="Sélectionnez l'académie dans laquelle vous exercez. ", right_index=True)
    # Remplacer les valeurs NaN dans la colonne 'UAI' par les valeurs de 'IPS_moyen' s'il n'y a pas d'UAI
    df_final['UAI'].fillna(df_final['IPS_moyen'], inplace=True)

    df_ips_uai = pd.read_csv('c:\\Users\\enzom\\Desktop\\Etude-Sociologique-IPS-main-master-master\\Données\\fr-en-ips-lycees-ap2022.csv',sep=';')
    df_ips_lycee_selected = df_ips_uai[['UAI', 'IPS voie GT']] 
    df_final_ips_avec_ips_lycee = df_final.merge(df_ips_lycee_selected, how='left', on='UAI')
    df_final_ips_avec_ips_lycee.drop('IPS_moyen', axis=1, inplace=True)

    df_final_ips_avec_ips_lycee['IPS voie GT'].fillna(df_final_ips_avec_ips_lycee['UAI'], inplace=True)
    df_final_ips_avec_ips_lycee.drop('UAI', axis=1, inplace=True)

    return df_final_ips_avec_ips_lycee