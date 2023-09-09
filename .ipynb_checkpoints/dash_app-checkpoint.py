import dash
import dash_bootstrap_components as dbc
from dash import dcc,html, dash_table
import ast
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date 
import base64
import numpy as np
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
from io import BytesIO # for wordcloud 
from datetime import datetime, timedelta



import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)


##############################################          FUNCTIONS             ##################################################
def flatten_list(list_of_lists):
    return [item for sublist in list_of_lists for item in ast.literal_eval(sublist)]


def generate_table(dataframe, max_rows=100):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

def top_keywords_df(list):
    list_updated = [word for word in list if word not in stop_words] 
    d = Counter(list_updated)
    keyword_df_temp = pd.DataFrame(d,index=[0]).T.reset_index()
    keyword_df_temp.columns = ['Keyword', "Frequency"]
    keyword_df_temp = keyword_df_temp.sort_values(["Frequency"], ascending = False)
    #keyword_df_temp["% Review with keyword"] = round(100*keyword_df_temp["Frequency"]/keyword_df_temp["Frequency"].sum(),2)
    
    return keyword_df_temp

def plot_wordcloud(list):
    list_updated = [word for word in list if word not in stop_words]
    # ps = PorterStemmer()
    # list_updated = [ps.stem(word) for word in list_updated]
    
    d = Counter(list_updated)
    wc = WordCloud(stopwords = stop_words,background_color='white', width=550, height=400,max_words=30)
    
    wc.fit_words(d)
    return wc.to_image()


# Function to filter dataframe from list of chosen filters 


def update_dictionary(input_dict):
    for i in list(input_dict.keys()):
        if input_dict[i] == '' or input_dict[i] == 'None' or input_dict[i] == None or input_dict[i]==[]: ## Also check for [] to address empty lists 
            input_dict[i] = filt_values[i]
    return input_dict
#############################################               DATA           ###################

## ingesting dataframe 

list_adhoc = ['stars','Stars','STARS', 'star','don','nan','wakefit']
stop_words = list(STOPWORDS) + list_adhoc
data = pd.read_csv('./data/df_raw.csv')
data = data.rename(columns={data.columns[0]: 'review_id'})



# building rating_df prior to gvoid str/int/flot conversion issue 
## Building a top_product sentiment table 
rating_df = data.groupby(['product_id','star_rating'], as_index = False)['review_id'].count()
rating_df['star_rating'] =rating_df['star_rating'].astype(float)
rating_df['review_id'] =rating_df['review_id'].astype(float)
rating_df['rating_mult'] = rating_df['star_rating']*rating_df['review_id']

rating_df_gpd = rating_df.groupby(['product_id'], as_index= False).apply(lambda x: x['rating_mult'].sum()/x['review_id'].sum())
rating_df_gpd.columns = ['Product ID','Weighted Rating']
rating_df_gpd['Weighted Rating'] = rating_df_gpd['Weighted Rating'].apply(lambda x : round(x,2))
rating_df_gpd = rating_df_gpd.sort_values(['Weighted Rating'], ascending = False)

# calculating date wise weighted rating of the products 

## Building a top_product sentiment table 
product_rating_df = data.groupby(['Week','product_parent','star_rating'], as_index = False)['review_id'].count()
product_rating_df['star_rating'] =product_rating_df['star_rating'].astype(float)
product_rating_df['review_id'] =product_rating_df['review_id'].astype(float)
product_rating_df['rating_mult'] = product_rating_df['star_rating']*product_rating_df['review_id']


product_rating_df_gpd = product_rating_df.groupby(['product_parent','Week'], as_index= False).apply(lambda x: x['rating_mult'].sum()/x['review_id'].sum())
product_rating_df_gpd.columns = ['Product Parent','Week','Weighted Rating']
product_rating_df_gpd['Weighted Rating'] = product_rating_df_gpd['Weighted Rating'].apply(lambda x : round(x,2))
product_rating_df_gpd = product_rating_df_gpd.sort_values(['Weighted Rating'], ascending = False)


print(product_rating_df)
# making change in data df 
data['review_date'] = pd.to_datetime(data['review_date'])
data['sentiment_tag'] = data['sentiment_tag'].fillna('NA')
data['star_rating'] = data['star_rating'].apply({lambda x : x.astype('str')})
data['star_rating'] = data['star_rating'].replace(to_replace=["1.0","2.0","3.0","4.0"],
           value=["1","2","3","4"])
## remove where sentiment cant be ascertained 
data = data[~data['star_rating'].isna()]
data = data[data['sentiment_tag']!="NA"]


#making a keyword dataframe
keyword_df = top_keywords_df(flatten_list(data['tags'].to_list()))






## data reuired for functions
filt_values = {'star_rating': ['1','2','3','4'], 'sentiment_tag': ['POSITIVE','NEGATIVE'],
             'verified_purchase': ['Y','N'],
               'product_id': list(data['product_id'].unique())}

review_cols = ['product_id','review_date','review_body']

# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '22%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa',
    "overflow": "scroll"
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '27%',
    'margin-right': '5%',
    'padding': '20px 10p'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#191970'
}

CARD_TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#0074D9'
}

CARD_TEXT_STYLE_SMALL = {
    'textAlign': 'center',
    'color': '#D3D3D3'
}

controls = dbc.FormGroup(
    [
        html.P('Date Range', style={
            'textAlign': 'center',"width": "100%"
            }),
                html.Div(dcc.DatePickerRange(
                id='my-date-picker-range',
                display_format = 'DD-MM-YYYY',
                min_date_allowed=date(2023, 1, 5),
                max_date_allowed=date(2023, 10, 31),
                initial_visible_month=date(2023, 7, 16),
                end_date=date(2023, 8, 31), 
                start_date=date(2023, 8, 1),

                style = {
                            'font-size': '5px','display': 'inline-block',# 'border-radius' : '2px', 
                            #'border' : '1px solid #ccc', 'color': '#333', 
                            'border-spacing' : '5', 'border-collapse' :'separate',
                            'zIndex': 10 ,  "width": "100%" ,
                            # 'padding-left': '1px',
                            # 'padding-right': '1px' 
                            } 
                         ),
                         style={
                'textAlign': 'center',"width": "100%"
                                }
                        ),
            html.Div(id='output-container-date-picker-range'),
            html.P('Reviews time duration : 1 Jan 2021 - 31 Aug 2023', style={
                'textAlign': 'center',"width": "100%", 'font-size': '12px'
            })
        ,
        html.Br(),
        
        html.P('Star Rating', style={
                'textAlign': 'center'
            }),
            dcc.Dropdown(
                id='star_rating',
                options=[{
                    'label': 'One',
                    'value': '1'
                }, {
                    'label': 'Two',
                    'value': '2'
                },
                    {
                        'label': 'Three',
                        'value': '3'
                    },
                {
                        'label': 'Four',
                        'value': '4'
                    },
                {
                        'label': 'Five',
                        'value': '5'
                    }
                ],
                value=['1','2','3','4'],  # default value
                multi=True
            ),
        html.Br(),
    

        html.P('Sentiment', style={
            'textAlign': 'center'
            }),
            dbc.Card([dbc.Checklist(
                id='sentiment_list',
                options=[
                    {
                    'label': 'Positive',
                    'value': 'POSITIVE'
                    },
                    {
                        'label': 'Negative',
                        'value': 'NEGATIVE'
                    }
                ],
                value=["POSITIVE","NEGATIVE"],
                inline=True
            )]),
        html.Br(),



        html.P('Verified Purchase', style={
            'textAlign': 'center'
            }),
            dbc.Card([dbc.Checklist(
                id='verified_purchase',
                options=[
                    {
                    'label': 'Yes',
                    'value': 'Y'
                    },
                    {
                        'label': 'No',
                        'value': 'N'
                    }
                ],
                value=["Y","N"],
                inline=True
            )]),

        html.Br(),


        

    html.P('Product Id', style=
           {'textAlign': 'center',
            }),
        html.Div([dcc.Dropdown(
            id='product_id',
            options=[{"label":str(i),"value":str(i)} for i in data['product_id'].unique()
            ],
            value=list(data['product_id'].unique())[0:10],  # default value
            multi=True,
            style={
                'maxHeight' :'400px',
                'minHeight' :'50px',
                #'height' :'200px',
                #'overflow-y':'auto'

            }
        )]),
        html.Br(),

        dbc.Button(
            id='clear_button',
            n_clicks=0,
            children='Remove All Filters',
            color='secondary',
            block=True
        ),

        dbc.Button(
            id='submit_button',
            n_clicks=0,
            children='Apply Filters',
            color='primary',
            block=True
        ),
        # dbc.Button(
        #     id='last_30_days',
        #     n_clicks=0,
        #     children='Last 30 days',
        #     color='primary',
        #     block=True
        #)
    ]
)

