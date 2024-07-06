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
st.write(
    "Caveat: The data may not cover all the industries in all countries. All the data have a unique LinkedIn url. However, in the real world, there are many companies do not have a LinkedIn url. And it is possible that there are industries or countries where companies are less likely to have a linkedin url. Thus, the data is a biased sample of companies."
)

st.divider()
st.write("## Key metric")
st.write("Industries Growth is estimated by the ratio of founded companies in the past N (N<20) years to that in the past 20 years. The higher the ratio, the more growth the industry had in the past N years.")


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

# count of founded companies change across time.
col2.write("#### How do the count of founded companies change across time?")
flag_exclude_unknown_2 = col2.checkbox(label="Exclude Unknown Industry Data for Company Counts", value=True)
flag_breakdown_industry = col2.checkbox(label="Break down by industry", value=False)
select_starting_year = col2.slider(
    'Select a founded year to begin with',
    1900, 2022, 2003, 1)

if flag_breakdown_industry:
    # count of founded companies change across time, break down by industry
    df2 = conn.query("select founded, cnt_company, industry from report_company_cnt_per_founded_industry_delta;", ttl=600)
    df2.columns = df2.columns.str.lower()

    if flag_exclude_unknown_2:
        df2 = df2[df2.industry != 'unknown']
    df2 = df2[df2.founded>=select_starting_year].copy()
    col2.line_chart(data=df2, x="founded", y="cnt_company", x_label = 'founded year', y_label='count of companies', color="industry", height=200, width=220)
else:
    if flag_exclude_unknown_2:
        df_per_year = conn.query("select founded, sum(cnt_company) as cnt_company from REPORT_COMPANY_CNT_PER_FOUNDED_INDUSTRY where industry!='unknown' group by 1;", ttl=600)
        df_per_year.columns = df_per_year.columns.str.lower()
    else:
        df_per_year = conn.query("select founded, cnt_company from report_company_cnt_per_founded;", ttl=600)
        df_per_year.columns = df_per_year.columns.str.lower()
    df_per_year = df_per_year[df_per_year.founded>=select_starting_year].copy()
    col2.line_chart(data=df_per_year, x="founded", y="cnt_company", x_label = 'founded year', y_label='count of companies', height=180, width=220)


# linechart of cnt of company in past 20 years and their delta in past 1 year
st.write("## Growth industries: Long term time trend in the past 20 years")
st.write("Growth industries = Industries having a higher ratio (vs. N/20) of founded companies in the past N (N<20) years compared to the past 20 years.")
selected_year_grow = st.selectbox(
    "Choose the past N years to check",
    ("10", "5", "3", "1"), index=3)
flag_exclude_unknown_3 = st.checkbox(label="Exclude Unknown Industry Data for Time Trend", value=True)
df_ratio_past_20_year = conn.query("select * from REPORT_COMPANY_CNT_PAST_20_YEAR;", ttl=600)
df_ratio_past_20_year.columns = df_ratio_past_20_year.columns.str.lower()

df_delta = conn.query("select * from report_company_cnt_per_founded_industry_delta where founded>2004;", ttl=600)
df_delta.columns = df_delta.columns.str.lower()

if flag_exclude_unknown_3:
    df_ratio_past_20_year = df_ratio_past_20_year[df_ratio_past_20_year.industry != 'unknown'].copy()
if selected_year_grow == "10":
    list_industry_growing_past_n_year = list(df_ratio_past_20_year[df_ratio_past_20_year.pct_company_past_10_year > 10/20]['industry'].unique())
elif selected_year_grow == "5":
    list_industry_growing_past_n_year = list(df_ratio_past_20_year[df_ratio_past_20_year.pct_company_past_5_year > 5/20]['industry'].unique())
elif selected_year_grow == "3":
    list_industry_growing_past_n_year = list(df_ratio_past_20_year[df_ratio_past_20_year.pct_company_past_3_year > 3/20]['industry'].unique())
elif selected_year_grow == "1":
    list_industry_growing_past_n_year = list(df_ratio_past_20_year[df_ratio_past_20_year.pct_company_past_1_year > 1/20]['industry'].unique())
else:
    list_industry_growing_past_n_year = []
df_delta_tmp = df_delta[df_delta.industry.isin(list_industry_growing_past_n_year)].copy()
if selected_year_grow == "10":
    var_size = 'pct_company_past_10_year'
elif selected_year_grow == "5":
    var_size = 'pct_company_past_5_year'
elif selected_year_grow == "3":
    var_size = 'pct_company_past_3_year'
