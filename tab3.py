import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go


def render_tab(df):

    layout = html.Div(
        [
            html.H1("Kanały sprzedaży", style={"text-align": "center"}),
            html.Div(
                [
                    dcc.Dropdown(
                        id="kanal_sprzedazy",
                        options=[
                            {"label": Store_type, "value": Store_type}
                            for Store_type in df["Store_type"].unique()
                        ],
                        value=df["Store_type"].unique()[0],
                    ),
                ],
                style={"width": "100%", "text-align": "center"},
            ),
            html.Div([dcc.Graph(id="dni_tygodnia")], style={"width": "100%"}),
            html.Div(
                [
                    html.Div([dcc.Graph(id="kraje")], style={"width": "50%"}),
                    html.Div([dcc.Graph(id="plec")], style={"width": "50%"}),
                ],
                style={"display": "flex"},
            ),
        ]
    )

    return layout