sidebar = html.Div(
    [
        html.H3('Filters', style=TEXT_STYLE),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE,
)


content_summary_row = dbc.Row([
    dbc.Col([
       
        
       html.P(["""OVERALL SUMMARY:\n\n""",html.Br(),"""The reviews highlight multiple issues with Wakefit products including poor quality, flawed design, and subpar customer service. Customers reported problems with mattresses being too soft, causing back pain, and not living up to the 'orthopedic' label. The delivery and assembly process was criticized for being inconvenient and damaging to the products. Some customers also reported receiving defective or damaged items, including beds with uneven legs, wardrobes with cracks, and sofas that arrived dirty and wet. Customer service was described as unresponsive and unhelpful in resolving these issues. The company's return policy was also criticized for being inconsistent across different platforms. Despite some positive comments about affordability and aesthetics, the overall sentiment was of disappointment and frustration."""],
                     
                     style={"border":"2px black solid",
                           "width" : "100%",
                            "height" :'100%',
                            "padding-top": "40px",
                            'font-size': '14px'
                           # "minLength" : "100px",
                           # "minHeight" :'400px',
                            
                           })
        
      ]
    
    ),
    dbc.Col(
        [
            

         html.P(["""What USERS liked:""",html.Br(),
         """1.Wide Range of Products: Customers loved the wide variety of products available on Amazon. They appreciated the ability to find almost anything they needed on the platform, from everyday essentials to niche items.""",html.Br(),
                """2. User-Friendly: Many reviews highlighted the user-friendly nature of Amazon products. Customers appreciated the intuitive design and easy-to-understand instructions, making the products accessible to a wide range of users."""],
                  style={"border":"2px black solid",'width': '100%', 
                            #"minLength" : "100px",
                           # "minHeight" :'190px',
                          "height" :'52%',
              'backgroundColor': "#C8E4B2",
                'readOnly' : True,
                         'font-size': '12px'
                        
                        }
                 ),
         
         

            
             html.P(["""What users COMPLAINED about:""",html.Br(),
             
             """1. The mattress is too soft and squishy, causing it to collapse or sag in the middle after a short period of use.""",html.Br(),
             """2. The bed frames have legs that are inconveniently placed, causing customers to often hit their feet on them. Additionally, some customers reported that the frames were too high or too low.""",html.Br(),
             """3. Some customers reported that the chairs were unstable, uncomfortable, and of poor quality."""],
                  style={"border":"2px black solid",'width': '100%', 
                        # "minLength" : "100px",
                        #  "minHeight" :'200px',
                          "height" :'46%',
                          'backgroundColor': "#FA9884",
                        'readOnly' : True,
                         'font-size': '12px'
                        }
                 ),    
        ]
        )
    ]
    ) 

content_summary_table = dbc.Row(
    [
        html.Br(),
        html.P('Top Products and their Weighted rating:', style={
            'textAlign': 'left','padding':'30px', 'font-size': '20px'
        }),
        
        dbc.Col(
            dash_table.DataTable(
            id='table_top_products',
            columns=[{"name": i, "id": i} for i in rating_df_gpd.columns],
            style_cell={'textAlign': 'center'},                style_cell_conditional=[
                        {
            'if': {'column_id': 'Product ID'},
                    'textAlign': 'left'
                        }
                        ],
            data = rating_df_gpd.head(5).to_dict('records')
        ), md=5
        )
    ]
                        )

content_first_row = dbc.Row([
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4(id='card_title_1', children=['Total reviews analyzed'], className='card-title',
                                style=CARD_TEXT_STYLE),
                        html.P(id='card_text_1', children='children', style=CARD_TEXT_STYLE),
                    ],style={"height": "10rem"}
                )
            ]
        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [

                dbc.CardBody(
                    [
                        html.H4('Total Positive Reviews', className='card-title', style=CARD_TEXT_STYLE),
                        html.P(id='card_text_2', children='children', style=CARD_TEXT_STYLE),
                    ]
                    ,style={"height": "10rem"}
                ),
            ]

        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4('Total Negative Reviews', className='card-title', style=CARD_TEXT_STYLE),
                        html.P(id='card_text_3', children='children', style=CARD_TEXT_STYLE),
                    ],style={"height": "10rem"}
                ),
            ]

        ),
        md=3
    ),
    dbc.Col(
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4('Sentiment score', className='card-title', style=CARD_TEXT_STYLE),
                        html.P('Percentage of positive reviews across the feedback.',
                              style={
            'textAlign': 'center',"width": "100%", 'font-size': '10px'
                                    }
                              
                              ),
                        html.P(id='card_text_4', children=' ', style=CARD_TEXT_STYLE),
                    ],style={"height": "10rem"}
                ),
            ]
        ),
        md=3
    )
])

content_product_rating_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_product_rating'), md=12
        ),
    ]
)


content_second_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_1'), md=12
        ),
    ]
)

content_sentiment_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_sentiment'), md=12
        ),
    ]
)

content_sentiment_product_row = dbc.Row(
    [
         dbc.Col(
            [
            html.Label("Top products based on sentiment analysis"),
            dash_table.DataTable(
            id='table_top_products_sentiment',
            columns=[{"name": i, "id": i} for i in  ['Product ID', 'Total Reviews analysed','Sentiment Score']],
            style_cell={'textAlign': 'center'},
            #     style_cell_conditional=[
            #             {
            # 'if': {'column_id': 'Keyword'},
            #         'textAlign': 'left'
            #             }
            #             ]
            #data=keyword_df.head(10).to_dict('records'),
                )
             ]
                ),
        
         dbc.Col(
             [
            html.Label("Bottom products based on sentiment analysis"),
            dash_table.DataTable(
            id='table_bottom_products_sentiment',
            columns=[{"name": i, "id": i} for i in  ['Product ID', 'Total Reviews analysed','Sentiment Score']],
            style_cell={'textAlign': 'center'},
            #     style_cell_conditional=[
            #             {
            # 'if': {'column_id': 'Keyword'},
            #         'textAlign': 'left'
            #             }
            #             ]
            #data=keyword_df.head(10).to_dict('records'),
                )
             ]
                )
    ]
)



