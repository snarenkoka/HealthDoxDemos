import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to fetch data from a Supabase table
def fetch_data(table_name: str):
    try:
        # Query data from the specified table
        response = supabase.table(table_name).select("*").execute()
        if response.data:
            return pd.DataFrame(response.data)  # Convert to pandas DataFrame
        else:
            st.write(f"No data found in the table '{table_name}'.")
            return pd.DataFrame()  # Return an empty DataFrame if no data found
    except Exception as e:
        st.error(f"An error occurred while fetching data: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Function to categorize risk based on risk score
def categorize_risk(score):
    if score > 17:
        return "Very High"
    elif 10 < score <= 17:
        return "High"
    elif 5 <= score <= 10:
        return "Medium"
    else:
        return "Low"
    

# Function to categorize impact
def categorize_impact(value):
    if value <= 2:
        return "Insignificant"
    elif 3 <= value <=4 :
        return "Moderate"
    else:
        return "Critical"

# Function to categorize likelihood
def categorize_likelihood(value):
    if value <= 2:
        return "Unlikely"
    elif 3 <= value <= 4:
        return "Potential"
    else:
        return "Likely"

def create_green_heatmap(data):
    try:
        st.subheader("Risk Heatmap Visualization")

        # Define a consistent custom color scale
        custom_color_scale = [
            (0.0, "green"),   # Low risk
            (0.25, "yellow"), # Medium-low risk
            (0.5, "orange"),  # Medium-high risk
            (1.0, "red")      # High risk
        ]

        # Create the heatmap using Plotly
        fig = px.density_heatmap(
            data_frame=data,
            x="likelihood",
            y="impact",
            z="risk_score",
            color_continuous_scale=["green", "yellow", "orange", "red"],
            labels={"likelihood": "Likelihood", "impact": "Impact", "risk_score": "Risk Score"},
        )

        # Show the heatmap
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error creating heatmap: {str(e)}")

# def create_timeline_chart(data):
#     try:
#         st.subheader("Incident Timeline by Severity Level")

#         # Convert Date and Time columns to a single datetime column
#         data['Datetime'] = pd.to_datetime(data['date'] + ' ' + data['time'], errors='coerce')

#         # Drop rows with invalid or missing datetime values
#         data = data.dropna(subset=['Datetime'])

#         # Sort data by Datetime for better visualization
#         data = data.sort_values(by='Datetime')

#         # Create a timeline chart using Plotly
#         fig = px.scatter(
#             data,
#             x='location',
#             y='Datetime',
#             color='severity_level',
#             hover_data=['incident_type', 'description', 'outcome', 'reporting_staff_role', 'followup_actions'],
#             labels={
#                 "Datetime": "Datetime",
#                 "Location": "location",
#                 "Severity Level": "severity_level"
#             },
#             # title="Incident Timeline by Severity Level"
#         )

#         # Customize layout for better appearance
#         fig.update_layout(
#             title="",
#             xaxis_title="Date & Time",
#             yaxis_title="Location",
#             template="plotly_white",
#             title_x=0.5
#         )

#         # Show the chart in Streamlit
#         st.plotly_chart(fig)
#     except Exception as e:
#         st.error(f"Error creating timeline chart: {str(e)}")

def create_bubble_chart(data):
    try:
        st.subheader("Severity vs. Likelihood Bubble Chart")

        # Group data by Severity Level, Likelihood, and Incident Type to count occurrences
        grouped_data = data.groupby(['severity_level', 'likelihood', 'incident_type'], as_index=False).size()

        # Create a bubble chart using Plotly
        fig = px.scatter(
            grouped_data,
            x='incident_type',
            y='likelihood',
            size='size',
            color='severity_level',
            hover_data=['size'],
            labels={
                "Severity Level": "severity_level",
                "Likelihood": "likelihood",
                "size": "Number of Incidents",
                "Incident Type": "Incident Type"
            },
            title="Bubble Chart: Severity vs. Likelihood by Incident Type"
        )

        # Customize layout for better appearance
        fig.update_layout(
            xaxis_title="Severity Level",
            yaxis_title="Likelihood",
            template="plotly_white",
            title_x=0.5
        )

        # Show the chart in Streamlit
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error creating bubble chart: {str(e)}")

def create_location_chart(data):
    try:
        st.subheader("Incident Distribution by Location")

        # Count the number of incidents per location
        location_counts = data['location'].value_counts().reset_index()
        location_counts.columns = ['location', 'Count']

        # Create a pie chart
        fig_pie = px.pie(
            location_counts,
            names='location',
            values='Count',
            title="Percentage of Incidents by Location",
            labels={"Location": "location", "Count": "Number of Incidents"}
        )

        # Create a bar chart
        fig_bar = px.bar(
            location_counts,
            x='location',
            y='Count',
            title="Number of Incidents by Location",
            labels={"Location": "Location", "Count": "Number of Incidents"},
            text='Count'
        )
        fig_bar.update_layout(template="plotly_white", xaxis_title="Location", yaxis_title="Number of Incidents")

        # Display the charts
        st.plotly_chart(fig_pie)
        st.plotly_chart(fig_bar)
    except Exception as e:
        st.error(f"Error creating location charts: {str(e)}")

def create_heatmap(data):
    try:
        st.subheader("Risk Heatmap Visualization (Categorized)")

        # Categorize impact and likelihood columns
        data["Impact Category"] = data["impact"].apply(categorize_impact)
        data["Likelihood Category"] = data["likelihood"].apply(categorize_likelihood)

        # Handle duplicates by aggregating (e.g., take the average risk_score)
        data = data.groupby(["Impact Category", "Likelihood Category"], as_index=False).agg({"risk_score": "mean"})

        # Prepare the data for the heatmap
        heatmap_data = data.pivot(index="Impact Category", columns="Likelihood Category", values="risk_score")

        # Ensure the correct order of categories
        heatmap_data = heatmap_data.reindex(
            index=["Critical", "Moderate", "Insignificant"],
            columns=["Unlikely", "Potential", "Likely"]
        )

        # Replace NaN with a specific value for visualization
        heatmap_data_filled = heatmap_data.fillna(0)# Fill NaN with a placeholder (-1)

        # Create a heatmap using Plotly
        fig = px.imshow(
            heatmap_data_filled,
            color_continuous_scale=[
                "green", "yellow", "orange", "red"
            ],
            labels={
                "x": "Likelihood",
                "y": "Impact",
                "color": "Risk Score",
            }
            # title="Risk Heatmap (Categorized)",
        )

        # Customize the color scale to handle the placeholder value
        fig.update_traces(
            # zmin=-1,  # Include the placeholder in the color scale
            zmax=heatmap_data_filled.max().max(),  # Maximum value in the data
            colorbar=dict(
                tickvals=[ 0,5, 10, 15, 20, 25],
                ticktext=["Low", "Medium", "High", "Very High", "Critical", "Extreme"]
            )
        )

        # Customize the layout
        fig.update_layout(
            title ="",
            xaxis_title="Likelihood",
            yaxis_title="Impact",
            title_x=0.5,
            template="plotly_white"
        )

        # Show the heatmap
        st.plotly_chart(fig)


    except Exception as e:
        st.error(f"Error creating heatmap: {str(e)}")

def display_risk_ranking_table():
    st.markdown("""
    <style>
        table {
            width: 60%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 18px;
            text-align: left;
        }
        th, td {
            padding: 12px;
            border: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
        .low {
            color: green;
            font-weight: bold;
        }
        .medium {
            color: yellow;
            font-weight: bold;
        }
        .high {
            color: orange;
            font-weight: bold;
        }
        .very-high {
            color: red;
            font-weight: bold;
        }
        .unknown {
            color: gray;
            font-weight: bold;
        }        
    </style>
    <table>
        <tr>
            <th>Risk Score Severity</th>
            <th>Risk Score Product (Impact *Likelihood)</th>
        </tr>
        <tr>
            <td class="very-high">VERY HIGH</td>
            <td>Greater than </b>17</td>
        </tr>
        <tr>
            <td class="high">HIGH</td>
            <td>Greater than </b>10, but less than or equal to </b>17</td>
        </tr>
        <tr>
            <td class="medium">MEDIUM</td>
            <td>Greater than </b>5, but less than </b>10</td>
        </tr>
        <tr>
            <td class="low">LOW</td>
            <td>Less than </b>5</td>
        
        
    </table>
    """, unsafe_allow_html=True)



def main():
    st.title("HealthDox Data Visualization")

    # Sidebar for table selection and buttons
    st.sidebar.header("Dashboard")
    table_options = ["Incident_Dataset", "Risk_Heatmap"]
    selected_table = st.sidebar.selectbox("Select Table", table_options)

    if st.sidebar.button("Process Table"):
        # Fetch and display the selected table
        data = fetch_data(selected_table)
        if not data.empty:
            st.subheader(f"{selected_table} Dataset")
            st.dataframe(data)

    if st.sidebar.button("View Visualization"):
        # Fetch data and generate heatmap for Risk_Heatmap table
        if selected_table == "Risk_Heatmap":
            risk_heatmap_data = fetch_data("Risk_Heatmap")
            if not risk_heatmap_data.empty:
                create_green_heatmap(risk_heatmap_data)
                create_heatmap(risk_heatmap_data)
                display_risk_ranking_table()

        if selected_table == "Incident_Dataset":
            incident_data = fetch_data("Incident_Dataset")
            if not incident_data.empty:
                # create_timeline_chart(incident_data)
                create_bubble_chart(incident_data)
                create_location_chart(incident_data)


    

if __name__ == "__main__":
    main()
