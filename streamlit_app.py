import streamlit as st
import snowflake

st.title("🎈 My new app")
st.write(
    "Test again! Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
st.text("This is some text")
code = '''def hello():
    print("Hello, Streamlit!")'''

st.code(code, language='python')

import pandas as pd
import numpy as np


chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c'])
st.dataframe(chart_data)
st.line_chart(chart_data)

# radio widget to take inputs from mulitple options
genre = st.radio(
    "What's your favorite movie genre",
    ('Comedy', 'Drama', 'Documentary'))

if genre == 'Comedy':
    st.write('You selected comedy.')
else:
    st.write("You didn't select comedy.")


# Initialize connection.
conn = st.connection("snowflake")

# Perform query.
df2 = conn.query("select * from freecompanydataset limit 10;", ttl=600)


# @st.cache_data
# def load_table():
#     session = conn.session()
#     return session.table("mytable").to_pandas()

# df2 = load_table()

for row in df2.itertuples():
    st.write(f"{row.NAME} is in {row.COUNTRY} and has size of {row.SIZE}")