content_third_row = dbc.Row(
    [
        dbc.Col(
            
            #dcc.Graph(id='graph_4', figure="fig"), #md=12,
            html.Img(id ="wordcloud_img") , md = 8
        ),
        
        dbc.Alert(
            children='',
            id="alert-no-wordcloud",
            fade=False,
             color="white"
        ),
        

         dbc.Col(
            [dash_table.DataTable(
            id='table_kw',
            columns=[{"name": i, "id": i} for i in ['Keyword','Relevance%']],
            style_cell={'textAlign': 'center'},
                style_cell_conditional=[
                        {
            'if': {'column_id': 'Keyword'},
                    'textAlign': 'left'
                        }
                        ]
            #data=keyword_df.head(10).to_dict('records'),
                ),
             dbc.Alert(
            children='',
            id="alert-no-table-kw",
            fade=False,
            color="white"
        ),
             
             ]
                ),
        
        
        

        
        
        

    ]
)


content_fourth_row = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(id='graph_5'),md=5
        ),
        dbc.Col(
            dcc.Graph(id='graph_6'),md=5
        ),
    ]
    )

content_fifth_row = dbc.Row(
    [
        html.H4('Filtered User reviews (20 most recent)', style={
            'textAlign': 'Center'
        }),
        
        
        dbc.Col(
            dash_table.DataTable(
            id='table_reviews',
            columns=[{"name": i, "id": i} for i in ['Product ID','Review Date','Review Text']],
            
                
            style_cell={'textAlign': 'left', 'minWidth': '80px', #'width': '50px',
                        'maxWidth': '1000px', 
                        'whiteSpace':'normal', 'height':'auto', 'lineHeight':'20px'},
                style_cell_conditional=[
                        {
                    'if': {'column_id': 'Review Date'},
                            'textAlign': 'center' ,'minWidth': '100px'
                        }
                        ]
          
        ), md=12
        )
    ]
    )



content = html.Div(
    [
        html.H2('Vire Insights | VoC v1.0', style=TEXT_STYLE),
        content_summary_row,
        html.Br(),
        content_summary_table,
        html.Hr(),
        html.H4('Overall summary for selected time window', style=TEXT_STYLE),
        html.Hr(),
        content_first_row,
        content_product_rating_row, 
        html.Hr(),
        content_second_row,
        content_sentiment_row,
        html.H6('Top and bottom products based on sentiment score (for selected date ranges)', style={
                                                                        'textAlign': 'left',
                                                                        'color': '#191970'
                                                                    }),
        content_sentiment_product_row,
        html.Br(),
        html.H3('Review profiling', style=TEXT_STYLE),
        html.Div(    
            [html.Label('Count of reviews filtered for analysis:'),html.P(html.Div(id='count_header'))]),
        html.Hr(),
        content_third_row,
        html.Hr(),
        content_fourth_row,
        html.Hr(),
        content_fifth_row
        
    ],
    style=CONTENT_STYLE
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([sidebar, content])





## Callback code -- Left to right , top down




## TOTAL REVIEWS
@app.callback(
    [Output('card_text_1', 'children'),
    Output('count_header','children')],
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 
     State('product_id', 'value')
     ]
   )
def update_card_text_1(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase, product_id):
    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    
    print("***************UPDATE CARD TEXT 1*********************")
    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)

    
    for key, val in filt_dict_updated.items():
        print(key)
        print("Dataframe length : {}".format(len(temp_df)))
        print("Sentiment : {}".format(temp_df['sentiment_tag'].unique()))
        
        temp_df = temp_df[temp_df[key].isin(val)]
    print("Update card text 1 - getting data")
    print("Len temp df : {}".format(len(temp_df)))
    print("Start date :{}".format(start_date))
    
    return len(temp_df),len(temp_df)


## POSITIVE REVIEWS
@app.callback(
    Output('card_text_2', 'children'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 

     State('product_id', 'value')
     ]
    )
def update_card_text_2(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase, product_id):
    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("*****************UPDATE CARD TEXT 2*******************")
    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        temp_df = temp_df[temp_df[key].isin(val)]

    temp_df = temp_df[(temp_df['sentiment_tag']=="POSITIVE")]
    return len(temp_df)


## NEGATIVE REVIEWS
@app.callback(
    Output('card_text_3', 'children'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 

     State('product_id', 'value')]
    )
    #def update_card_text_1(n_clicks, dropdown_value, check_list_value, start_date, end_date):
def update_card_text_3(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase, product_id):
    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("*****************UPDATE CARD TEXT 3*******************")
    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)
    # FILTERING DATAFRAME
    for key, val in filt_dict_updated.items():
        temp_df = temp_df[temp_df[key].isin(val)]
        
    temp_df = temp_df[temp_df['sentiment_tag']=="NEGATIVE"]
    return len(temp_df)



