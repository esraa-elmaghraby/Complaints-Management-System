import streamlit as st
import plotly.express as px
import plotly.io as pio
import pandas as pd

# Set default plotly theme
pio.templates.default = "plotly_white"

def show_analytics(conn, texts):
    st.markdown("<h2 style='color:#2c3e50;'>Analytics</h2>", unsafe_allow_html=True)

    custom_colors = ["#0cc0df", "#ffde59", "#ff3131", "#ff914d", "#8c52ff", "#5ce1e6"]

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints")
    complaints_data = cursor.fetchall()

    if complaints_data:
        df = pd.DataFrame(complaints_data, columns=[
            "id", "name", "email", "category", "content", "priority", "status", "created_at"
        ])
        df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')

        # KPIs
        total = len(df)
        resolved = len(df[df["status"].str.lower().isin(["resolved", "تم الحل"])])
        unresolved = total - resolved
        percent_resolved = (resolved / total) * 100 if total > 0 else 0

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric(label="Total Complaints", value=total)
        kpi2.metric(label="Resolved Complaints", value=resolved)
        kpi3.metric(label="Resolution Rate", value=f"{percent_resolved:.2f}%")

        st.markdown("---")

        # Charts Row 1: Category & Priority
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            fig_cat = px.bar(df, x="category", color="category", title="Complaints by Category",
                             color_discrete_sequence=custom_colors)
            fig_cat.update_layout(title_font_size=18, title_font_color="#2c3e50")
            st.plotly_chart(fig_cat, use_container_width=True)

        with row1_col2:
            fig_pri = px.pie(df, names="priority", title="Complaints by Priority",
                             color_discrete_sequence=custom_colors)
            fig_pri.update_traces(textinfo="percent+label", pull=0.03)
            fig_pri.update_layout(title_font_size=18, title_font_color="#2c3e50")
            st.plotly_chart(fig_pri, use_container_width=True)

        # Charts Row 2: Status & Time Trend
        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            fig_status = px.pie(df, names="status", title="Complaints by Status",
                                color_discrete_sequence=custom_colors)
            fig_status.update_traces(textinfo="percent+label", pull=0.03)
            fig_status.update_layout(title_font_size=18, title_font_color="#2c3e50")
            st.plotly_chart(fig_status, use_container_width=True)

        with row2_col2:
            df_monthly = df.groupby(df["created_at"].dt.to_period("M")).size().reset_index(name="count")
            df_monthly["created_at"] = df_monthly["created_at"].astype(str)
            fig_time = px.line(df_monthly, x="created_at", y="count", markers=True, title="Monthly Complaint Trend")
            fig_time.update_traces(line_shape="linear", line_color="#8c52ff", marker_color="#5ce1e6")
            fig_time.update_layout(
                title_font_size=18,
                xaxis_title="Month",
                yaxis_title="Number of Complaints",
                title_font_color="#2c3e50"
            )
            st.plotly_chart(fig_time, use_container_width=True)

    else:
        st.warning("No complaint data found in the database.")
