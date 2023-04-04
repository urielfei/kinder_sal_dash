import pandas as pd
from dash import dash_table, dcc, html, Dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px


df = pd.read_csv('df_ranks.csv')
df_cum = pd.read_csv('df_cum_standings.csv')
df_matrices = pd.read_csv('df_matrices.csv')

df_cum = df_cum.rename({'cum_points': 'Points', 'team_name': 'Team','week':'Week'},axis=1)

# df = pd.read_csv('https://raw.githubusercontent.com/urielfei/kinder_sal_dash/main/df_ranks.csv')
# df_cum = pd.read_csv('https://raw.githubusercontent.com/urielfei/kinder_sal_dash/main/df_cum_standings.csv')
# df_matrices = pd.read_csv('https://raw.githubusercontent.com/urielfei/kinder_sal_dash/main/df_matrices.csv')

def discrete_background_color_bins(df,  columns, n_bins=7):
    import colorlover
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    df_numeric_columns = df[columns]
    df_max = df_numeric_columns.max().max()
    df_min = df_numeric_columns.min().min()
    ranges = [
        ((df_max - df_min) * i) + df_min
        for i in bounds
    ]
    styles = []
    legend = []

    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        backgroundColor = colorlover.scales[str(n_bins+4)]['div']['RdYlGn'][i+1]
        color = 'black'

        for column in df_numeric_columns:
            styles.append({
                'if': {
                    'filter_query': (
                            '{{{column}}} >= {min_bound}' +
                            (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                    ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                    'column_id': column
                },
                'backgroundColor': backgroundColor,
                'color': color
            })
        legend.append(
            html.Div(style={'display': 'inline-block', 'width': '60px'}, children=[
                html.Div(
                    style={
                        'backgroundColor': backgroundColor,
                        'borderLeft': '1px rgb(50, 50, 50) solid',
                        'height': '10px'
                    }
                ),
                html.Small(round(min_bound, 2), style={'paddingLeft': '2px'})
            ])
        )

    return styles, html.Div(legend, style={'padding': '5px 0 5px 0'})

rank_cols = [col for col in df.columns if '_rank' in col]
styles, legend = discrete_background_color_bins(df, columns=rank_cols)

#Set default graph
pal_gr_color = px.colors.qualitative.Dark24
graph_title_layout = {'y':0.9,'x':0.5,'xanchor': 'center','yanchor': 'top'}

filtered_data = df_cum[df_cum['Week'] <= min(df_cum['Week'].max(),19)]
fig = px.line(filtered_data, x='Week', y='Points', color='Team', title='Cumulative Points by Week', color_discrete_sequence=pal_gr_color)
fig.update_layout(title = graph_title_layout)

graph = dcc.Graph(id='my-graph',
               figure= fig
               )


def draw_element(element):
    return  html.Div([
        dbc.Card(
            dbc.CardBody([
                element
            ])
        ),
    ])

# Text field
def drawText(text='Text'):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H2(text),
                ], style={'textAlign': 'center'})
            ])
        ),
    ])

dropdown = dcc.Dropdown(
                id='week-dropdown',
                options=[{'label': w, 'value': w} for w in df['week'].unique()],
                value=min(df['week'].max(),19)
            )

table_ranks = dash_table.DataTable(
            id='ranks_table',
            columns=[{'name': col, 'id': col} for col in df.columns if col not in 'week'],
            data=df.to_dict('records'),
            style_header={
                'backgroundColor': 'light grey',
                'fontWeight': 'bold'
            },
            style_cell={
                "textAlign": "center",
                'color':'black',
                'fontSize': '12px',  # reduce font size
                'font': 'Open Sans'
            },
            style_data_conditional=styles
)

table_league = dash_table.DataTable(
            id='league-table',
            columns=[{'name': col, 'id': col} for col in df_cum.columns if col in ['Team','Points']],
            data=df_cum.to_dict('records'),
            style_header={'backgroundColor': 'silver', 'fontWeight': 'bold'},
            style_cell={
                'backgroundColor': 'light grey',
                "textAlign": "center",
                'color':'black',
                'fontSize': '12px',  # reduce font size
                'font': 'Open Sans'
            }
)

table_matrix = dash_table.DataTable(
            id='matrix-table',
            columns=[{'name': col, 'id': col} for col in df_matrices.columns if col not in 'week'],
            data=df_matrices.to_dict('records'),
            style_cell={
                "textAlign": "center",
                'color': 'black',
                'fontSize': '12px',  # reduce font size
                'font': 'Open Sans'
            },
            style_header={
                'whiteSpace': 'normal',  # wrap text within cell
                'maxWidth': '180px',  # set maximum width for cell
                'fontSize':'11px',
                'backgroundColor': 'rgb(210, 210, 210)',
                'color': 'black',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                    {
                        'if': {'column_id': 'Team'},
                        'whiteSpace': 'normal',  # wrap text within cell
                        'maxWidth': '180px',  # set maximum width for cell
                        'fontSize':'11px',
                        'fontWeight': 'bold',
                        'backgroundColor': 'rgb(210, 210, 210)'
                    }
    ]
        )

# Build App
app = Dash(external_stylesheets=[dbc.themes.SLATE])


app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                ], width=3),
                dbc.Col([
                    drawText('Ligat Kinder Sal')
                ], width=6),
                dbc.Col([
                ], width=3),
            ], align='center'),
            dbc.Row([
                dbc.Col([
                    html.Div(
                        html.H3('Week'),
                        style={'margin-left': '30%'}
                    ),
                    html.Div(
                        dropdown,
                        style={'margin-left': '25%', 'width': '30%'}
                    )
                ], width=3),
                dbc.Col([
                ], width=9),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    draw_element(table_ranks)
                ], width=9),
                dbc.Col([
                    draw_element(table_league)
                ], width=3),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    draw_element(table_matrix)
                ], width=7),
                dbc.Col([
                    draw_element(graph)
                ], width=5),
            ], align='center'),
        ]), color = 'dark'
    )
])

@app.callback(
    Output('ranks_table', 'data'),
    [Input('week-dropdown', 'value')])
def update_table(selected_week):
    filtered_data = df[df['week'] == selected_week]
    table_data = filtered_data.to_dict('records')
    return table_data

@app.callback(
    Output('matrix-table', 'data'),
    [Input('week-dropdown', 'value')])
def update_table(selected_week):
    filtered_data = df_matrices[df_matrices['week'] == selected_week]
    table_data = filtered_data.to_dict('records')
    return table_data

@app.callback(
    Output('league-table', 'data'),
    [Input('week-dropdown', 'value')])
def update_table(selected_week):
    filtered_data = df_cum[df_cum['Week'] == selected_week]
    filtered_data = filtered_data.sort_values(by='Points',ascending=False)
    table_data = filtered_data.to_dict('records')
    return table_data

@app.callback(
    Output('matrix-table', 'columns'),
    [Input('matrix-table', 'data')]
)
def update_columns(data):
    dat = pd.DataFrame(data)
    columns_order = ['Team'] + dat['Team'].to_list()
    columns = [{'name': col, 'id': col} for col in columns_order]
    return columns

@app.callback(
    Output('my-graph', 'figure'),
    [Input('week-dropdown', 'value')])
def update_graph(selected_week):
    filtered_data = df_cum[df_cum['Week'] <= selected_week]
    fig = px.line(filtered_data, x='Week', y='Points', color='Team', title='Cumulative Points by Week', color_discrete_sequence=pal_gr_color)
    fig.update_layout(title=graph_title_layout)
    return fig


if __name__ == '__main__':
    app.run(debug=True)