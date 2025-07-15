
import pandas as pd

def step1_katanomi_paidia_ekpaideutikon(df, num_classes):
    df = df.copy()

    if "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ" not in df.columns:
        df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = ""
    if "ΚΛΕΙΔΩΜΕΝΟΣ" not in df.columns:
        df["ΚΛΕΙΔΩΜΕΝΟΣ"] = False

    paidia_ekp = df[df["ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν"].copy()
    paidia_ekp_indices = paidia_ekp.index.tolist()
    class_labels = [f"Τμήμα {i+1}" for i in range(num_classes)]

    tmimata = {label: [] for label in class_labels}
    fylo_ana_tmima = {label: {"Α": 0, "Κ": 0} for label in class_labels}

    def is_fully_mutual_friend(df, i, candidate_class):
        if "ΦΙΛΟΙ" not in df.columns:
            return False
        friends = str(df.loc[i, "ΦΙΛΟΙ"]).split(",")
        friends = [f.strip() for f in friends if f.strip()]
        for friend_name in friends:
            friend_row = df[df["ΟΝΟΜΑΤΕΠΩΝΥΜΟ"] == friend_name]
            if not friend_row.empty:
                f_index = friend_row.index[0]
                f_friends = str(friend_row.iloc[0]["ΦΙΛΟΙ"]).split(",")
                f_friends = [f.strip() for f in f_friends if f.strip()]
                if df.loc[f_index, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] == candidate_class and df.loc[i, "ΟΝΟΜΑΤΕΠΩΝΥΜΟ"] in f_friends:
                    return True
        return False

    if len(paidia_ekp) <= num_classes:
        for idx, (i, row) in enumerate(paidia_ekp.iterrows()):
            tmima = class_labels[idx]
            df.loc[i, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = tmima
            df.loc[i, "ΚΛΕΙΔΩΜΕΝΟΣ"] = True
            fylo_ana_tmima[tmima][row["ΦΥΛΟ"]] += 1
            tmimata[tmima].append(i)
    else:
        for i in paidia_ekp_indices:
            row = df.loc[i]
            fylo = row["ΦΥΛΟ"]
            best_choice = None
            min_count = float('inf')

            for tmima in class_labels:
                count = len(tmimata[tmima])
                same_gender_count = fylo_ana_tmima[tmima][fylo]

                # 1. Προτεραιότητα: πλήρως αμοιβαία φιλία
                if is_fully_mutual_friend(df, i, tmima):
                    best_choice = tmima
                    break

                # 2. Προτεραιότητα: αποφυγή συγκέντρωσης ίδιου φύλου
                if same_gender_count == 0 and count < min_count:
                    best_choice = tmima
                    min_count = count
                elif same_gender_count > 0 and count < min_count and best_choice is None:
                    best_choice = tmima
                    min_count = count

            if best_choice is None:
                best_choice = min(class_labels, key=lambda t: len(tmimata[t]))

            df.loc[i, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = best_choice
            df.loc[i, "ΚΛΕΙΔΩΜΕΝΟΣ"] = True
            fylo_ana_tmima[best_choice][fylo] += 1
            tmimata[best_choice].append(i)

    return df
