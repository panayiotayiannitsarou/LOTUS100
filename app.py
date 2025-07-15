
import streamlit as st
import pandas as pd
import math
from io import BytesIO

from step1 import step1_katanomi_paidia_ekpaideutikon
from step2 import step2_katanomi_zoiroi
from step3 import step3_katanomi_idiaiterotites
from step4 import step4_katanomi_filia
from step5 import step5_omadopoihsh_katigories, step5_katanomi_omadon_se_tmimata
from step6 import step6_ypolipoi_xwris_filies
from step7_final_check_and_fix import step7_final_check_and_fix

# ➤ Κλείδωμα με Κωδικό
st.sidebar.title("🔐 Κωδικός Πρόσβασης")
password = st.sidebar.text_input("Εισάγετε τον κωδικό:", type="password")
if password != "katanomi2025":
    st.warning("Παρακαλώ εισάγετε έγκυρο κωδικό για πρόσβαση στην εφαρμογή.")
    st.stop()

# ➤ Ενεργοποίηση/Απενεργοποίηση Εφαρμογής
enable_app = st.sidebar.checkbox("✅ Ενεργοποίηση Εφαρμογής", value=True)
if not enable_app:
    st.info("🔒 Η εφαρμογή είναι προσωρινά απενεργοποιημένη.")
    st.stop()

st.title("🎯 Ψηφιακή Κατανομή Μαθητών Α΄ Δημοτικού – Βήματα 1 έως 7")

# ➤ Εισαγωγή Αρχείου Excel
uploaded_file = st.file_uploader("📥 Εισαγωγή Αρχείου Excel Μαθητών", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ Το αρχείο ανέβηκε επιτυχώς!")
    num_classes = math.ceil(len(df) / 25)
    df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = ""
    df["ΚΛΕΙΔΩΜΕΝΟΣ"] = False

    with st.spinner("▶️ Βήμα 1: Παιδιά Εκπαιδευτικών..."):
        df = step1_katanomi_paidia_ekpaideutikon(df, num_classes)
    with st.spinner("▶️ Βήμα 2: Ζωηροί Μαθητές..."):
        df = step2_katanomi_zoiroi(df, num_classes)
    with st.spinner("▶️ Βήμα 3: Παιδιά με Ιδιαιτερότητες..."):
        df = step3_katanomi_idiaiterotites(df, num_classes)
    with st.spinner("▶️ Βήμα 4: Αμοιβαίες Φιλίες..."):
        df = step4_katanomi_filia(df)
    with st.spinner("▶️ Βήμα 5: Ομαδοποίηση & Κατηγοριοποίηση..."):
        categories, _ = step5_omadopoihsh_katigories(df)
        df = step5_katanomi_omadon_se_tmimata(df, categories, num_classes)
    with st.spinner("▶️ Βήμα 6: Υπόλοιποι Μαθητές Χωρίς Φιλίες..."):
        df = step6_ypolipoi_xwris_filies(df, num_classes)
    with st.spinner("▶️ Βήμα 7: Έλεγχος & Διορθώσεις..."):
        df, warnings, success = step7_final_check_and_fix(df, num_classes)
        if not success:
            st.error("⛔ Η κατανομή δεν ήταν επιτυχής λόγω παραβίασης πληθυσμιακών περιορισμών (π.χ. >25 μαθητές ή διαφορά >2).")
            st.stop()

    df["ΤΜΗΜΑ"] = df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"]
    st.success(f"✅ Ολοκληρώθηκε η κατανομή με {num_classes} τμήματα.")

    st.subheader("🔍 Προεπισκόπηση Τελικής Κατανομής")
    st.dataframe(df)

    if warnings:
        st.warning("⚠️ Προειδοποιήσεις Κατανομής:")
        for w in warnings:
            st.text(w)

    # Στατιστικά Τμημάτων
    st.subheader("📊 Πίνακας Στατιστικών Ανά Τμήμα")
    summary = []
    for i in range(num_classes):
        class_id = f'Τμήμα {i+1}'
        class_df = df[df["ΤΜΗΜΑ"] == class_id]
        total = class_df.shape[0]
        stats = {
            "ΤΜΗΜΑ": class_id,
            "ΑΓΟΡΙΑ": (class_df["ΦΥΛΟ"] == "Α").sum(),
            "ΚΟΡΙΤΣΙΑ": (class_df["ΦΥΛΟ"] == "Κ").sum(),
            "ΠΑΙΔΙΑ_ΕΚΠΑΙΔΕΥΤΙΚΩΝ": (class_df["ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν").sum(),
            "ΖΩΗΡΟΙ": (class_df["ΖΩΗΡΟΣ"] == "Ν").sum(),
            "ΙΔΙΑΙΤΕΡΟΤΗΤΕΣ": (class_df["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν").sum(),
            "ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ": (class_df["ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ"] == "Ν").sum(),
            "ΙΚΑΝΟΠΟΙΗΤΙΚΗ_ΜΑΘΗΣΙΑΚΗ_ΙΚΑΝΟΤΗΤΑ": (class_df["ΙΚΑΝΟΠΟΙΗΤΙΚΗ ΜΑΘΗΣΙΑΚΗ ΙΚΑΝΟΤΗΤΑ"] == "Ν").sum(),
            "ΣΥΝΟΛΟ Τμήματος": total
        }
        summary.append(stats)

    stats_df = pd.DataFrame(summary)
    st.dataframe(stats_df)

    # Λήψη αρχείων
    output_katanomi = BytesIO()
    df.to_excel(output_katanomi, index=False)
    st.download_button("📥 Λήψη Excel Κατανομής", data=output_katanomi.getvalue(), file_name="Katanomi_Telikos.xlsx")

    output_stats = BytesIO()
    stats_df.to_excel(output_stats, index=False, sheet_name="Στατιστικά")
    st.download_button("📊 Λήψη Excel Στατιστικών", data=output_stats.getvalue(), file_name="Statistika_Tmimaton.xlsx")
