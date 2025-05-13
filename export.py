import pandas as pd
import streamlit as st
def export_data(conn, texts):
    st.title(texts["export_title"])

    # Load complaints data from the database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints")
    complaints_data = cursor.fetchall()

    if complaints_data:
        df = pd.DataFrame(complaints_data, columns=["id", "name", "email", "category", "content", "priority", "status", "created_at"])

        # Export to CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label=texts["download_csv"],
            data=csv,
            file_name="complaints_data.csv",
            mime="text/csv"
        )
    else:
        st.write(texts["no_data_export"])
