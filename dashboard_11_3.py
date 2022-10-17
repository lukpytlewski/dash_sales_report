import pandas as pd
import datetime as dt
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import class_db
import tab1
import tab2
import tab3

df = class_db.db()
df.merge()

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Tabs(
                    id="tabs",
                    value="tab-1",
                    children=[
                        dcc.Tab(label="Sprzedaż globalna", value="tab-1"),
                        dcc.Tab(label="Produkty", value="tab-2"),
                        dcc.Tab(label="Kanały sprzedaży", value="tab-3"),
                    ],
                ),
                html.Div(id="tabs-content"),
            ],
            style={"width": "80%", "margin": "auto"},
        )
    ],
    style={"height": "100%"},
)


@app.callback(Output("tabs-content", "children"), [Input("tabs", "value")])
def render_content(tab):

    if tab == "tab-1":
        return tab1.render_tab(df.merged)
    elif tab == "tab-2":
        return tab2.render_tab(df.merged)
    elif tab == "tab-3":
        return tab3.render_tab(df.merged)


## tab1 callbacks
@app.callback(
    Output("bar-sales", "figure"),
    [Input("sales-range", "start_date"), Input("sales-range", "end_date")],
)
def tab1_bar_sales(start_date, end_date):

    truncated = df.merged[
        (df.merged["tran_date"] >= start_date) & (df.merged["tran_date"] <= end_date)
    ]
    grouped = (
        truncated[truncated["total_amt"] > 0]
        .groupby([pd.Grouper(key="tran_date", freq="M"), "Store_type"])["total_amt"]
        .sum()
        .round(2)
        .unstack()
    )

    traces = []
    for col in grouped.columns:
        traces.append(
            go.Bar(
                x=grouped.index,
                y=grouped[col],
                name=col,
                hoverinfo="text",
                hovertext=[f"{y/1e3:.2f}k" for y in grouped[col].values],
            )
        )

    data = traces
    fig = go.Figure(
        data=data,
        layout=go.Layout(title="Przychody", barmode="stack", legend=dict(x=0, y=-0.5)),
    )

    return fig


@app.callback(
    Output("choropleth-sales", "figure"),
    [Input("sales-range", "start_date"), Input("sales-range", "end_date")],
)
def tab1_choropleth_sales(start_date, end_date):

    truncated = df.merged[
        (df.merged["tran_date"] >= start_date) & (df.merged["tran_date"] <= end_date)
    ]
    grouped = (
        truncated[truncated["total_amt"] > 0]
        .groupby("country")["total_amt"]
        .sum()
        .round(2)
    )

    trace0 = go.Choropleth(
        colorscale="Viridis",
        reversescale=True,
        locations=grouped.index,
        locationmode="country names",
        z=grouped.values,
        colorbar=dict(title="Sales"),
    )
    data = [trace0]
    fig = go.Figure(
        data=data,
        layout=go.Layout(
            title="Mapa",
            geo=dict(showframe=False, projection={"type": "natural earth"}),
        ),
    )

    return fig


## tab2 callbacks
@app.callback(Output("barh-prod-subcat", "figure"), [Input("prod_dropdown", "value")])
def tab2_barh_prod_subcat(chosen_cat):

    grouped = (
        df.merged[(df.merged["total_amt"] > 0) & (df.merged["prod_cat"] == chosen_cat)]
        .pivot_table(
            index="prod_subcat", columns="Gender", values="total_amt", aggfunc="sum"
        )
        .assign(_sum=lambda x: x["F"] + x["M"])
        .sort_values(by="_sum")
        .round(2)
    )

    traces = []
    for col in ["F", "M"]:
        traces.append(
            go.Bar(x=grouped[col], y=grouped.index, orientation="h", name=col)
        )

    data = traces
    fig = go.Figure(
        data=data,
        layout=go.Layout(
            barmode="stack",
            margin={
                "t": 20,
            },
        ),
    )
    return fig


## tab3 callbacks
@app.callback(Output("dni_tygodnia", "figure"), [Input("kanal_sprzedazy", "value")])
def tab3_dni_tygodnia(wybrany_kanal_sprzedazy):

    grouped = (
        df.merged[df.merged["Store_type"] == wybrany_kanal_sprzedazy]
        .groupby("day_of_week")["total_amt"]
        .sum()
        .round(2)
    )

    fig = go.Figure(
        data=[
            go.Bar(
                x=grouped.index.map(
                    {
                        0: "Monday",
                        1: "Tuesday",
                        2: "Wednesday",
                        3: "Thursday",
                        4: "Friday",
                        5: "Saturday",
                        6: "Sunday",
                    }
                ),
                y=grouped.values,
            )
        ],
        layout=go.Layout(title="Sales by day of week"),
    )

    return fig


@app.callback(Output("kraje", "figure"), [Input("kanal_sprzedazy", "value")])
def tab3_kraje(wybrany_kanal_sprzedazy):

    grouped = (
        df.merged[df.merged["Store_type"] == wybrany_kanal_sprzedazy]
        .groupby("country")["total_amt"]
        .sum()
        .round(2)
    )

    fig = go.Figure(
        data=[
            go.Pie(
                labels=grouped.index,
                values=grouped.values,
            )
        ],
        layout=go.Layout(title="Sales by country"),
    )
    return fig


@app.callback(Output("plec", "figure"), [Input("kanal_sprzedazy", "value")])
def tab3_plec(wybrany_kanal_sprzedazy):

    grouped = (
        df.merged[df.merged["Store_type"] == wybrany_kanal_sprzedazy]
        .groupby("Gender")["total_amt"]
        .sum()
        .round(2)
    )

    colors = ["yellow", "red"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=grouped.index,
                values=grouped.values,
                hole=0.3,
            )
        ],
        layout=go.Layout(title="Sales by gender"),
    )

    fig.update_traces(marker=dict(colors=colors))

    return fig


if __name__ == "__main__":

    app.run_server(debug=False)
