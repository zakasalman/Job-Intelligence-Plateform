import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Job Market Intelligence", page_icon="💼", layout="wide")
st.title("🤖 AI-Powered Job Market Intelligence")


# --- CACHED RESOURCES ---
@st.cache_data
def load_data():
    # Make sure this matches your current clean dataset (e.g., linkedin_50k_clean.csv)
    return pd.read_csv("linkedin_50k_clean.csv")


@st.cache_data
def get_top_skills(df):
    skills_df = df[(df['job_skills'] != 'not specified') & (df['job_skills'] != 'nan')].copy()
    individual_skills = skills_df['job_skills'].str.split(',').explode().str.strip().str.title()
    junk_words = ['', 'And', 'To', 'Of', 'In', 'For', 'With', 'A', 'The', 'Or', 'On', 'Skills', 'Ability', 'Abilities']
    clean_skills = individual_skills[~individual_skills.isin(junk_words)]

    top_skills_df = clean_skills.value_counts().head(10).reset_index()
    top_skills_df.columns = ['Skill', 'Count']
    return top_skills_df


df = load_data()

# --- TABS ---
# The Role Recommender tab has been removed, leaving just the Dashboard and ATS Matcher
tab1, tab2 = st.tabs(["📊 Interactive Dashboard", "📄 ATS Resume Matcher"])

# ==========================================
# TAB 1: THE INTERACTIVE DASHBOARD
# ==========================================
with tab1:
    st.subheader("High-Level Industry Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Jobs Analyzed", "500000")
    col2.metric("Top Hiring Company", df['company'].value_counts().index[0])
    col3.metric("Top Location", df['job_location'].value_counts().index[0])
    col4.metric("Most Common Level", df['job_level'].value_counts().index[0])
    st.divider()

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("**🔥 Top 10 Most In-Demand Skills**")
        fig_skills = px.bar(get_top_skills(df), x='Count', y='Skill', orientation='h', color='Count',
                            color_continuous_scale='Blues', text_auto='.2s')
        fig_skills.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_skills, use_container_width=True)

        st.markdown("**📈 Experience Level Distribution**")
        level_df = df['job_level'].value_counts().reset_index()
        level_df.columns = ['Experience Level', 'Count']
        fig_levels = px.pie(level_df, names='Experience Level', values='Count', hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Teal)
        fig_levels.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_levels, use_container_width=True)

    with chart_col2:
        st.markdown("**📍 Top 10 Hiring Locations**")
        loc_df = df['job_location'].value_counts().head(10).reset_index()
        loc_df.columns = ['Location', 'Count']
        fig_loc = px.bar(loc_df, x='Location', y='Count', color='Count', color_continuous_scale='Viridis',
                         text_auto='.2s')
        fig_loc.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_loc, use_container_width=True)

        st.markdown("**🏢 Workplace Alignment**")
        type_df = df['job_type'].value_counts().reset_index()
        type_df.columns = ['Job Type', 'Count']
        fig_type = px.pie(type_df, names='Job Type', values='Count',
                          color_discrete_sequence=px.colors.sequential.Sunset)
        fig_type.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_type, use_container_width=True)

# ==========================================
# TAB 2: ATS RESUME MATCHER
# ==========================================
with tab2:
    st.header("ATS Resume Compatibility Scanner")
    colA, colB = st.columns(2)
    with colA:
        job_desc = st.text_area("Paste the Job's Required Skills:", height=200)
    with colB:
        resume_text = st.text_area("Paste Your Resume Text:", height=200)

    if st.button("Calculate ATS Match Score") and job_desc and resume_text:
        text_list = [job_desc, resume_text]
        cv = CountVectorizer(stop_words='english')
        count_matrix = cv.fit_transform(text_list)
        match_percentage = cosine_similarity(count_matrix)[0][1] * 100

        if match_percentage >= 80:
            st.success(f"🔥 Excellent Match! Your ATS Score is **{match_percentage:.1f}%**")
        elif match_percentage >= 50:
            st.warning(f"⚠️ Moderate Match. Your ATS Score is **{match_percentage:.1f}%**")
        else:
            st.error(f"❌ Low Match. Your ATS Score is **{match_percentage:.1f}%**")
