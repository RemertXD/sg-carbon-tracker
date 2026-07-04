import streamlit as st

st.set_page_config(layout="wide", page_title="About the Developer")

st.title("👨‍💻 Meet the Developer")
st.markdown("---")

col1, col2 = st.columns([3, 5])
with col1:
    st.image("me_photo.jpeg", use_container_width=True, caption="Rohan")

with col2:
    st.markdown("### 👋 Hi There!")
    st.markdown(
        """
        <span style='font-size: 1.2rem; line-height: 1.6;'>
        I am Rohan, the developer of this website. I am a Grade 11 student 
        at Invictus International School who is passionate about Mathematics and Coding. 
        I love building software tools that apply data analytics and this is my first project 
        which addresses real-world problems! Feel free to contact me for any feedback or suggestions.
        
        Contact: jain2010rohan@gmail.com
        </span>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

st.markdown("## 🌍 Why Did I Build This Website?")

st.write(
    "After recently completing a course on Net Zero Carbon Emissions, I truly realized the scale of this "
    "problem and the urgency needed to solve it! If you are interested in taking the course, click the link below. "
    "It only takes about one hour to do!"

)
st.link_button(
        "🌱 Net Zero 101: What, Why and How",
        "https://unccelearn.org/course/view.php?id=185&page=overview",
        use_container_width=True
    )

st.write(
    "A nationwide survey conducted by the National University of Singapore (NUS IPUR), "
    "the Singapore University of Technology and Design (SUTD), and the Ministry of Sustainability "
    "and the Environment found that **only 15% of residents were aware of Singapore's goal of Net Zero "
    "carbon emissions by 2050**."
)
st.write(
    "Furthermore, domestic transport makes up **~11.7%** of Singapore's total carbon emissions—trailing "
    "only behind Power Generation (~38.7%) and Industry (~47.3%). While changing industrial sectors takes time, "
    "we can actively reduce carbon emissions in transport right now! This website empowers you to calculate, "
    "visualize, and choose the most eco-friendly public transport route for your daily commute."
)

metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    st.metric(label="Industry Emissions", value="~47.3%")
with metric_col2:
    st.metric(label="Power Generation", value="~38.7%")
with metric_col3:
    st.metric(label="Transport Emissions (Our Target)", value="~11.7%", delta="- Let's Reduce This!")

st.markdown("---")

st.markdown("## 🛠️ How Did I Build This Website?")
st.write(
    "This application was built entirely using **Python**! By leveraging the robust open-source **OneMap API** "
    "developed by the Singapore Land Authority (SLA), the app fetches live geocoding records and real-time public transit routing matrices."
)
st.write(
    "This clean, responsive user interface was designed using the Python web framework **Streamlit** and interactive mapping "
    "library **Folium**. Throughout development, I also utilized **AI tools** to help troubleshoot "
    "complex asynchronous UI states, optimize the code structure, and deliver a polished, professional finish."
)

st.markdown("---")

st.markdown("## 🌱 Ready to Take a Step Further?")

with st.container(border=True):
    st.markdown("### 🗺️ Beyond Your Commute")
    st.write(
        "Public transit is a fantastic start, but the average Singaporean still emits roughly **8,870 kg of CO₂ per year** "
        "across all of their cumulative daily lifestyle habits."
    )
    st.write(
        "To evaluate your environmental impact outside of traveling—including your household utility consumption "
        "(electricity, water, gas) and dining footprint—check out the official calculator managed by SP Group."
    )

    st.link_button(
        "📊 Launch SP Group Carbon Tracker",
        "https://mycarbonfootprint.spgroup.com.sg/",
        use_container_width=True
    )
