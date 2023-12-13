import streamlit as st
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import geojson

def modify(x):
    acceptable_length = 100
    if (len(x) < acceptable_length):
        return x
    else: 
        return x[: acceptable_length] + "..."


mapbox_access_token = "pk.eyJ1IjoiYW1hbnp5MTIzNCIsImEiOiJjbG9land0NjcwazR6MmtvMjgycTJ2bHp2In0.wEKHMlZHua7rHUV0Av03UQ"
px.set_mapbox_access_token(mapbox_access_token)

st. set_page_config(layout="wide")
st.title("HiRISK High Mountain Asia")
df_avalanches = pd.read_csv("HiAVALDB.csv", encoding = "latin1")
df_avalanches = df_avalanches.drop(["Unnamed: 0"], axis=1)

df_glofs = pd.read_csv("HMAGLOFDB (2).csv", encoding = "latin1")

@st.cache_resource
def get_gj(): 
    with open('HIMAP_boundaries.geojson') as f:
        gj = geojson.load(f)

    return gj


def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

event_checkbox = st.selectbox("Select Hazard Type", ["Avalanches","GLOF"])
st.divider()


if(event_checkbox == "GLOF"):
    # pass 
    
    df = df_glofs.copy()

    with st.container():
        col1, col2, col3 = st.columns([0.2, 0.5,0.3])
    
    # Filter by country 
    # country = col1.selectbox("Select country", sorted(df['Country'].drop_duplicates().tolist()))
    # df = df.loc[(df["Country"]  == country)]
    # col1.divider()


    # # Filter by river basin 
    # river_basin = col1.multiselect("Filter By River Basin",  df['River_Basin'].dropna().drop_duplicates().tolist(), default = df['River_Basin'].dropna().drop_duplicates().tolist()[0])
    # df = df.loc[(df["River_Basin"].isin(river_basin))]
    # col1.divider()
    
    
    # if(len(river_basin)>0):

    
    # Filter by Lake type 
    lake_type = col1.multiselect("Filter By Lake Type", df["Lake_type"].dropna().drop_duplicates().tolist(), default = df["Lake_type"].dropna().drop_duplicates().tolist()[0])

    if(len(lake_type)>0):

        df = df.loc[df["Lake_type"].isin(lake_type)]

        col_1, col_2, col_3= col2.columns([0.33, 0.33, 0.33])
        col_1.write("Total Fatalities: " + str(df["Lives_total"].str.replace('[^0-9]', '').replace("+", "").replace(u'\xa0', '0').replace('', np.nan).fillna(0).astype(int).sum()))
        col_2.write(str("Total Injured: " + str(int(df["Injured_total"].replace('', np.nan).fillna(0).astype(int).sum()))))
        col_3.write(str("Total Incidents: " + str(df.shape[0])))



        plot_df = df.loc[~(df["Lat_impact"].isna()) & ~(df["Lon_impact"].isna())]
        plot_df["Remarks"] = plot_df["Remarks"].replace(np.nan, "")
        plot_df= plot_df.replace(np.nan , "")
        
        fig = go.Figure()
        fig.add_trace(go.Scattermapbox(
                lat=plot_df["Lat_impact"],
                lon=plot_df["Lon_impact"],
                mode = "markers",
                marker=go.scattermapbox.Marker(
                    size=14,
                    color='rgb(255, 0, 0)',
                    opacity=0.7, 
                ),
                text=df["Remarks"].fillna("").apply(modify),
                textposition = "bottom right",
                
                customdata=plot_df[["Year_approx", "Lake_name","Glacier_name","G_ID","Lake_type", "Country"]],
                hovertemplate="%{lon}, %{lat}<br>Time Period: %{customdata[0]}<br><br>Lake Name: %{customdata[1]}<br>Lake Type: %{customdata[4]}<br><br>Glacier Name: %{customdata[2]}<br>G_ID: %{customdata[3]}<br><br>Remarks: %{text}<extra>Country: %{customdata[5]}</extra>",
            ))
        fig.update_layout(mapbox_layers=[{
                    "below": 'traces',
                    "sourcetype": "geojson",
                    "type": "line",
                    "color": "black",
                    "source": get_gj()
                }])

        fig.update_layout(
            autosize=True,
            hovermode='closest',
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=dict(
                    lat=36,
                    lon=85
                ),
                pitch=0,
                zoom=3.8,
                style='light'
            ),
                height = 650, 
                margin=dict(l=0,r=0,b=0,t=0)
        )
        col2.plotly_chart(fig, use_container_width=True)
    

        # Make a pie chart for the mechanism 
        pie_df = df["Mechanism"].value_counts().reset_index()

        fig2 = px.pie(pie_df, names = "Mechanism", values = "count", title="Mechanisms of lake breach", height = 320)
        fig2.update_layout(margin = dict( b=0))
        col3.plotly_chart(fig2, use_container_width=True)

        bar_df = df["Lake_type"].value_counts().reset_index()

        fig3 = px.bar(bar_df, y = 'count', x = 'Lake_type', height = 400, title = "Types of Lakes")
        fig3.update_traces(width=0.2)
        fig3.update_xaxes(title='')
        col3.plotly_chart(fig3, use_container_width=True)

        st.divider()
        st.dataframe(df, use_container_width=True)

        csv = convert_df(df)
        st.download_button(
        "Download Data",
        csv,
        f"Filtered GLOF Data.csv",
        "text/csv",
        key='download-csv'
        )





