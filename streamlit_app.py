import streamlit as st
import snowflake
import pandas as pd
import numpy as np
import altair as alt

st.title("🎈 Fast Growing Industries")
st.write(
    "The app is desgiend to help you identify industries that grew fast in recent years and learn more about the growing industry of interest."
)
st.write(
    "Data source: [freecompanydataset](https://app.snowflake.com/marketplace/listing/GZSTZRRVYL2/people-data-labs-free-company-dataset?available=available/)"
)
st.write(
    "Caveat: All the companies in the data have a unique LinkedIn url. Companies with no LinkedIn url are not included in the data."
)

st.divider()
st.write("## Key metrics and scope")
st.write("Industry Growth: Number of founded companies in a year.")
st.write("Growth speed in the past N (N<20) years: Ratio of the number of founded companies in the past N years to that in the past 20 years. The higher the ratio, the faster the industry grew in the past N years.")
st.write("Industries having the ratio > N/20 are identified as fast growing industries.")
st.write('Scope: past 20 years (2004 - 2023)')

# Initialize connection.
conn = st.connection("snowflake")

st.divider()
st.write("## Top industries and growth time trend")
# industries.
df_per_industry = conn.query("select * from REPORT_COMPANY_CNT_PER_INDUSTRY;", ttl=600)
df_per_industry.columns = df_per_industry.columns.str.lower()

st.write(f"There are {df_per_industry.shape[0] - 1} industries. Data source also includes 23.5% companies with unknown industries.")

col1, col2 = st.columns(2)

col1.write("#### Top industries (count of founded companies)")
show_top_industries = col1.slider(
    'Select a range of the number of top industries to show',
    0, df_per_industry.shape[0], 10, 1)
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
col2.write("#### How do the growth change across time?")
flag_exclude_unknown_2 = col2.checkbox(label="Exclude Unknown Industry Data for Company Counts", value=True)
flag_breakdown_industry = col2.checkbox(label="Break down by industry", value=False)
select_starting_year = col2.slider(
    'Select a founded year to begin with',
    1900, 2022, 2003, 1)

if flag_breakdown_industry:
    # count of founded companies change across time, break down by industry
    df2 = conn.query("select founded, cnt_company, cnt_region, cnt_employee, industry from report_company_cnt_per_founded_industry_delta;", ttl=600)
    df2.columns = df2.columns.str.lower()

    if flag_exclude_unknown_2:
        df2 = df2[df2.industry != 'unknown']
    df2 = df2[df2.founded>=select_starting_year].copy()
    # col2.line_chart(data=df2, x="founded", y="cnt_company", x_label = 'founded year', y_label='count of companies', color="industry", height=200, width=220)
    line_chart_1 = alt.Chart(df2).mark_line().encode(
        alt.X('founded', title='founded year'),
        alt.Y('cnt_company', title='count of companies'),
        color=alt.Color('industry', legend=None),
        tooltip=['founded', 'cnt_company', 'industry']
    ).interactive()
    line_chart_1.height=200
    line_chart_1.width=220
    col2.altair_chart(line_chart_1, use_container_width=True)
    
    # line_chart_1b = alt.Chart(df2).mark_line().encode(
    #     alt.X('founded', title='founded year'),
    #     alt.Y('cnt_employee', title='count of employees'),
    #     color=alt.Color('industry', legend=None),
    #     tooltip=['founded', 'cnt_employee', 'industry']
    # ).interactive()
    # line_chart_1b.height=180
    # line_chart_1b.width=220
    # col2.altair_chart(line_chart_1b, use_container_width=True)

    line_chart_1c = alt.Chart(df2).mark_line().encode(
        alt.X('founded', title='founded year'),
        alt.Y('cnt_region', title='count of regions'),
        color=alt.Color('industry', legend=None),
        tooltip=['founded', 'cnt_region', 'industry']
    ).interactive()
    line_chart_1c.height=180
    line_chart_1c.width=220
    col2.altair_chart(line_chart_1c, use_container_width=True)