elif selected_year_grow == "1":
    var_size = 'pct_company_past_1_year'
# df_delta_tmp = df_delta_tmp.merge(df_ratio_past_20_year, on='industry', how='left')
st.write(f"There are {len(list_industry_growing_past_n_year)} industries.")

col1_growing, col2_growing = st.columns(2)
col1_growing_tile = col1_growing.container(height=500, border=False)
col2_growing_tile = col2_growing.container(height=500, border=False)
col2_growing_tile.line_chart(data=df_delta_tmp, x="founded", y="cnt_company", color="industry", y_label="count of companies")

df_ratio_past_20_year_tmp = df_ratio_past_20_year[df_ratio_past_20_year.industry.isin(list_industry_growing_past_n_year)].copy()

df_ratio_past_20_year_tmp = df_ratio_past_20_year_tmp[['industry',var_size]].copy()
df_ratio_past_20_year_tmp2 = pd.melt(df_ratio_past_20_year_tmp.reset_index(), id_vars=["industry"], value_vars=[var_size])
df_ratio_past_20_year_tmp2.sort_values(by="value", ascending=False, inplace=True)

chart_ratio = (
    alt.Chart(df_ratio_past_20_year_tmp2)
    .mark_bar()
    .encode(
        x=alt.X("value", type="quantitative", title="ratio of companies in the past N years vs. 20 years", sort=alt.EncodingSortField(
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
col1_growing_tile.altair_chart(chart_ratio, use_container_width=True)

df_delta_tmp_1 = df_delta_tmp[df_delta_tmp.founded == 2023]
col2_growing_tile.write(f"Among the {len(list_industry_growing_past_n_year)} industires, {df_delta_tmp_1[df_delta_tmp_1.delta_cnt_company>0].shape[0]} industries are growing from 2022 to 2023.")
col2_growing_tile.write(f"Industry growing from 2022 to 2023: {df_delta_tmp_1[df_delta_tmp_1.delta_cnt_company>0]['industry'].unique()}")
# st.bar_chart(data=df_delta_tmp_1, x="industry", y="delta_cnt_company", y_label="delta in founded companies from previous year")


# linechart of cnt of company in past 20 years and their delta in past 1 year
st.write("## Learn about selected growth industries")
selected_grow_industry = st.selectbox(
    "Choose the growth industry of interest",
    list_industry_growing_past_n_year)

st.write("#### Break down by company size")
col1_by_size, col2_by_size = st.columns(2)
df_size = conn.query("select * from REPORT_COMPANY_CNT_PER_FOUNDED_INDUSTRY_SIZE where founded >= 2004;", ttl=600)
df_size.columns = df_size.columns.str.lower()
df_size = df_size[df_size.industry == selected_grow_industry].copy()
# col1_by_size.line_chart(data=df_size, x="founded", y="cnt_company", color="size", y_label="count of companies")
line_chart_by_size = alt.Chart(df_size).mark_line(interpolate='basis').encode(
    alt.X('founded', title='founded'),
    alt.Y('cnt_company', title='count of companies'),
    color='size:N'
).properties(
    title='Time trend'
)
col1_by_size.altair_chart(line_chart_by_size)

df_size_all = conn.query("select * from REPORT_COMPANY_CNT_PER_SIZE;", ttl=600)
df_size_all.columns = df_size_all.columns.str.lower()
df_size_agg = df_size.groupby('size')['cnt_company'].sum().reset_index()
df_size_agg = df_size_agg.merge(df_size_all, on='size', how='right')
for i_ in range(df_size_agg.shape[0]):
    df_size_agg.loc[i_, 'size_order'] = int(df_size_agg.loc[i_, 'size'].split('-')[0].split('+')[0])
    df_size_agg.loc[i_, 'pct_company_x'] = df_size_agg.loc[i_, 'cnt_company_x']*100.0/df_size_agg['cnt_company_x'].sum()
    df_size_agg.loc[i_, 'pct_company_y'] = df_size_agg.loc[i_, 'cnt_company_y']*100.0/df_size_agg['cnt_company_y'].sum()
df_size_agg.sort_values(by=['size_order'], inplace=True)
df_size_agg.rename(columns={'pct_company_x':'pct_company_industry', 'pct_company_y':'pct_company_all'}, inplace=True)
df_size_agg_transposed=pd.melt(df_size_agg, id_vars=['size_order'] , value_vars=['pct_company_industry','pct_company_all'])

chart_compare_to_all = alt.Chart(df_size_agg_transposed).mark_bar(
    opacity=1,
    ).encode(
    column = alt.Column('size_order:O', title="Compare the industry vs. all", spacing = 5, header = alt.Header(labelOrient = "bottom")),
    x =alt.X('variable', title="company size",  axis=None),
    y =alt.Y('value', title="percent companies out of all", sort=alt.EncodingSortField(
        field='value',
        order='descending'
    )),
    color= alt.Color('variable')
).configure_view(stroke='transparent').properties(
    title='Compare the industry vs. all'
)
col2_by_size.altair_chart(chart_compare_to_all)


st.write("#### Break down by country")
df_country = conn.query("select * from REPORT_COMPANY_CNT_PER_FOUNDED_INDUSTRY_COUNTRY where founded >= 2004;", ttl=600)
df_country.columns = df_country.columns.str.lower()
df_country = df_country[df_country.industry == selected_grow_industry].copy()
st.write(f"There are {round(df_country[df_country.country.isna()].shape[0]/df_country.shape[0],3)*100}% of companies missing country data.")
df_country.fillna('missing country data', inplace=True)
df_country_tmp = df_country.groupby('country')['cnt_company'].sum().reset_index()
df_country_tmp.sort_values(by=['cnt_company'], ascending=False, inplace=True)
list_country_tmp = list(df_country_tmp.country.values)
list_country_tmp = list_country_tmp[:5]
st.write(f"The top 5 countries where the companies are from in the past are: {list_country_tmp}")
if 'missing country data' in list_country_tmp:
    df_country_tmp2 = df_country[df_country.country.isin(list_country_tmp)].copy()
else:
    list_country_tmp.append('missing country data')
    df_country_tmp2 = df_country[df_country.country.isin(list_country_tmp)].copy()
st.line_chart(data=df_country_tmp2, x="founded", y="cnt_company", color="country", y_label="count of companies")



# linechart of cnt of company in past 20 years and their delta in past 1 year
st.write("## Growth industries: Short term growth from 2022 to 2023")
list_industry_positive_delta_2023 = list(df_delta[(df_delta.founded == 2023)&(df_delta.delta_cnt_company > 0)&(df_delta.cnt_company > 0)]['industry'].unique())
df_delta_tmp_2 = df_delta[df_delta.industry.isin(list_industry_positive_delta_2023)].copy()
st.write(f"There are {len(list_industry_positive_delta_2023)} industries growing from 2022 to 2023: {list_industry_positive_delta_2023}")

select_starting_year_2 = st.slider(
    'Select a founded year to begin with ',
    2004, 2022, 2004, 1)
df_delta_tmp_2 = df_delta_tmp_2[df_delta_tmp_2.founded >=select_starting_year_2].copy()
st.line_chart(data=df_delta_tmp_2, x="founded", y="cnt_company", color="industry", y_label="count of companies")



# # scatterplot of cnt of company in past 20 years and their delta in past 1 year
# st.write("## Distribution of industry in count of founded companies in the past 20 years and the ratio of new company in the past 1 year")
# flag_exclude_unknown = st.checkbox(label="Exclude Unknown Industry Data for Industry Distribution", value=True)
# st.write("color = industry, size = count of founded companies in the past 3 years")
# df3 = conn.query("select * from REPORT_COMPANY_CNT_PAST_20_YEAR;", ttl=600)
# df3.columns = df3.columns.str.lower()
# if flag_exclude_unknown:
#     df3_tmp = df3[df3.industry != "unknown"]
#     st.scatter_chart(data=df3_tmp,  color="industry", x="cnt_company_past_20_year", y="cnt_company_past_1_year", x_label="Founded companies in the past 20 years", y_label="Foundedcompanies in the past 1 year", size="pct_company_past_3_year", height=500, width=500)
# else:
#     st.scatter_chart(data=df3,  color="industry", x="cnt_company_past_20_year", y="cnt_company_past_1_year", x_label="Founded companies in the past 20 years", y_label="Foundedcompanies in the past 1 year", size="pct_company_past_3_year", height=500, width=500)




# # df2

# # for row in df2.itertuples():
# #     st.write(f"{row.NAME} is in {row.COUNTRY} and has size of {row.SIZE}")



# # if st.button("embed"):
# #     result = conn.query(text_to_embed)
# #     result


# # radio widget to take inputs from mulitple options
# genre = st.radio(
#     "What's your favorite movie genre",
#     ('Comedy', 'Drama', 'Documentary'))

# if genre == 'Comedy':
#     st.write('You selected comedy.')
# else:
#     st.write("You didn't select comedy.")

# st.write(
#     "Test again! Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
# )