elif(event_checkbox == "Avalanches"):
    df = df_avalanches.copy()
    with st.container():
        col1, col2, col3 = st.columns([0.2, 0.5,0.3])


    '''
    Removing country filter
    '''

    # country = col1.selectbox("Select country", sorted(df['Country'].drop_duplicates().tolist()))
    # col1.divider()
    # df = df.loc[(df["Country"]  == country)]


    if(len(df['Type'].dropna().drop_duplicates().tolist()) > 0 ):
        avalanche_type = col1.multiselect("Select Avalanche Type",  df['Type'].dropna().drop_duplicates().tolist(), default = df['Type'].dropna().drop_duplicates().tolist()[0])
    else: 
        avalanche_type = col1.multiselect("Select Avalanche Type",  df['Type'].dropna().drop_duplicates().tolist())



    # df = df.loc[(df["Country"]  == country) & (df["Type"].isin(avalanche_type))]
    df = df.loc[(df["Type"].isin(avalanche_type))]
    df["Year"] = df["Year"].astype(int)
    min_year = df["Year"].min() 
    max_year = df["Year"].max()


    col1.divider()

    if (len(avalanche_type) > 0):

        years = col1.multiselect('Filter incidents by Year',tuple(sorted(df["Year"].unique().tolist())),tuple(sorted(df["Year"].unique().tolist()))[-1])
        
        if(len(years)> 0):

            df = df.loc[df["Year"].isin(years)]

            col_1, col_2, col_3= col2.columns([0.33, 0.33, 0.33])
            col_1.write("Total Fatalities: " + str(df["Fatalities"].sum()))
            col_2.write("Total Injured: "+ str(int(df["Injured"].sum())))
            col_3.write("Total Incidents: " + str(df.shape[0]))


            plot_df = df.loc[~(df["Latitude"].isna()) & ~(df["Longitude"].isna())]
            plot_df["Remarks"] = plot_df["Remarks"].replace(np.nan, "")
            if plot_df.shape[0] > 0 and len(avalanche_type) > 0:
                fig = go.Figure()
                fig.add_trace(go.Scattermapbox(
                        lat=plot_df["Latitude"],
                        lon=plot_df["Longitude"],
                        mode = "markers",
                        marker=go.scattermapbox.Marker(
                            size=14,
                            color='rgb(0, 0, 255)',
                            opacity=0.7, 
                        ),
                        # name = df["Location"],
                        text = df["Remarks"].fillna("").apply(modify),
                        textposition = "bottom right",
                        
                        # hoverinfo='text', 
                        customdata=plot_df[["Location", "Fatalities","Day","Month","Year", "Country", "Type"]],
                        hovertemplate="%{lon}, %{lat}<br>Date: %{customdata[2]}-%{customdata[3]}-%{customdata[4]}<br>Type: %{customdata[6]}<br><br>Fatalities: %{customdata[1]}<br>Remarks:%{text}<extra><h1>Location: %{customdata[0]}<br><br>Country: %{customdata[5]}</h1></extra>",
                    ))
                fig.update_layout(mapbox_layers=[{
                            "below": 'traces',
                            "sourcetype": "geojson",
                            "type": "line",
                            "color": "black",
                            "source": get_gj()
                        }])

                fig.update_layout(
                    autosize=True,
                    hovermode='closest',
                    showlegend=False,
                    mapbox=dict(
                        accesstoken=mapbox_access_token,
                        bearing=0,
                        center=dict(
                            lat=36,
                            lon=85
                        ),
                        pitch=0,
                        zoom=3.8,
                        style='light'
                    ),
                    height = 650, 
                    margin=dict(l=0,r=0,b=0,t=0)
                )
                col2.plotly_chart(fig, use_container_width=True)

            else: 
                col2.map()


            df["Year"] = df["Year"].astype(str)
            


            fig2 = px.bar(df.groupby("Type").sum(), y = "Fatalities", height = 700,)
            fig2.update_traces(width=0.2)
            # fig2.update_yaxes(title='', visible=True, showticklabels=True,title_font=dict(size=12))
            fig2.update_layout(margin=dict(r = 0), title="Fatalities by Avalanche Type")
            col3.plotly_chart(fig2, theme= None, use_container_width=True)


            st.divider()
            st.dataframe(df, use_container_width=True)



            csv = convert_df(df)
            st.download_button(
            "Download Data",
            csv,
            f"Filtered Glacier Data.csv",
            "text/csv",
            key='download-csv'
            )
            st.title("References")
            
else:
    pass

