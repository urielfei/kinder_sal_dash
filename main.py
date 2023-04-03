import dash
import pandas as pd
import plotly.express as px
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output

df = pd.read_csv('df_ranks.csv')
df_cum = pd.read_csv('df_cum_standings.csv')
df_matrices = pd.read_csv('df_matrices.csv')

# df = pd.read_csv('https://raw.githubusercontent.com/urielfei/kinder_sal_dash/main/df_ranks.csv')
# df_cum = pd.read_csv('https://raw.githubusercontent.com/urielfei/kinder_sal_dash/main/df_cum_standings.csv')
# df_matrices = pd.read_csv('https://raw.githubusercontent.com/urielfei/kinder_sal_dash/main/df_matrices.csv')

app = dash.Dash(__name__)


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


app.layout = html.Div([
    html.H1('Kinder Sal', style={'text-align': 'center'}),

    # Dropdown for selecting the week
    html.Div([
        html.Div(
            html.H3('Week'),
            style={'margin-left': '30%'}
        ),
        html.Div(
            dcc.Dropdown(
                id='week-dropdown',
                options=[{'label': w, 'value': w} for w in df['week'].unique()],
                value=min(df['week'].max(),19)
            ),
                style={'margin-left': '25%', 'width':'30%'}
        )
    ]),

    html.Br(),
    html.Div([
        #html.Div(legend, style={'float': 'right'}),
        dash_table.DataTable(
            id='ranks_table',
            columns=[{'name': col, 'id': col} for col in df.columns if col not in 'week'],
            data=df.to_dict('records'),
            style_header={'backgroundColor': 'light grey', 'fontWeight': 'bold'},
            # style_cell={'textAlign': 'left', 'padding': '5px', 'whiteSpace': 'normal'}
            style_cell={
                "textAlign": "center",
                "minWidth": "60px",
                "maxWidth": "160px",
                'padding': '5px',  # reduce cell padding
                'fontSize': '12px',  # reduce font size
                'font': 'Open Sans'
            },
            style_data_conditional=styles
        )
    ], style={'width': '80%', 'display': 'inline-block'}),

    html.Div(children=[
        dcc.Graph(id='my-graph')
    ], style={'width': '80%'}),

    html.Div(children=[
        dash_table.DataTable(
            id='matrix-table',
            columns=[{'name': col, 'id': col} for col in df_matrices.columns if col not in 'week'],
            data=df_matrices.to_dict('records'),
            style_cell={
                "textAlign": "center",
                'padding': '5px',  # reduce cell padding
                'fontSize': '12px'  # reduce font size
            },
            style_header={"backgroundColor": 'light grey',
                          "color": "black",
                          'fontWeight': 'bold',
                          "textAlign": "center",
                          'padding': '5px',  # reduce cell padding
                          'fontSize': '12px'  # reduce font size

                          }
        )
    ] , style={'width': '30%'})

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
    filtered_data = df_cum[df_cum['week'] <= selected_week]
    filtered_data = filtered_data.rename({'cum_points':'Points','team_name':'Team'},axis='columns')
    fig = px.line(filtered_data, x='week', y='Points', color='Team', title='Cumulative Points by Week')
    return fig


if __name__ == '__main__':
    app.run(debug=True)
