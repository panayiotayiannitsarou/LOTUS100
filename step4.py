
import pandas as pd

def step4_katanomi_filia(df):
    df = df.copy()

    if "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ" not in df.columns:
        df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = ""
    if "ΚΛΕΙΔΩΜΕΝΟΣ" not in df.columns:
        df["ΚΛΕΙΔΩΜΕΝΟΣ"] = False

    not_placed = df[df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] == ""]

    for i in not_placed.index:
        row = df.loc[i]
        friends = str(row["ΦΙΛΟΙ"]).split(",")
        friends = [f.strip() for f in friends if f.strip()]
        for friend_name in friends:
            friend_row = df[df["ΟΝΟΜΑΤΕΠΩΝΥΜΟ"] == friend_name]
            if not friend_row.empty:
                friend_tmima = friend_row.iloc[0]["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"]
                if friend_tmima != "":
                    df.loc[i, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = friend_tmima
                    df.loc[i, "ΚΛΕΙΔΩΜΕΝΟΣ"] = True
                    break  # Μόλις βρεθεί φίλος με τοποθέτηση, δεν ψάχνουμε άλλον

    return df
