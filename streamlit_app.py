import streamlit as st

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

