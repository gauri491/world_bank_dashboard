# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "altair==6.3.0",
#     "marimo>=0.25.2",
#     "numpy==2.5.5",
#     "pandas==3.1.1",
#     "pingouin==0.7.0",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import altair as alt
    import numpy as np
    import pingouin as pg

    return alt, mo, pd, pg


@app.cell
def _(pd):
    base_url = "https://docs.google.com/spreadsheets/d/"
    doc_id = "1YY5iwL8J53umfHMNhJd1m-MbRPtRpX65oyxhq1KjzuI/"
    doc_format = "export?format=csv"

    url = base_url + doc_id + doc_format

    df_raw = pd.read_csv(url)
    return (df_raw,)


@app.cell
def _(df_raw, pd):
    # filter years

    df_raw["date"] = pd.to_datetime(df_raw["date"])
    df_raw["year"] = df_raw["date"].dt.year

    # countries
    countries = ["India", "Mexico", "Germany", "Japan", "Ethiopia"]

    # create the column of gdp_per_capita

    df_raw["gdp_per_capita"] = df_raw["GDP_current_US"] / df_raw["population"]

    df= df_raw[(df_raw["year"] >= 2000) & (df_raw["year"] <= 2020)]
    return countries, df


@app.cell
def _(mo):
    ## asked AI to help with the formatting

    a = mo.Html("""
    <div style="
        background: #1B4332;
        padding: 22px 26px;
        border-radius: 14px;
        color: white;
        margin-bottom: 14px;
    ">
        <div style="
            font-size: 13px;
            color: #B7D6C2;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 8px;
        ">
            Group 8
        </div>

        <div style="
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 12px;
        ">
            Economic Growth Destroys Forests?
        </div>

        <div style="
            font-size: 14px;
            color: #E0EDE5;
            margin-bottom: 12px;
        ">
            Our claim: Economic growth destroys forests.
        </div>

        <div style="
            border-top: 1px solid #52796A;
            padding-top: 10px;
            font-size: 13px;
        ">
            <b>Contributing members</b><br>
            Aditi Parab · Sanskriti Vijayvargiya · Gauri Chitnis
        </div>
    </div>

    <div style="
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
    ">

        <div style="
            flex: 1;
            min-width: 180px;
            background: #E8F1EB;
            padding: 16px;
            border-radius: 12px;
            border-left: 4px solid #40916C;
            color: #243B2F;
        ">
            <div style="font-weight: 700; margin-bottom: 6px;">
                WHY THIS CLAIM?
            </div>
            <div style="font-size: 13px;">
                Economic growth can increase demand for land, resources, and infrastructure, which may contribute to deforestation. We want to examine whether the data supports this relationship
            </div>
        </div>

        <div style="
            flex: 1;
            min-width: 180px;
            background: #F0F3E8;
            padding: 16px;
            border-radius: 12px;
            border-left: 4px solid #87986A;
            color: #243B2F;
        ">
            <div style="font-weight: 700; margin-bottom: 6px;">
                WHY THESE INDICATORS?
            </div>
            <div style="font-size: 13px;">
                Forest area indicates the extent of forest cover, while GDP per capita, agricultural land, and population density help assess economic, land-use, and demographic patterns
            </div>
        </div>

        <div style="
            flex: 1;
            min-width: 180px;
            background: #F5EEE3;
            padding: 16px;
            border-radius: 12px;
            border-left: 4px solid #BC8A56;
            color: #443625;
        ">
            <div style="font-weight: 700; margin-bottom: 6px;">
                WHY THESE COUNTRIES?
            </div>
            <div style="font-size: 13px;">
                India, Mexico, Germany, Japan and Ethiopia represent
                different development levels and regions, allowing us
                to compare diverse economic and forest patterns
            </div>
        </div>

    </div>
    """)
    return (a,)


@app.cell
def _(mo):
    # comparison indicator dropdown

    comparison_dropdown = mo.ui.dropdown(
        options={
            "GDP per capita (US$)": "gdp_per_capita",
            "Agricultural land (%)": "agricultural_land%",
            "Population density (people/km²)": "population_density"
        },
        value="GDP per capita (US$)",
        label="Compare forest area with"
    )

    # year slider

    period_slider = mo.ui.range_slider(
        start=2000,
        stop=2020,
        value=(2000, 2020),
        label="Period"
    )

    b = mo.hstack([comparison_dropdown, period_slider])
    return b, comparison_dropdown, period_slider


