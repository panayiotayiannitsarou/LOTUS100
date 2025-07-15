
import pandas as pd

def step3_katanomi_idiaiterotites(df, num_classes):
    df = df.copy()

    if "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ" not in df.columns:
        df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = ""
    if "ΚΛΕΙΔΩΜΕΝΟΣ" not in df.columns:
        df["ΚΛΕΙΔΩΜΕΝΟΣ"] = False

    class_labels = [f"Τμήμα {i+1}" for i in range(num_classes)]

    idiaiteroi_all = df[df["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν"]
    idiaiteroi_free = idiaiteroi_all[~idiaiteroi_all["ΚΛΕΙΔΩΜΕΝΟΣ"]]

    idiaiterotites_ana_tmima = {label: 0 for label in class_labels}
    zoiroi_ana_tmima = {label: 0 for label in class_labels}
    fylo_ana_tmima = {label: {"Α": 0, "Κ": 0} for label in class_labels}

    for _, row in df[df["ΚΛΕΙΔΩΜΕΝΟΣ"]].iterrows():
        tmima = row["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"]
        fylo_ana_tmima[tmima][row["ΦΥΛΟ"]] += 1
        if row["ΖΩΗΡΟΣ"] == "Ν":
            zoiroi_ana_tmima[tmima] += 1
        if row["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν":
            idiaiterotites_ana_tmima[tmima] += 1

    def has_conflict(df, i, candidate_class):
        if "ΣΥΓΚΡΟΥΣΗ" not in df.columns:
            return False
        conflicts = str(df.loc[i, "ΣΥΓΚΡΟΥΣΗ"]).split(",")
        conflicts = [c.strip() for c in conflicts if c.strip()]
        for name in conflicts:
            row = df[df["ΟΝΟΜΑΤΕΠΩΝΥΜΟ"] == name]
            if not row.empty and row.iloc[0]["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] == candidate_class:
                return True
        return False

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

    total_idiaiteroi = len(idiaiteroi_all)

    for i in idiaiteroi_free.index:
        row = df.loc[i]
        fylo = row["ΦΥΛΟ"]
        best_choice = None
        fewest_zoiroi = float("inf")

        for tmima in class_labels:
            if total_idiaiteroi <= num_classes and idiaiterotites_ana_tmima[tmima] >= 1:
                continue  # όταν είναι λίγοι, μόνο 1 ανά τμήμα
            if has_conflict(df, i, tmima):
                continue
            if zoiroi_ana_tmima[tmima] < fewest_zoiroi:
                best_choice = tmima
                fewest_zoiroi = zoiroi_ana_tmima[tmima]

        # Προτίμηση: πλήρως αμοιβαία φιλία
        for tmima in class_labels:
            if has_conflict(df, i, tmima):
                continue
            if is_fully_mutual_friend(df, i, tmima) and zoiroi_ana_tmima[tmima] <= fewest_zoiroi:
                best_choice = tmima
                break

        # Αποφυγή συγκέντρωσης ίδιου φύλου
        for tmima in class_labels:
            if has_conflict(df, i, tmima):
                continue
            if fylo_ana_tmima[tmima][fylo] == 0 and zoiroi_ana_tmima[tmima] <= fewest_zoiroi:
                best_choice = tmima
                break

        if best_choice is None:
            best_choice = min(class_labels, key=lambda t: idiaiterotites_ana_tmima[t])

        df.loc[i, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = best_choice
        df.loc[i, "ΚΛΕΙΔΩΜΕΝΟΣ"] = True
        idiaiterotites_ana_tmima[best_choice] += 1
        fylo_ana_tmima[best_choice][fylo] += 1

    return df
