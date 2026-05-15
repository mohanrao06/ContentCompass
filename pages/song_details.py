import streamlit as st

# Hide sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Song Details Page")
st.info("Song detail page is under construction. This will show comprehensive information about the selected song once the song recommendation system is implemented.")

if st.button("← Back to Recommendations"):
    st.switch_page("app.py")