
import pandas as pd

def step6_ypolipoi_xwris_filies(df, num_classes):
    df = df.copy()

    if "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ" not in df.columns:
        df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = ""
    if "ΚΛΕΙΔΩΜΕΝΟΣ" not in df.columns:
        df["ΚΛΕΙΔΩΜΕΝΟΣ"] = False

    class_labels = [f"Τμήμα {i+1}" for i in range(num_classes)]

    # Υπολογισμός πλήθους και φύλου ανά τμήμα
    count_ana_tmima = {tmima: 0 for tmima in class_labels}
    fylo_ana_tmima = {tmima: {"Α": 0, "Κ": 0} for tmima in class_labels}

    for _, row in df[df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] != ""].iterrows():
        tmima = row["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"]
        count_ana_tmima[tmima] += 1
        fylo_ana_tmima[tmima][row["ΦΥΛΟ"]] += 1

    # Επιλογή μη τοποθετημένων μαθητών χωρίς αμοιβαία φιλία
    def has_mutual_friend(i):
        if "ΦΙΛΟΙ" not in df.columns:
            return False
        name = df.loc[i, "ΟΝΟΜΑΤΕΠΩΝΥΜΟ"]
        friends = str(df.loc[i, "ΦΙΛΟΙ"]).split(",")
        friends = [f.strip() for f in friends if f.strip()]
        for friend_name in friends:
            f_row = df[df["ΟΝΟΜΑΤΕΠΩΝΥΜΟ"] == friend_name]
            if not f_row.empty:
                f_friends = str(f_row.iloc[0]["ΦΙΛΟΙ"]).split(",")
                f_friends = [f.strip() for f in f_friends if f.strip()]
                if name in f_friends:
                    return True
        return False

    for i in df[(df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] == "")].index:
        if has_mutual_friend(i):
            continue  # παραλείπεται αν έχει πλήρως αμοιβαία φιλία

        fylo = df.loc[i, "ΦΥΛΟ"]

        # Προτεραιότητα 1: Μικρότερο πλήθος
        min_count = min(count_ana_tmima.values())
        candidates = [tm for tm, c in count_ana_tmima.items() if c == min_count]

        # Προτεραιότητα 2: Ισορροπία φύλου
        best_tmima = min(candidates, key=lambda tm: fylo_ana_tmima[tm][fylo])

        df.loc[i, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = best_tmima
        df.loc[i, "ΚΛΕΙΔΩΜΕΝΟΣ"] = True
        count_ana_tmima[best_tmima] += 1
        fylo_ana_tmima[best_tmima][fylo] += 1

    return df
