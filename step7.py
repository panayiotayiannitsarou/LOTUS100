
import pandas as pd
from collections import defaultdict
import itertools

def get_category(subdf):
    fyla = subdf["ΦΥΛΟ"].unique()
    glwssa = subdf["ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ"].unique()
    if len(fyla) > 1:
        return "Μικτού Φύλου"
    elif len(glwssa) == 1:
        if fyla[0] == "Α":
            return "Καλή Γνώση (Αγόρια)" if glwssa[0] == "Ν" else "Όχι Καλή Γνώση (Αγόρια)"
        else:
            return "Καλή Γνώση (Κορίτσια)" if glwssa[0] == "Ν" else "Όχι Καλή Γνώση (Κορίτσια)"
    else:
        return "Μικτής Γνώσης (Αγόρια)" if fyla[0] == "Α" else "Μικτής Γνώσης (Κορίτσια)"

def step7_elgxos_dior8oseis(df, num_classes):
    success_status = True
    df = df.copy()
    warnings = []
    class_labels = [f"Τμήμα {i+1}" for i in range(num_classes)]

    # Προετοιμασία: Φτιάχνουμε ομάδες από Βήματα 5 και 6 (ΚΛΕΙΔΩΜΕΝΟΣ == False)
    groups = []
    visited = set()
    name_to_index = {row["ΟΝΟΜΑΤΕΠΩΝΥΜΟ"]: idx for idx, row in df[df["ΚΛΕΙΔΩΜΕΝΟΣ"] == False].iterrows()}

    for idx, row in df[df["ΚΛΕΙΔΩΜΕΝΟΣ"] == False].iterrows():
        if idx in visited:
            continue
        name = row["ΟΝΟΜΑΤΕΠΩΝΥΜΟ"]
        friends = str(row["ΦΙΛΟΙ"]).split(",")
        friends = [f.strip() for f in friends if f.strip() and f.strip() in name_to_index]
        group = [idx]
        visited.add(idx)
        for friend in friends:
            f_idx = name_to_index.get(friend)
            if f_idx is not None and f_idx not in visited:
                friend_friends = str(df.loc[f_idx, "ΦΙΛΟΙ"]).split(",")
                friend_friends = [f.strip() for f in friend_friends if f.strip()]
                if name in friend_friends:
                    group.append(f_idx)
                    visited.add(f_idx)
        groups.append(group)

    # Υπολογισμός συνολικών χαρακτηριστικών ανά τμήμα
    def count_per_class(df, colname, value="Ν"):
        counts = {}
        for label in class_labels:
            counts[label] = (df[df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] == label][colname] == value).sum()
        return counts

    def student_count(df):
        return df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"].value_counts().to_dict()

    def difference_exceeds(c1, c2, threshold=3):
        return abs(c1 - c2) > threshold

    # Επαναλαμβανόμενο check για κάθε χαρακτηριστικό
    characteristics = [
        ("ΦΥΛΟ", ["Α", "Κ"]),
        ("ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ", ["Ν", "Ο"]),
        ("ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ", ["Ν", "Ο"])
    ]

    for col, values in characteristics:
        counts = count_per_class(df, col, values[0])

        # Εξετάζουμε όλα τα πιθανά ζευγάρια τμημάτων
        for cls1, cls2 in itertools.combinations(class_labels, 2):
            v1, v2 = counts.get(cls1, 0), counts.get(cls2, 0)
            if difference_exceeds(v1, v2):
                found = False
                for g1 in groups:
                    for g2 in groups:
                        if g1 == g2:
                            continue
                        tm1 = df.loc[g1[0], "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"]
                        tm2 = df.loc[g2[0], "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"]
                        if tm1 == cls1 and tm2 == cls2:
                            f1 = df.loc[g1, col].unique()
                            f2 = df.loc[g2, col].unique()
                            same_gender = df.loc[g1, "ΦΥΛΟ"].nunique() == 1 and df.loc[g2, "ΦΥΛΟ"].nunique() == 1
                            if same_gender and f1[0] == values[0] and f2[0] == values[1]:
                                # Ανταλλαγή
                                df.loc[g1, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = cls2
                                df.loc[g2, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = cls1
                                found = True
                                break
                    if found:
                        break
                if not found:
                    warnings.append(f"⚠️ Δεν κατέστη δυνατή η εξισορρόπηση για το χαρακτηριστικό: {col} μεταξύ {cls1} και {cls2}")

    # Ποσοτικός έλεγχος
    counts = student_count(df)
    for c1, c2 in itertools.combinations(class_labels, 2):
        if abs(counts.get(c1, 0) - counts.get(c2, 0)) > 2:
            success_status = False
            warnings.append(f"⛔ Παραβίαση πληθυσμιακής ισορροπίας μεταξύ {c1} και {c2}")
    for tm, count in counts.items():
        if count > 2:
            success_status = False5:
            success_status = False
            warnings.append(f"⛔ Το {tm} υπερβαίνει το όριο των 25 μαθητών")

    return df, warnings, success_status
