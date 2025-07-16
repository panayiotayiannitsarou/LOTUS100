
import pandas as pd
from collections import defaultdict

# Βήμα 3: Κατηγοριοποίηση ομάδων και ήδη τοποθετημένων
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

def step5_omadopoihsh_katigories(df):
    df = df.copy()

    # Βήμα 1: Επιλογή μη τοποθετημένων μαθητών
    not_placed = df[df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] == ""].copy()
    placed = df[df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] != ""].copy()

    # Βήμα 2: Ομαδοποίηση βάσει πλήρως αμοιβαίας φιλίας
    visited = set()
    groups = []

    name_to_index = {row["ΟΝΟΜΑΤΕΠΩΝΥΜΟ"]: idx for idx, row in not_placed.iterrows()}

    for idx, row in not_placed.iterrows():
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
                friend_friends = str(not_placed.loc[f_idx, "ΦΙΛΟΙ"]).split(",")
                friend_friends = [f.strip() for f in friend_friends if f.strip()]
                if name in friend_friends:
                    group.append(f_idx)
                    visited.add(f_idx)

        groups.append(group)



    categories = defaultdict(list)

    # Ομαδικές μη τοποθετημένες
    for group in groups:
        subdf = not_placed.loc[group]
        cat = get_category(subdf)
        categories[cat].append(group)

    # Τοποθετημένοι ανά κατηγορία (σαν μονές ομάδες)
    for idx, row in placed.iterrows():
        cat = get_category(pd.DataFrame([row]))
        categories[cat].append([idx])

    return categories, groups


def step5_katanomi_omadon_se_tmimata(df, categories, num_classes):
    df = df.copy()
    class_labels = [f"Τμήμα {i+1}" for i in range(num_classes)]

    # Μετρητές για κατανομή κατηγοριών στα τμήματα
    katigoria_ana_tmima = {tmima: defaultdict(int) for tmima in class_labels}
    plenoi_ana_tmima = {tmima: 0 for tmima in class_labels}

    # Προσμέτρηση ήδη τοποθετημένων
    for idx, row in df[df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] != ""].iterrows():
        cat = get_category(pd.DataFrame([row]))
        tmima = row["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"]
        katigoria_ana_tmima[tmima][cat] += 1
        plenoi_ana_tmima[tmima] += 1

    # Κατανομή αδιαίρετων ομάδων ανά κατηγορία
    for katigoria, teams in categories.items():
        team_index = 0
        sorted_teams = sorted(teams, key=lambda x: -len(x))  # Μεγάλες ομάδες πρώτα

        for group in sorted_teams:
            # Επιλογή τμήματος με βάση εναλλαγή
            # Βρίσκουμε το τμήμα με τη μικρότερη αναλογία στην ίδια κατηγορία
            best_tmima = min(class_labels, key=lambda tm: (katigoria_ana_tmima[tm][katigoria], plenoi_ana_tmima[tm]))

            # Τοποθέτηση όλων των μελών της ομάδας
            for i in group:
                df.loc[i, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = best_tmima
                df.loc[i, "ΚΛΕΙΔΩΜΕΝΟΣ"] = True
                katigoria_ana_tmima[best_tmima][katigoria] += 1
                plenoi_ana_tmima[best_tmima] += 1

    return df
