
import pandas as pd

def step2_katanomi_zoiroi(df, num_classes):
    df = df.copy()

    if "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ" not in df.columns:
        df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = ""
    if "ΚΛΕΙΔΩΜΕΝΟΣ" not in df.columns:
        df["ΚΛΕΙΔΩΜΕΝΟΣ"] = False

    class_labels = [f"Τμήμα {i+1}" for i in range(num_classes)]

    # Υπολογισμός ήδη τοποθετημένων ζωηρών
    zoiroi_placed = df[(df["ΖΩΗΡΟΣ"] == "Ν") & (df["ΚΛΕΙΔΩΜΕΝΟΣ"] == True)]
    zoiroi_free = df[(df["ΖΩΗΡΟΣ"] == "Ν") & (df["ΚΛΕΙΔΩΜΕΝΟΣ"] == False)]

    # Αριθμός ζωηρών ανά τμήμα (ήδη τοποθετημένων)
    zoiroi_ana_tmima = {label: 0 for label in class_labels}
    fylo_ana_tmima = {label: {"Α": 0, "Κ": 0} for label in class_labels}

    for _, row in zoiroi_placed.iterrows():
        tmima = row["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"]
        zoiroi_ana_tmima[tmima] += 1
        fylo_ana_tmima[tmima][row["ΦΥΛΟ"]] += 1

    for _, row in df[df["ΚΛΕΙΔΩΜΕΝΟΣ"] == True].iterrows():
        tmima = row["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"]
        fylo_ana_tmima[tmima][row["ΦΥΛΟ"]] += 1

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
                same_class = df.loc[f_index, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] == candidate_class
                mutual = df.loc[i, "ΟΝΟΜΑΤΕΠΩΝΥΜΟ"] in f_friends
                if same_class and mutual:
                    return True
        return False

    total_zoiroi = len(zoiroi_placed) + len(zoiroi_free)

    if total_zoiroi <= num_classes:
        # Ένας ζωηρός ανά τμήμα το πολύ
        for i in zoiroi_free.index:
            row = df.loc[i]
            fylo = row["ΦΥΛΟ"]
            best_choice = None

            for tmima in class_labels:
                if zoiroi_ana_tmima[tmima] == 0:
                    if is_fully_mutual_friend(df, i, tmima):
                        best_choice = tmima
                        break
                    if best_choice is None:
                        best_choice = tmima

            if best_choice is None:
                best_choice = min(class_labels, key=lambda t: zoiroi_ana_tmima[t])

            df.loc[i, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = best_choice
            df.loc[i, "ΚΛΕΙΔΩΜΕΝΟΣ"] = True
            zoiroi_ana_tmima[best_choice] += 1
            fylo_ana_tmima[best_choice][fylo] += 1
    else:
        # Ισοκατανομή με κανόνες
        for i in zoiroi_free.index:
            row = df.loc[i]
            fylo = row["ΦΥΛΟ"]
            best_choice = None
            min_zoiroi = float("inf")

            for tmima in class_labels:
                zoiroi_here = zoiroi_ana_tmima[tmima]
                same_gender_count = fylo_ana_tmima[tmima][fylo]

                # 1. Αποφυγή σύγκρουσης με άλλον ζωηρό
                if zoiroi_here >= (total_zoiroi // num_classes) + 1:
                    continue

                # 2. Πλήρως αμοιβαία φιλία με παιδί εκπαιδευτικού ή άλλο ζωηρό
                if is_fully_mutual_friend(df, i, tmima):
                    best_choice = tmima
                    break

                # 3. Αποφυγή συγκέντρωσης ίδιου φύλου
                if same_gender_count == 0 and zoiroi_here < min_zoiroi:
                    best_choice = tmima
                    min_zoiroi = zoiroi_here
                elif zoiroi_here < min_zoiroi and best_choice is None:
                    best_choice = tmima
                    min_zoiroi = zoiroi_here

            if best_choice is None:
                best_choice = min(class_labels, key=lambda t: zoiroi_ana_tmima[t])

            df.loc[i, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = best_choice
            df.loc[i, "ΚΛΕΙΔΩΜΕΝΟΣ"] = True
            zoiroi_ana_tmima[best_choice] += 1
            fylo_ana_tmima[best_choice][fylo] += 1

    return df