else:
    if flag_exclude_unknown_2:
        # df_per_year = conn.query("select founded, count(id) as cnt_company, sum(size_est) as cnt_employee from REPORT_COMPANY_CNT_PER_FOUNDED_INDUSTRY where industry!='unknown' group by 1;", ttl=600)
        df_per_year = conn.query("select founded, count(id) as cnt_company, sum(size_est) as cnt_employee, count(distinct region) as cnt_region from int_freecompanydataset where industry!='unknown' group by 1;", ttl=600)
        df_per_year.columns = df_per_year.columns.str.lower()
    else:
        df_per_year = conn.query("select founded, count(id) as cnt_company, sum(size_est) as cnt_employee, count(distinct region) as cnt_region from int_freecompanydataset group by 1;", ttl=600)
        df_per_year.columns = df_per_year.columns.str.lower()
    df_per_year = df_per_year[df_per_year.founded>=select_starting_year].copy()
    # col2.line_chart(data=df_per_year, x="founded", y="cnt_company", x_label = 'founded year', y_label='count of companies', height=180, width=220)
    line_chart_2 = alt.Chart(df_per_year).mark_line().encode(
        alt.X('founded', title='founded year'),
        alt.Y('cnt_company', title='count of companies'),
        tooltip=['founded', 'cnt_company'],
        color=alt.value("#FFAA00")
    ).interactive()
    line_chart_2.height=200
    line_chart_2.width=220
    col2.altair_chart(line_chart_2, use_container_width=True)

    # line_chart_2b = alt.Chart(df_per_year).mark_line().encode(
    #     alt.X('founded', title='founded year'),
    #     alt.Y('cnt_employee', title='count of employees'),
    #     tooltip=['founded', 'cnt_employee'],
    #     color=alt.value("#FFAA00")
    # ).interactive()
    # line_chart_2b.height=180
    # line_chart_2b.width=220
    # col2.altair_chart(line_chart_2b, use_container_width=True)

    line_chart_2c = alt.Chart(df_per_year).mark_line().encode(
        alt.X('founded', title='founded year'),
        alt.Y('cnt_region', title='count of regions'),
        tooltip=['founded', 'cnt_region'],
        color=alt.value("#FFAA00")
    ).interactive()
    line_chart_2c.height=180
    line_chart_2c.width=220
    col2.altair_chart(line_chart_2c, use_container_width=True)


# df_break_down_region = conn.query("select founded, region, count(id) as cnt_company from int_freecompanydataset where region!='unknown' and founded >=2004 group by 1,2;", ttl=600)
# df_break_down_region.columns = df_break_down_region.columns.str.lower()

# line_chart_break_down_region = alt.Chart(df_break_down_region).mark_line().encode(
#         alt.X('founded', title='founded year'),
#         alt.Y('cnt_company', title='count of companies'),
#         color=alt.Color('region', legend=None),
#         tooltip=['founded', 'cnt_company', 'region']
#     ).interactive()
# line_chart_break_down_region.height=180
# line_chart_break_down_region.width=220
# col2.altair_chart(line_chart_break_down_region, use_container_width=True)

    
# linechart of cnt of company in past 20 years and their delta in past 1 year
st.write("## Fast growing industries: High growth ratio in the past N years")
st.write("An industry is a Fast Growing Industry in the past N years (N<20) when it has a ratio (vs. N/20) of count of founded companies in the past N years to that of the past 20 years > N/20.")
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
st.write(f"There are {len(list_industry_growing_past_n_year)} industries grew fast in the past {selected_year_grow} year(s) (ratio > {selected_year_grow}/20).")

col1_growing, col2_growing = st.columns(2)
col1_growing_tile = col1_growing.container(height=600, border=False)
col2_growing_tile = col2_growing.container(height=600, border=False)
# col2_growing_tile.line_chart(data=df_delta_tmp, x="founded", y="cnt_company", color="industry", y_label="count of companies")
line_chart_3 = alt.Chart(df_delta_tmp).mark_line().encode(
        alt.X('founded', title='founded year'),
        alt.Y('cnt_company', title='count of companies'),
        color=alt.Color('industry', legend=None),
        tooltip=['founded', 'cnt_company', 'industry']
    ).interactive()