## SENTIMENT SCORE
@app.callback(
    Output('card_text_4', 'children'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 

     State('product_id', 'value')]
    )
    #def update_card_text_1(n_clicks, dropdown_value, check_list_value, start_date, end_date):
def update_card_text_4(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase, product_id):
    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("**************** UPDATE CARD TEXT 4********************")
    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase, 
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        temp_df = temp_df[temp_df[key].isin(val)]
        
    if len(temp_df) >0:

        len_neg = len(temp_df[temp_df['sentiment_tag']=="NEGATIVE"])
        len_pos = len(temp_df[temp_df['sentiment_tag']=="POSITIVE"])
    # Sample data and figure
        return round((100*(len_pos)/(len_pos+len_neg)),1)
    else :
        return 0

## LINE CHART 
@app.callback(
    Output('graph_1', 'figure'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 

     State('product_id', 'value')]
    )

def update_graph_1(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase, product_id):

    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("*************** UPDATE LINE CHART *********************")
    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase, 
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        temp_df = temp_df[temp_df[key].isin(val)]

    grouped_df = temp_df.groupby(['review_date','sentiment_tag'], as_index = False)['review_id'].count()
    grouped_df = grouped_df.fillna(0)

    pivot_df = pd.pivot_table(grouped_df, values=['review_id'], index=['review_date'], columns=['sentiment_tag'],
                aggfunc='sum', fill_value=0, margins=False, dropna=False, margins_name='All', observed=False, sort=True)

    pivot_df.columns = [' '.join(col).strip() for col in pivot_df.columns.values]
    pivot_df = pivot_df.reset_index()
    
    if len(pivot_df) >0:
        pivot_df.columns = ['date','neg_cc','pos_cc']
        ## Calculate number of ticks 
        
        tick_count = int(max(1,round((len(pivot_df)/10),0)))
        #pivot_df['date'] = pivot_df['date'].dt.strftime('%d-%m-%Y')
    else :
        pivot_df = pd.DataFrame(columns = ['date','neg_cc','pos_cc'])

    x = pivot_df['date']
    y1 = pivot_df['neg_cc']
    y2 = pivot_df['pos_cc']
    
    #fig = px.line(x=x, y = [y1,y2])
    # fig = px.line(x=pivot_df['date'], y = pivot_df['neg_cc'],#pivot_df['pos_cc']],
    #               color_discrete_sequence=["#F6635C", "#85A389"],
    #              )
    if len(pivot_df) >0 :
        fig1 = px.line(x=pivot_df['date'], y = pivot_df['neg_cc'],#pivot_df['pos_cc']],
                      color_discrete_sequence=["#F6635C"],labels={
                                                                "neg_cc": "Negative", 
                                                                }
                     )
        fig1.update_traces(
            hovertemplate="<br>".join([
                "Date: %{x}",
                "Negative Reviews: %{y}"
            ]),

            )


        fig2 = px.line(x=pivot_df['date'], y = pivot_df['pos_cc'],#pivot_df['pos_cc']],
                      color_discrete_sequence=[ "#85A389"]
                     )
        fig2.update_traces(
            hovertemplate="<br>".join([
                "Date: %{x}",
                "Positive Reviews: %{y}"])
            )


        layout = go.Layout(title = "Customer sentiment trends",showlegend = True)

        fig = go.Figure(data=fig1.data + fig2.data, layout = layout)

        fig.update_traces(showlegend=True)
        fig.update_layout(legend_title_text='Sentiment')

        fig['data'][0]['name'] = 'Negative'
        fig['data'][1]['name'] = 'Positive'

        # Update AXES name and title 
        fig.update_xaxes(title='Date')
        fig.update_xaxes(linecolor='#61677A')

        fig.update_yaxes(title='#Reviews')
        fig.update_yaxes(linecolor='#61677A')

        fig.update_xaxes(tickangle=-45,
                     tickmode = 'array',
                     tickvals = pivot_df['date'][0::tick_count],
                     #ticktext= [d.strftime('%Y-%m-%d') for d in datelist]
                        )

        fig.update_layout(
            {
            'plot_bgcolor' :'rgba(0,0,0,0)',
            }
                )
    else :
        return {
        "layout": {
            "xaxis": {
                "visible": True
            },
            "yaxis": {
                "visible": True
            },
            "annotations": [
                {
                    "text": "Add more data",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        }
    }
        
    return fig






####### PRODUCT RATING TREND 

@app.callback(
    Output('graph_product_rating', 'figure'),
    [Input('submit_button', 'n_clicks')],
    # [
    #  State('product_id', 'value')]
    )

def update_graph_product_rating(n_clicks):
    print("-------------------------------------------- Getting product rating ")
    temp_df = product_rating_df_gpd
    temp_df = temp_df[temp_df['Week']!='c']
    temp_df['Week'] = temp_df['Week'].astype('int')

    temp_df = temp_df.reset_index(drop=True).sort_values(['Week','Product Parent'], ascending = True)
    
    fig = px.line(x=temp_df['Week'], y = temp_df['Weighted Rating'], color =temp_df['Product Parent'])
    # Change title 
    fig.update_layout({'title':'Weighted Product rating overtime',
                     'plot_bgcolor' :'rgba(0,0,0,0)',
                    }),
    # Change the x-axis name
    fig.update_xaxes(title='Week')
    fig.update_xaxes(linecolor='#61677A')
    # Change the y-axis name
    fig.update_yaxes(title='Calculated Weighted Rating')
    fig.update_yaxes(linecolor='#61677A')
    # # Update Legend name and title 
    fig.update_traces(
            hovertemplate="<br>".join([
                "Week: %{x}",
                "Weighted Rating: %{y}"
            ]),

            )
    fig.update_xaxes(tickangle=-45,
         tickmode = 'array',
         tickvals = temp_df['Week'][0::2],
            )
        
#     product_uq = list(temp_df['Product Parent'].unique())[0:3]
#     print(product_uq)
#     fig = go.Figure()
#     for prod in product_uq:
#         prod_temp_df = temp_df[temp_df['Product Parent']==prod]
#         prod_temp_df = prod_temp_df.sort_values(['Week'], ascending = True)
#         fig.add_trace(go.Line(x=prod_temp_df.Week, y=prod_temp_df['Weighted Rating']))
        
        
    return fig


### PRODUCT RATING 

@app.callback(
    Output('graph_sentiment', 'figure'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 

     State('product_id', 'value')]
    )

def update_graph_sentiment(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase, product_id):

    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("*************** UPDATE SENTIMENT LINE CHART *********************")
    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        temp_df = temp_df[temp_df[key].isin(val)]

    grouped_df = temp_df.groupby(['review_date','sentiment_tag'], as_index = False)['review_id'].sum()
    grouped_df = grouped_df.fillna(0)

    pivot_df = pd.pivot_table(grouped_df, values=['review_id'], index=['review_date'], columns=['sentiment_tag'],
                aggfunc='sum', fill_value=0, margins=False, dropna=False, margins_name='All', observed=False, sort=True)

    
    if len(pivot_df) >0 :
        pivot_df.columns = [' '.join(col).strip() for col in pivot_df.columns.values]
        pivot_df = pivot_df.reset_index()
        pivot_df.columns = ['date','neg_cc','pos_cc']
        pivot_df['sentiment_score'] = round((100*pivot_df['pos_cc']/(pivot_df['pos_cc']+pivot_df['neg_cc'])),2)

        tick_count = int(max(1,round((len(pivot_df)/10),0)))
        
        fig = px.line(x=pivot_df['date'], y = pivot_df['sentiment_score'])
        # Change title 
        fig.update_layout({'title':'Trendline of sentiment score',
                         'plot_bgcolor' :'rgba(0,0,0,0)',
                        }),
        # Change the x-axis name
        fig.update_xaxes(title='Date')
        fig.update_xaxes(linecolor='#61677A')
        # Change the y-axis name
        fig.update_yaxes(title='Calculated sentiment score')
        fig.update_yaxes(linecolor='#61677A')
        # # Update Legend name and title 
        fig.add_hline(y=pivot_df['sentiment_score'].mean(), line_width=3, line_dash="dash", line_color="grey")
        fig.update_yaxes(range = [0,110])
        fig.update_traces(line_color='#0000ff')
        fig.update_traces(
                hovertemplate="<br>".join([
                    "Date: %{x}",
                    "Sentiment Score: %{y}"
                ]),

                )
        fig.update_xaxes(tickangle=-45,
             tickmode = 'array',
             tickvals = pivot_df['date'][0::tick_count],
             #ticktext= [d.strftime('%Y-%m-%d') for d in datelist]
                )
        
        fig.add_annotation(dict(font=dict(color='black',size=15),
                                            x=pivot_df['date'].max(),
                                            y=pivot_df['sentiment_score'].mean()*1.06,
                                            showarrow=False,
                                            text="Mean :{}".format(round(pivot_df['sentiment_score'].mean(),1)),
                                            textangle=0,
                                            xanchor='right'))
    else :
        return {
        "layout": {
            "xaxis": {
                "visible": True
            },
            "yaxis": {
                "visible": True
            },
            "annotations": [
                {
                    "text": "Add more data",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        }
    }

 
        
    return fig







## TOP SENTIMENT PRODUCTS

@app.callback(
    [Output('table_top_products_sentiment', 'data'),
    Output('table_bottom_products_sentiment', 'data')
    ],
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')]
    )

def update_products(n_clicks, start_date, end_date):

    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("*************** UPDATE SENTIMENT PRODUCTS *********************")


    ## Building a top_product sentiment table 
    grouped_df = temp_df.groupby(['product_id','sentiment_tag'], as_index = False)['review_id'].count()
    grouped_df = grouped_df.fillna(0)
    
    pivot_df = pd.pivot_table(grouped_df, values=['review_id'], index=['product_id'], columns=['sentiment_tag'],
                aggfunc='sum', fill_value=0, margins=False, dropna=False, margins_name='All', observed=False, sort=True)


    pivot_df.columns = [' '.join(col).strip() for col in pivot_df.columns.values]

    
    pivot_df = pivot_df.reset_index()
    pivot_df.columns = ['product_id','neg_cc','pos_cc']
    pivot_df['total_count'] = pivot_df['pos_cc']+pivot_df['neg_cc']
    pivot_df['sentiment_score'] = round((100*pivot_df['pos_cc']/pivot_df['total_count']),2)

    pivot_df = pivot_df.drop(['pos_cc','neg_cc'], axis =1)
    pivot_df.columns = ['Product ID', 'Total Reviews analysed','Sentiment Score']

    top_products = pivot_df.sort_values(['Sentiment Score'], ascending = False)
    top_products = top_products[top_products['Total Reviews analysed']>2].head(3)
    bottom_products = pivot_df.sort_values(['Sentiment Score'], ascending = True)
    bottom_products = bottom_products[bottom_products['Total Reviews analysed']>2].head(3)
    
    return [top_products.to_dict('records'), bottom_products.to_dict('records')]



## WORDCLOUD 
@app.callback(
    Output('wordcloud_img', 'src'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 

     State('product_id', 'value')
     ]
    )

def update_graph_4(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase, product_id):


    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("**************** WORDCLOUD ********************")

    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    #print("Filtered dictionary :{}".format(filt_dict_updated))

    for key, val in filt_dict_updated.items():
        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]
        #print("Len of dataframe = {}".format(len(temp_df)))
        
    if len(temp_df) >5:

    # Sample data and figure
        img = BytesIO()
        word_list = flatten_list(temp_df['tags'].to_list())
        #print(word_list)
        fig = plot_wordcloud(word_list)
        fig.save(img, format="PNG")
    
        return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

    
@app.callback([Output('alert-no-wordcloud', 'children'),
              Output('alert-no-table-kw', 'children')
              ],
        [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 

     State('product_id', 'value')
     ]
     )
def handle_error(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase, product_id):
    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("*************** TABLE OF KEYWORDS *********************")

    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]
        
    if len(temp_df)<6:
        ret_str = "Please add more parameters to display the wordcloud"
        ret_str_kw = "Please add more parameters to display the frequency table."
        
        return "",""

#####################################################################################

## KEYWORD TABLE
@app.callback(
    Output('table_kw', 'data'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 

     State('product_id', 'value')
     ]
    )
def update_keyword_table(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase, product_id):


    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("*************** TABLE OF KEYWORDS *********************")

    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,

                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]
        #print("Len of dataframe = {}".format(len(temp_df)))
        #print("Top KW dataframe...")
        #print(top_keywords_df(flatten_list(temp_df['tags'].to_list())))

    df_length = len(temp_df)
    
    word_list = flatten_list(temp_df['tags'].to_list())
    #print(word_list)
#     list_updated = [word for word in word_list if word not in stop_words] 
#     d = Counter(list_updated)
#     wc = WordCloud(stopwords = stop_words,background_color='white', width=550, height=400,max_words=30)
#     wc.fit_words(d)

#     keyword_df = pd.DataFrame(wc.words_,index=[0]).T.reset_index()
#     #print(keyword_df)
#     keyword_df.columns = ['Keyword','Relevance']
#     keyword_df['Relevance'] = keyword_df['Relevance'].apply({lambda x : round(x,2)})
    
#     return keyword_df.head(10).to_dict('records')
        
    if len(temp_df) >5:
        keyword_df = top_keywords_df(flatten_list(temp_df['tags'].to_list()))
        keyword_df['Relevance%'] = round(100*keyword_df['Frequency']/df_length,2)
        keyword_df =keyword_df.drop(['Frequency'], axis = 1)
        #print(keyword_df)
        return keyword_df.head(10).to_dict('records')
    


## HORIZONTAL BAR CHART
@app.callback(
    #Output('graph_4', 'img'),
    Output('graph_5', 'figure'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 

     State('product_id', 'value')
     ]
    )
def update_graph_5(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase, product_id):

    star_rating_str = str(star_rating)[1:-1]
    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("****************UPDATE H. BAR CHART********************")
    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase, 
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)


    for key, val in filt_dict_updated.items():
        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]
        #print("Len of dataframe = {}".format(len(temp_df)))

    grouped_df = temp_df.groupby(['star_rating'], as_index= False)['review_id'].count()

    if len(temp_df) >0:
        fig = go.Figure([go.Bar(x = grouped_df['review_id'], y = grouped_df['star_rating'], marker_color = 'royalblue',
                             orientation = 'h',
                             textposition = 'outside',
                              name=""
                             )])
        fig.update_xaxes(title='# Review Count', showline=True,
                linewidth=1,
                linecolor='grey',
                mirror=True)

        fig.update_yaxes(title = "Star rating on Marketplace",showline=True,
                linewidth=1,
                linecolor='grey',
                mirror=True)
        
        fig.update_layout(title='Bar Chart of Star Rating Distribution')
        fig.update_traces(
        hovertemplate="<br>".join([
            "#Reviews: %{x}",
            "Star Rating: %{y}"
        ])
        )

        return fig
    else :
        return {
        "layout": {
            "xaxis": {
                "visible": True
            },
            "yaxis": {
                "visible": True
            },
            "annotations": [
                {
                    "text": "No matching data found",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        }
    }

#####################################################################################


 ## PIE CHART       
@app.callback(
    #Output('graph_4', 'img'),
    Output('graph_6', 'figure'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 

     State('product_id', 'value')
     ]
    )
def update_graph_6(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase, product_id):

    star_rating_str = str(star_rating)[1:-1]
    temp_df = data.query('review_date > @start_date & review_date < @end_date')

    print("**************** PIE CHART ********************")

    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)

    for key, val in filt_dict_updated.items():
        #print("Filtering {}".format(key))
        temp_df = temp_df[temp_df[key].isin(val)]
        #print("Len of dataframe = {}".format(len(temp_df)))

    grouped_df = temp_df.groupby(['sentiment_tag'], as_index= False)['review_id'].count()
    
    #print("grouped DF :{}".format(grouped_df))
    print("getting pie chart")
    if len(temp_df) >0:
        fig =  px.pie(
          grouped_df,
            values='review_id',
            names='sentiment_tag',
            color ='sentiment_tag',
            hole=.3,
            color_discrete_map=  #["#F6635C", "#85A389"]
            
            {'POSITIVE':'#85A389'  ,
                                 'NEGATIVE':'#F6635C'}
            
        )

        fig.update_layout(title='Piechart of Sentiment Distribution')
        fig.update_traces(
        hovertemplate="<br>".join([

            "#Reviews: %{value}"
        ])
        )
        return fig
    
    else :
        return {
        "layout": {
            "xaxis": {
                "visible": True
            },
            "yaxis": {
                "visible": True
            },
            "annotations": [
                {
                    "text": "No matching data found",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        }
    }

#####################################################################################       



## REVIEW TABLE
@app.callback(
    Output('table_reviews', 'data'),
    [Input('submit_button', 'n_clicks'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')],
    [State('star_rating', 'value'), 
     State('sentiment_list', 'value'), 
     State('verified_purchase', 'value'), 

     State('product_id', 'value')
     ]
    )
def update_review_table(n_clicks, start_date, end_date,star_rating, sentiment_list, verified_purchase, product_id):

    temp_df = data.query('review_date > @start_date & review_date < @end_date')
    print("*************** TABLE OF KEYWORDS *********************")

    filt_dict = {'star_rating':star_rating,
                 'sentiment_tag': sentiment_list, 
                  'verified_purchase':verified_purchase,
                 'product_id' : product_id}
    
    filt_dict_updated = update_dictionary(filt_dict)

    for key, val in filt_dict_updated.items():
        temp_df = temp_df[temp_df[key].isin(val)]

    temp_df = temp_df[review_cols]
    #emp_df['review_date'] =  temp_df['review_date'].dt.strftime('%d-%m-%Y')
    
    temp_df.columns = ['Product ID','Review Date','Review Text']
    temp_df = temp_df.sort_values(['Review Date'], ascending = False)
    temp_df = temp_df.drop_duplicates(['Product ID', 'Review Text'], keep='first')

    if len(temp_df) >0:
        return temp_df.head(20).to_dict('records')
    
    else :
        return "Insufficient data"



#Update dropDown1 options
@app.callback([
        Output('my-date-picker-range', 'start_date'),
        Output('my-date-picker-range', 'end_date'),
        Output('star_rating', 'value'), 
        Output('sentiment_list', 'value'), 
        Output('verified_purchase', 'value'), 

        Output('product_id', 'value')],
        [Input('clear_button', 'n_clicks')],
        )

def clearDropDown1(n_clicks):
    print("**************** CLEAR ALL FUNCTION ********************")
    if n_clicks != 0: #Don't clear options when loading page for the first time
        return ['2023-08-01','2023-08-31',['1','2','3','4'],['POSITIVE','NEGATIVE'],
             ['Y','N'],
             list(data['product_id'].unique())
               ] #Return an empty list of options
    
    
## LAST 30 days button

# @app.callback([
#         Output('my-date-picker-range', 'start_date'),
#         Output('my-date-picker-range', 'end_date')],
#         Input('last_30_days', 'n_clicks'),
#         )
# def update_last_30(n_clicks):
#     print("**************** LAST 30 DAYS ********************")
#     if n_clicks != 0: #Don't clear options when loading page for the first time
#         max_date = datetime(2023,8,23).strftime("%Y-%m-%d")
#         min_date = (datetime.now().date() - timedelta(30)).strftime("%Y-%m-%d")
        
        
#     return ['2023-07-01','2023-08-01'] #Return an empty list of options










if __name__ == '__main__':
    app.run_server(port='8085')




