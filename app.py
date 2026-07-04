import streamlit

page_1 = streamlit.Page("Singapore_Carbonfootprint.py", title="Singapore Carbonfootprint")
page_2 = streamlit.Page("Meet_The_Developer.py", title="About")
streamlit.navigation([page_1,page_2]).run()