line_chart_3.height=160
line_chart_3.width=220
col2_growing_tile.altair_chart(line_chart_3, use_container_width=True)

# line_chart_3b = alt.Chart(df_delta_tmp).mark_line().encode(
#         alt.X('founded', title='founded year'),
#         alt.Y('cnt_employee', title='count of employees'),
#         color=alt.Color('industry', legend=None),
#         tooltip=['founded', 'cnt_employee', 'industry']
#     ).interactive()
# line_chart_3b.height=160
# line_chart_3b.width=220
# col2_growing_tile.altair_chart(line_chart_3b, use_container_width=True)

line_chart_3c = alt.Chart(df_delta_tmp).mark_line().encode(
        alt.X('founded', title='founded year'),
        alt.Y('cnt_region', title='count of regions'),
        color=alt.Color('industry', legend=None),
        tooltip=['founded', 'cnt_region', 'industry']
    ).interactive()
line_chart_3c.height=160
line_chart_3c.width=220
col2_growing_tile.altair_chart(line_chart_3c, use_container_width=True)


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
col2_growing_tile.write(f"Among the {len(list_industry_growing_past_n_year)} industires, {df_delta_tmp_1[df_delta_tmp_1.delta_cnt_company>0].shape[0]} industry(ies) grew faster from 2022 to 2023.")
col2_growing_tile.write(f"Industry(ies) grew faster from 2022 to 2023: {df_delta_tmp_1[df_delta_tmp_1.delta_cnt_company>0]['industry'].unique()}")
# st.bar_chart(data=df_delta_tmp_1, x="industry", y="delta_cnt_company", y_label="delta in founded companies from previous year")


# linechart of cnt of company in past 20 years and their delta in past 1 year
st.write("## Learn about selected fast growing industries")
selected_grow_industry = st.selectbox(
    "Choose the fast growing industry of interest",
    list_industry_growing_past_n_year)

st.write(f"#### Break down by company size for {selected_grow_industry}")
# col1_by_size, col2_by_size = st.columns(2)

df_size_all = conn.query("select * from REPORT_COMPANY_CNT_PER_SIZE;", ttl=600)
df_size_all.columns = df_size_all.columns.str.lower()

df_size = conn.query("select * from REPORT_COMPANY_CNT_PER_FOUNDED_INDUSTRY_SIZE where founded >= 2004;", ttl=600)
df_size.columns = df_size.columns.str.lower()
df_size = df_size[df_size.industry == selected_grow_industry].copy()

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
    column = alt.Column('size_order:O', title="Break down by company size", spacing = 5, header = alt.Header(labelOrient = "bottom")),
    x =alt.X('variable', title="company size",  axis=None),
    y =alt.Y('value', title="percent companies out of all", sort=alt.EncodingSortField(
        field='value',
        order='descending'
    )),
    color= alt.Color('variable')
).configure_view(stroke='transparent').properties(
    title=f"Compare {selected_grow_industry} vs. all industires"
)
chart_compare_to_all.height=100
# chart_compare_to_all.width=200
st.altair_chart(chart_compare_to_all)

if selected_year_grow == "10":
    df_size_past = df_size[df_size.founded >= 2023-10+1].copy()
elif selected_year_grow == "5":
    df_size_past = df_size[df_size.founded >= 2023-5+1].copy()
elif selected_year_grow == "3":
    df_size_past = df_size[df_size.founded >= 2023-3+1].copy()
elif selected_year_grow == "1":
    df_size_past = df_size[df_size.founded >= 2023-1+1].copy()

df_size_past_agg = df_size_past.groupby('size')['cnt_company'].sum().reset_index()
df_size_past_agg['pct_company'] = df_size_past_agg['cnt_company']*100.0/df_size_past_agg['cnt_company'].sum()

