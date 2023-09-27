#!/Users/bin/python
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import seaborn as sns

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites = spacex_df['Launch Site'].unique()
# Create a dash application
app = dash.Dash(__name__)

# ---------------------------------------------------------------------------------
# Create the dropdown menu options

dropdown_options = [{'label': i, 'value': i}
                    for i in launch_sites]

dropdown_options.append({'label': 'All sites', 'value': 'All sites'})

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                html.Div([html.Label("Select launch site:"),
                                          dcc.Dropdown(
                                    id='site-dropdown',
                                    options=dropdown_options,
                                    value='All sites',
                                    # placeholder='select sites'
                                )]),

                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(
                                    [dcc.Graph(id='success-pie-chart')], style={'display': 'flex'}),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=min_payload,
                                                max=max_payload,
                                                marks={i: str(i) for i in range(
                                                    int(min_payload), int(max_payload) + 1, 1000)},
                                                value=[
                                                    min_payload, max_payload]
                                                ),

                                # # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                # html.Div(
                                #     dcc.Graph(id='success-payload-scatter-chart')),
                                html.Br(),
                                html.Div(
                                    [dcc.Graph(id='success-payload-scatter-chart')]),

                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output


@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')

)
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# use groupby to create relevant data for plotting
def update_pie_chart(selected_site):
    if selected_site in launch_sites:

        # succ_count = spacex_df[spacex_df['Launch Site'] ==
        #                        selected_site]['class'].value_counts().reset_index()
        # fig1 = px.bar(succ_count,
        #               x='class',
        #               y='count',
        #               title='succes at the site - '+selected_site
        #               )
        selected_df = spacex_df[spacex_df['Launch Site'] ==
                                selected_site]['class'].value_counts().reset_index()
        class_mapping = {0: 'fail', 1: 'success'}
        selected_df['outcome'] = selected_df['class'].map(class_mapping)
        px.pie(selected_df, values='count', names='outcome')

        fig1 = px.pie(selected_df,
                      values='count',
                      names='outcome',
                      title='Percentage of succes at the site - '+selected_site
                      )
        fig1.update_layout(xaxis_title="Success rate at the site - "+selected_site,
                           xaxis=dict(
                               tickmode='array',
                               tickvals=[0, 1],
                               ticktext=['Fail',  'Sucess']
                           )
                           )
    else:
        # Launch_rate = spacex_df.groupby('Launch Site', as_index=False)[
        #     'class'].count().reset_index()
        for_chart = spacex_df.groupby(['Launch Site', 'class'])[
            'class'].count().loc[(slice(None), 1)].to_frame().reset_index().rename(columns={'class': 'class_success'})
        fig1 = px.pie(for_chart,
                      values='class_success',
                      names='Launch Site',
                      title='succes count of each site'
                      )

    return fig1


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
    Output(component_id='success-payload-scatter-chart',
           component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value'),

     ]

)
def update_payload_chart(selected_site, value):
    if selected_site in launch_sites:
        select_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        filtered_df = select_df.query(
            '`Payload Mass (kg)` >= @value[0] and `Payload Mass (kg)` <= @value[1]')
        fig2 = px.scatter(filtered_df,
                          x='Payload Mass (kg)',
                          y='class',
                          color='Booster Version Category',
                          title='Correlation between Payload and Sucess for site = '+selected_site
                          )
    else:
        filtered_df = spacex_df.query(
            '`Payload Mass (kg)` >= @value[0] and `Payload Mass (kg)` <= @value[1]')
        fig2 = px.scatter(filtered_df,
                          x='Payload Mass (kg)',
                          y='class',
                          color='Booster Version Category',
                          title='Correlation between Payload and Sucess for all sites'
                          )

    return fig2


# Run the app
if __name__ == '__main__':
    app.run_server()
