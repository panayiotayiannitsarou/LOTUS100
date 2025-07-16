def step7_final_check_and_fix(df, num_classes, max_diff=3):
    import pandas as pd
    import numpy as np
    import itertools

    warnings = []
    success = True

    
    import pandas as pd
    import itertools
    
    #from step7 import step7_final_check_and_fix  # Εισαγωγή από το αρχείο step7.py
    
    # Προαιρετική wrapper συνάρτηση (αν την καλείς αλλού μέσα στο app)
    def apply_final_check(df, num_classes, max_diff=3):
        df = df.copy()
        df, success_status, warnings = step7_final_check_and_fix(df, num_classes, max_diff)
        return df, success_status, warnings
    
    
        # Βρες ομάδες μη κλειδωμένων με πλήρως αμοιβαίες φιλίες
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
    
        def count_per_class(df, colname, value="Ν"):
            return {label: (df[df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] == label][colname] == value).sum() for label in class_labels}
    
        def student_count(df):
            return df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"].value_counts().to_dict()
    
        def difference_exceeds(a, b, threshold):
            return abs(a - b) > threshold
    
        characteristics = [
            ("ΦΥΛΟ", ["Α", "Κ"]),
            ("ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ", ["Ν", "Ο"]),
            ("ΜΑΘΗΣΙΑΚΗ_ΙΚΑΝΟΤΗΤΑ", ["Ν", "Ο"])
        ]
    
        for col, values in characteristics:
            counts = count_per_class(df, col, values[0])
            for cls1, cls2 in itertools.combinations(class_labels, 2):
                v1, v2 = counts.get(cls1, 0), counts.get(cls2, 0)
                if difference_exceeds(v1, v2, max_diff):
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
            if count > 25:
                success_status = False
                warnings.append(f"⛔ Το {tm} υπερβαίνει το όριο των 25 μαθητών")
    
        return df, warnings, success_status
    

    return df, warnings, success