# col1_by_size.line_chart(data=df_size, x="founded", y="cnt_company", color="size", y_label="count of companies")
line_chart_by_size = alt.Chart(df_size_past_agg).mark_bar(interpolate='basis').encode(
    alt.X('size', title='size'),
    alt.Y('pct_company', title='percent of companies'),
    # color='size:N'
).properties(
    title=f"Growth in the past {selected_year_grow} year(s)"
)
line_chart_by_size.height=300
line_chart_by_size.width=500
st.altair_chart(line_chart_by_size)

# line_chart_by_size2 = alt.Chart(df_size_past_agg).mark_bar(interpolate='basis').encode(
#     alt.X('size', title='size'),
#     alt.Y('cnt_employee', title='count of employees'),
#     # color='size:N'
# )
# line_chart_by_size2.height=300
# # line_chart_by_size2.width=200
# st.altair_chart(line_chart_by_size2)

# line_chart_by_size3 = alt.Chart(df_size_past_agg).mark_line(interpolate='basis').encode(
#     alt.X('size', title='size'),
#     alt.Y('cnt_region', title='count of regions'),
#     # color='size:N'
# )
# line_chart_by_size3.height=300
# # line_chart_by_size3.width=200
# st.altair_chart(line_chart_by_size3)


st.write(f"#### Break down by country for {selected_grow_industry}")
df_country = conn.query("select * from REPORT_COMPANY_CNT_PER_FOUNDED_INDUSTRY_COUNTRY where founded >= 2004;", ttl=600)
df_country.columns = df_country.columns.str.lower()
df_country = df_country[df_country.industry == selected_grow_industry].copy()
st.write(f"There are {round(df_country[df_country.country.isna()].shape[0]/df_country.shape[0],3)*100}% of companies missing country data.")
df_country.fillna('missing country data', inplace=True)
df_country_tmp = df_country.groupby('country')['cnt_company'].sum().reset_index()
df_country_tmp.sort_values(by=['cnt_company'], ascending=False, inplace=True)
list_country_tmp = list(df_country_tmp.country.values)
list_country_tmp = list_country_tmp[:5]
st.write(f"The top 5 countries where the companies are from: {list_country_tmp}")
if 'missing country data' in list_country_tmp:
    df_country_tmp2 = df_country[df_country.country.isin(list_country_tmp)].copy()
else:
    list_country_tmp.append('missing country data')
    df_country_tmp2 = df_country[df_country.country.isin(list_country_tmp)].copy()
st.line_chart(data=df_country_tmp2, x="founded", y="cnt_company", color="country", y_label="count of companies")
# st.line_chart(data=df_country_tmp2, x="founded", y="cnt_employee", color="country", y_label="count of employees")



# linechart of cnt of company in past 20 years and their delta in past 1 year
st.write("## Industries having more founded companies in 2023 compared to that in 2022")
list_industry_positive_delta_2023 = list(df_delta[(df_delta.founded == 2023)&(df_delta.delta_cnt_company > 0)&(df_delta.cnt_company > 0)]['industry'].unique())
df_delta_tmp_2 = df_delta[df_delta.industry.isin(list_industry_positive_delta_2023)].copy()
st.write(f"There are {len(list_industry_positive_delta_2023)} industries growing faster from 2022 to 2023: {list_industry_positive_delta_2023}")

select_starting_year_2 = st.slider(
    'Select a founded year to begin with ',
    2004, 2022, 2004, 1)
df_delta_tmp_2 = df_delta_tmp_2[df_delta_tmp_2.founded >=select_starting_year_2].copy()
st.line_chart(data=df_delta_tmp_2, x="founded", y="cnt_company", color="industry", y_label="count of companies")


# get user feedback
from streamlit_feedback import streamlit_feedback
st.write("Please provide your feedback. Thank you!")
feedback = streamlit_feedback(
    feedback_type="faces",
    optional_text_label="[Optional] Please provide an explanation",
)