@app.cell
def _(comparison_dropdown, countries, df, period_slider):
    selected_indicator = comparison_dropdown.value

    start_year, end_year = period_slider.value

    filtered_df = df[(df["year"].between(start_year, end_year)) & (df["country"].isin(countries))]
    return end_year, filtered_df, selected_indicator, start_year


@app.cell
def _(alt, filtered_df, selected_indicator):
    scatter = alt.Chart(filtered_df).mark_circle(size=80).encode(
        x=alt.X(selected_indicator, title=selected_indicator),
        y=alt.Y("forest_land%", title="Forest  Land (%)"),
        color="country",
        tooltip=["country", "year", selected_indicator, "forest_land%"]
    )

    trendline = alt.Chart(filtered_df).transform_regression(
        selected_indicator,
        "forest_land%",
        groupby=["country"]
    ).mark_line().encode(
        x=selected_indicator,
        y="forest_land%",
        color="country"
    )

    (scatter + trendline).properties(
        width=800,
        height=500,
        title="Forest Land vs Selected Indicator"
    ).configure_axis(
        grid=True,
        gridOpacity=0.7,
        labelFontSize=12,
        titleFontSize=14
    )
    return


@app.cell
def _(countries, filtered_df, pd, pg, selected_indicator):
    results = []

    for country in countries:
        country_df = filtered_df[filtered_df["country"] == country]

        country_df = country_df[[selected_indicator, "forest_land%"]].dropna()

        corr = pg.corr(
            country_df[selected_indicator],
            country_df["forest_land%"],
            method="spearman"
        )

        results.append({
            "Country": country,
            "n (Years)": corr["n"].iloc[0],
            "r": corr["r"].iloc[0],
            "p-value": corr["p_val"].iloc[0],
            "95% CI": corr["CI95"].iloc[0]
        })

    correlation_table = pd.DataFrame(results)

    correlation_table.round(3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ***Correlation method: Spearman***

    We used **Spearman correlation** because it measures whether two indicators tend to rise or fall together without assuming a straight line.
    Some countries show curved or skewed patterns (for example Ethiopia's forest land), and Spearman is less affected by such shapes and by a few extreme years than Pearson.
    """)
    return


@app.cell
def _(mo):
    changes_switch = mo.ui.switch(label="Test year-to-year changes instead of values (removes shared trends)")
    return (changes_switch,)


@app.cell
def _(
    changes_switch,
    comparison_dropdown,
    countries,
    end_year,
    filtered_df,
    mo,
    pd,
    pg,
    selected_indicator,
    start_year,
):
    ##
    x_label = comparison_dropdown.selected_key

    use_changes = changes_switch.value
    mode_name = "year-to-year changes" if use_changes else "yearly values"

    safe_rows = []
    skipped = []

    for _country in countries:
        _data = (
            filtered_df[filtered_df["country"] == _country][["year", selected_indicator, "forest_land%"]]
            .dropna()
            .sort_values("year")
        )
        if use_changes:
            _data = _data.assign(
                gap=_data["year"].diff(),
                x=_data[selected_indicator].diff(),
                y=_data["forest_land%"].diff(),
            )
            _pair = _data[_data["gap"] == 1][["x", "y"]].dropna()
        else:
            _pair = _data.rename(columns={selected_indicator: "x", "forest_land%": "y"})[["x", "y"]]

        _n = len(_pair)

        # check 1: at least 5 years with data
        if _n < 5:
            skipped.append(f"**{_country}**: only {_n} usable observation(s) for this pair and period, so no test was run.")
            continue

        # check 2: an indicator that never changes has no correlation
        if _pair["x"].nunique() < 2 or _pair["y"].nunique() < 2:
            skipped.append(f"**{_country}**: one of the two series does not change in this period, so no correlation can be calculated.")
            continue

        _corr = pg.corr(x=_pair["x"], y=_pair["y"], method="spearman")
        _r = float(_corr["r"].iloc[0])

        # check 3: if pingouin still gives NaN, do not show it
        if pd.isna(_r):
            skipped.append(f"**{_country}**: the test did not give a result for this period.")
            continue

        _ci = _corr["CI95"].iloc[0]
        safe_rows.append({
            "Country": _country,
            "n": int(_corr["n"].iloc[0]),
            "r": _r,
            "p": float(_corr["p_val"].iloc[0]),
            "ci_low": float(_ci[0]),
            "ci_high": float(_ci[1]),
        })

    # raw numbers
    safe_table = pd.DataFrame(safe_rows)

    # strength of |r|
    def _strength(r):
        if abs(r) < 0.1:
            return "Negligible"
        elif abs(r) < 0.3:
            return "Small"
        elif abs(r) < 0.5:
            return "Moderate"
        else:
            return "Large"

    if len(safe_table) > 0:
        display_table = pd.DataFrame({
            "Country": safe_table["Country"],
            "n": safe_table["n"],
            "r": safe_table["r"].round(2),
            "p-value": safe_table["p"].apply(lambda p: "<0.001" if p < 0.001 else f"{p:.3f}"),
            "95% CI": [f"[{lo:.2f}, {hi:.2f}]" for lo, hi in zip(safe_table["ci_low"], safe_table["ci_high"])],
            "Strength": safe_table["r"].apply(_strength),
            "Significant (5%)": safe_table["p"].apply(lambda p: "Yes" if p < 0.05 else "No"),
        })
        _table = mo.ui.table(display_table, selection=None, pagination=False)
    else:
        _table = mo.callout(mo.md("No country has enough data for this indicator and period."), kind="danger")

    _messages = [mo.callout(mo.md(m), kind="warn") for m in skipped]

    table_view = mo.vstack([
        mo.md(f"**Spearman correlation of {mode_name}, {start_year}–{end_year}**"),
        _table,
        *_messages,
    ])
    return mode_name, safe_table, table_view, use_changes, x_label


@app.cell
def _(mo, mode_name, safe_table, use_changes, x_label):
    ##
    n_valid = len(safe_table)

    if n_valid == 0:
        verdict_view = mo.callout(
            mo.md("**Verdict: the data cannot tell.** No country has enough data for this choice."),
            kind="warn",
        )
    else:
        _neg = safe_table["r"] < 0
        _pos = safe_table["r"] > 0
        _sig = safe_table["p"] < 0.05

        n_neg = int(_neg.sum())
        n_neg_sig = int((_neg & _sig).sum())
        n_pos_sig = int((_pos & _sig).sum())
        n_large = int((_neg & (safe_table["r"].abs() > 0.5)).sum())

        # decide the verdict
        if n_valid < 3:
            verdict_word = "the data cannot tell, because fewer than 3 countries could be tested"
        elif n_neg_sig >= (2 / 3) * n_valid:
            verdict_word = "the data supports the claim"
        elif n_pos_sig >= (2 / 3) * n_valid:
            verdict_word = "the data contradicts the claim"
        elif n_neg_sig == 0 and n_pos_sig == 0:
            verdict_word = "the data cannot tell, because no country shows a significant correlation"
        else:
            verdict_word = "the data gives a mixed picture"

        _very_strong = safe_table.loc[safe_table["r"].abs() > 0.9, "Country"].tolist()
        if use_changes:
            last_sentence = (
                "Year-to-year changes remove the shared trend over time, but a correlation "
                "still cannot show cause: a third factor can drive both."
            )
        elif len(_very_strong) > 0:
            last_sentence = (
                "A correlation cannot show cause, and for " + ", ".join(_very_strong)
                + " (|r| above 0.9) both indicators may simply follow time, so check the Over time tab "
                "or switch to year-to-year changes."
            )
        else:
            last_sentence = (
                "A correlation cannot show cause: a third factor or a shared trend over time "
                "can create it, and the p-values are too optimistic because years are not independent."
            )

        verdict_text = (
            f"Looking at {mode_name}, in **{n_neg} of {n_valid}** countries a higher value of '{x_label}' "
            f"goes with less forest, as the claim expects. "
            f"{n_neg_sig} of them are significant (p < 0.05) and {n_large} show a large correlation (|r| > 0.5), "
            f"while {n_pos_sig} of the {n_valid} countries show a significant correlation in the opposite direction. "
            f"**Verdict: {verdict_word}.** "
            f"{last_sentence}"
        )

        verdict_view = mo.callout(mo.md(verdict_text), kind="info")
    return (verdict_view,)


@app.cell
def _(alt, filtered_df, mo, selected_indicator, x_label):
    ##
    if selected_indicator == "gdp_per_capita":
        _y_scale = alt.Scale(type="log")
    else:
        _y_scale = alt.Scale(zero=False)

    forest_lines = alt.Chart(filtered_df).mark_line(point=True).encode(
        x=alt.X("year:Q", title="Year", axis=alt.Axis(format="d")),
        y=alt.Y("forest_land%:Q", title="Forest land (% of land area)", scale=alt.Scale(zero=False)),
        color=alt.Color("country:N", title="Country"),
        tooltip=[
            alt.Tooltip("country:N", title="Country"),
            alt.Tooltip("year:Q", title="Year", format="d"),
            alt.Tooltip("forest_land%:Q", title="Forest land (%)", format=".2f"),
        ],
    ).properties(width=380, height=250, title="Forest land over time")

    indicator_lines = alt.Chart(filtered_df).mark_line(point=True).encode(
        x=alt.X("year:Q", title="Year", axis=alt.Axis(format="d")),
        y=alt.Y(f"{selected_indicator}:Q", title=x_label, scale=_y_scale),
        color=alt.Color("country:N", title="Country"),
        tooltip=[
            alt.Tooltip("country:N", title="Country"),
            alt.Tooltip("year:Q", title="Year", format="d"),
            alt.Tooltip(f"{selected_indicator}:Q", title=x_label, format=",.2f"),
        ],
    ).properties(width=380, height=250, title=f"{x_label} over time")

    over_time_view = mo.vstack([
        mo.hstack([forest_lines, indicator_lines], justify="start"),
    ])
    return (over_time_view,)


@app.cell
def _(alt, filtered_df, mo, selected_indicator, x_label):
    # histogram of the main indicator
    forest_hist = alt.Chart(filtered_df.dropna(subset=["forest_land%"])).mark_bar().encode(
        x=alt.X("forest_land%:Q", bin=alt.Bin(maxbins=15), title="Forest land (% of land area)"),
        y=alt.Y("count():Q", title="Number of country-years"),
        color=alt.Color("country:N", title="Country"),
        tooltip=[alt.Tooltip("count():Q", title="Country-years")],
    ).properties(width=380, height=250, title="Distribution of forest land")

    # histogram of the chosen indicator
    indicator_hist = alt.Chart(filtered_df.dropna(subset=[selected_indicator])).mark_bar().encode(
        x=alt.X(f"{selected_indicator}:Q", bin=alt.Bin(maxbins=15), title=x_label),
        y=alt.Y("count():Q", title="Number of country-years"),
        color=alt.Color("country:N", title="Country"),
        tooltip=[alt.Tooltip("count():Q", title="Country-years")],
    ).properties(width=380, height=250, title=f"Distribution of {x_label}")

    distribution_view = mo.vstack([
        mo.hstack([forest_hist, indicator_hist], justify="start"),
    ])
    return (distribution_view,)


@app.cell
def _(
    a,
    alt,
    b,
    changes_switch,
    distribution_view,
    filtered_df,
    mo,
    over_time_view,
    selected_indicator,
    table_view,
    verdict_view,
    x_label,
):
    _points = alt.Chart(filtered_df).mark_circle(size=60).encode(
        x=alt.X(f"{selected_indicator}:Q", title=x_label, scale=alt.Scale(zero=False)),
        y=alt.Y("forest_land%:Q", title="Forest land (% of land area)", scale=alt.Scale(zero=False)),
        color=alt.Color("country:N", title="Country"),
        tooltip=[
            alt.Tooltip("country:N", title="Country"),
            alt.Tooltip("year:Q", title="Year", format="d"),
            alt.Tooltip(f"{selected_indicator}:Q", title=x_label, format=",.2f"),
            alt.Tooltip("forest_land%:Q", title="Forest land (%)", format=".2f"),
        ],
    )

    # one trend line per country
    _trend = alt.Chart(filtered_df).transform_regression(
        selected_indicator, "forest_land%", groupby=["country"]
    ).mark_line().encode(
        x=alt.X(f"{selected_indicator}:Q"),
        y=alt.Y("forest_land%:Q"),
        color=alt.Color("country:N"),
    )

    scatter_view = (_points + _trend).properties(
        width=450, height=320, title=f"Forest land vs {x_label}"
    )

    claim_check_tab = mo.vstack([
        mo.hstack([scatter_view, table_view], widths=[3, 2], align="start"),
        verdict_view,
    ])

    dashboard_tabs = mo.ui.tabs({
        "Claim check": claim_check_tab,
        "Over time": over_time_view,
        "Distributions": distribution_view
    })

    mo.vstack(
        [a, 
         b, 
         "We used Spearman correlation because it measures whether two indicators tend to rise or fall together without assuming a straight line. Some countries show curved or skewed patterns (for example Ethiopia's forest land), and Spearman is less affected by such shapes and by a few extreme years than Pearson.",
        changes_switch, 
        dashboard_tabs]
    )
    return


if __name__ == "__main__":
    app.run()
