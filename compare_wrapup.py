import pandas as pd


existentes_path = r"C:\Users\alexandre.ferreira\Desktop\Scripts\Comparar\wrapup_existentes.csv"
criados_path = r"C:\Users\alexandre.ferreira\Desktop\Scripts\Comparar\wrarpup_criados.csv"


existentes_df = pd.read_csv(existentes_path)
criados_df = pd.read_csv(criados_path)


comparado_df = pd.merge(criados_df, existentes_df, on="Wrap-Up Name", how="inner")


comparado_df.to_csv("wrapups_com_ids.csv", index=False)

print("Comparação concluída com sucesso!")
