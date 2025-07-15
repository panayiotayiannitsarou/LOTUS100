
import streamlit as st
import pandas as pd
import math
from io import BytesIO

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

st.title("🎯 Ψηφιακή Κατανομή Μαθητών Α΄ Δημοτικού")

# ➤ Εισαγωγή Αρχείου Excel
uploaded_file = st.file_uploader("📥 Εισαγωγή Αρχείου Excel Μαθητών", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ Το αρχείο ανέβηκε επιτυχώς!")

    def calculate_class_distribution(df):
        total_students = len(df)
        max_per_class = 25
        num_classes = math.ceil(total_students / max_per_class)
        st_per_class = total_students // num_classes
        remainder = total_students % num_classes
        class_sizes = [st_per_class + 1 if i < remainder else st_per_class for i in range(num_classes)]
        class_labels = []
        for i, size in enumerate(class_sizes):
            class_labels.extend([f"Τμήμα {i+1}"] * size)
        df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
        df_shuffled["ΤΜΗΜΑ"] = class_labels
        df_shuffled["ΚΛΕΙΔΩΜΕΝΟΣ"] = False
        return df_shuffled, num_classes

    def show_statistics_table(df, num_classes):
        summary = []
        for i in range(num_classes):
            class_id = f'Τμήμα {i+1}'
            class_df = df[df['ΤΜΗΜΑ'] == class_id]
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
        st.subheader("📊 Πίνακας Στατιστικών Ανά Τμήμα")
        st.dataframe(stats_df)

        # Λήψη Excel μόνο με Στατιστικά
        output_stats = BytesIO()
        stats_df.to_excel(output_stats, index=False, sheet_name='Στατιστικά')
        st.download_button(
            label="📥 Λήψη Excel μόνο με Στατιστικά",
            data=output_stats.getvalue(),
            file_name="Monon_Statistika.xlsx"
        )

    if st.button("📌 Τελική Κατανομή Μαθητών (μετά τα 8 Βήματα)"):
        df, num_classes = calculate_class_distribution(df)
        st.session_state["df"] = df
        st.session_state["num_classes"] = num_classes
        st.success(f"✅ Η κατανομή ολοκληρώθηκε με {num_classes} τμήματα.")
        st.subheader("🔍 Προεπισκόπηση Μετά την Κατανομή")
        st.dataframe(df)

        # Λήψη Excel μόνο με Κατανομή
        output_katanomi = BytesIO()
        df.to_excel(output_katanomi, index=False)
        st.download_button(
            label="📥 Λήψη Excel μόνο με Κατανομή",
            data=output_katanomi.getvalue(),
            file_name="Monon_Katanomi.xlsx"
        )

    if "df" in st.session_state and "ΤΜΗΜΑ" in st.session_state["df"].columns:
        df = st.session_state["df"]
        num_classes = st.session_state["num_classes"]
        show_statistics_table(df, num_classes)
