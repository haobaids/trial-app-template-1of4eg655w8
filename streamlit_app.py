import streamlit as st
import snowflake
import pandas as pd
import numpy as np
import altair as alt

st.title("🎈 Growth Industry Area")
st.write(
    "The app is desgiend to help you identify industry areas that are at the growth stage and learn more about the industry of interest."
)
st.write(
    "Data source: [freecompanydataset](https://app.snowflake.com/marketplace/listing/GZSTZRRVYL2/people-data-labs-free-company-dataset?available=available/)"
)
 



# Initialize connection.
conn = st.connection("snowflake")

st.divider()
st.write("## Distribution of industries and founded years")
# industries.
df_per_industry = conn.query("select * from REPORT_COMPANY_CNT_PER_INDUSTRY;", ttl=600)
df_per_industry.columns = df_per_industry.columns.str.lower()

st.write(f"There are {df_per_industry.shape[0] - 1} industries. Data source also includes 23.5% companies with unknown industries.")

col1, col2 = st.columns(2)

col1.write("#### Top industries (count of companies)")
show_top_industries = col1.slider(
    'Select a range of the number of top industries to show',
    0, df_per_industry.shape[0], 5, 1)
flag_exclude_unknown_1 = col1.checkbox(label="Exclude Unknown Industry Data for top industires", value=True)

if flag_exclude_unknown_1:
    df_per_industry = df_per_industry[df_per_industry.industry != "unknown"].copy()
df_per_industry2 = pd.melt(df_per_industry.reset_index(), id_vars=["industry"])
df_per_industry2.sort_values(by="value", ascending=False, inplace=True)
df_per_industry2 = df_per_industry2[:int(show_top_industries)]

# Horizontal stacked bar chart
chart = (
    alt.Chart(df_per_industry2)
    .mark_bar()
    .encode(
        x=alt.X("value", type="quantitative", title="", sort=alt.EncodingSortField(
        field='value',
        order='descending'
    )),
        y=alt.Y("industry", type="nominal", title="", sort=alt.EncodingSortField(
        field='value',
        order='descending'
    )),
        order=alt.Order("value", sort="descending"),
    )
)

col1.altair_chart(chart, use_container_width=True)

container_1 = col2.container(border=False, height=700)
# count of founded companies change across time.
container_1.write("##### How do the count of founded companies change across time?")
flag_exclude_unknown_2 = container_1.checkbox(label="Exclude Unknown Industry Data for Company Counts", value=True)

if flag_exclude_unknown_2:
    df_per_year = conn.query("select founded, sum(cnt_company) as cnt_company from REPORT_COMPANY_CNT_PER_FOUNDED_INDUSTRY where industry!='unknown' group by 1;", ttl=600)
    df_per_year.columns = df_per_year.columns.str.lower()
else:
    df_per_year = conn.query("select founded, cnt_company from report_company_cnt_per_founded;", ttl=600)
    df_per_year.columns = df_per_year.columns.str.lower()
container_1.line_chart(data=df_per_year, x="founded", y="cnt_company", x_label = 'founded year', y_label='count of companies', height=180, width=220)


# count of founded companies change across time, break down by industry
container_1.write("##### Break down by industry")
df2 = conn.query("select founded, cnt_company, industry from report_company_cnt_per_founded_industry_delta;", ttl=600)
df2.columns = df2.columns.str.lower()
flag_exclude_unknown_3 = container_1.checkbox(label="Exclude Unknown Industry Data for break down", value=False)

if flag_exclude_unknown_3:
    df2 = df2[df2.industry != 'unknown']
container_1.line_chart(data=df2, x="founded", y="cnt_company", x_label = 'founded year', y_label='count of companies', color="industry", height=200, width=220)


# scatterplot of cnt of company in past 20 years and their delta in past 1 year
st.write("# Distribution of industry in count of founded companies in past 20 years and the ratio of new company in past 1 year")
flag_exclude_unknown = st.checkbox(label="Exclude Unknown Industry Data for Industry Distribution", value=True)
st.write("color = industry, size = count of founded companies in past 3 years")
df3 = conn.query("select * from REPORT_COMPANY_CNT_PAST_20_YEAR;", ttl=600)
df3.columns = df3.columns.str.lower()
if flag_exclude_unknown:
    df3_tmp = df3[df3.industry != "unknown"]
    st.scatter_chart(data=df3_tmp,  color="industry", x="cnt_company_past_20_year", y="cnt_company_past_1_year", x_label="Founded companies in past 20 years", y_label="Foundedcompanies in past 1 year", size="pct_company_past_3_year")
else:
    st.scatter_chart(data=df3,  color="industry", x="cnt_company_past_20_year", y="cnt_company_past_1_year", x_label="Founded companies in past 20 years", y_label="Foundedcompanies in past 1 year", size="pct_company_past_3_year")

# df2

# for row in df2.itertuples():
#     st.write(f"{row.NAME} is in {row.COUNTRY} and has size of {row.SIZE}")



# if st.button("embed"):
#     result = conn.query(text_to_embed)
#     result


# radio widget to take inputs from mulitple options
genre = st.radio(
    "What's your favorite movie genre",
    ('Comedy', 'Drama', 'Documentary'))

if genre == 'Comedy':
    st.write('You selected comedy.')
else:
    st.write("You didn't select comedy.")

st.write(
    "Test again! Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)