import pandas as pd
import streamlit as st
import random
import asyncio
from huggingface_hub import InferenceClient
# import os
# from dotenv import load_dotenv

# load_dotenv()

# Load API keys
HF_API_KEY = st.secrets["HF_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


# Initialize Hugging Face client
client = InferenceClient(api_key=HF_API_KEY)

def infer_schema(file):
    """Infer schema of the uploaded CSV file."""
    df = pd.read_csv(file)
    schema = []

    for column in df.columns:
        col_type = df[column].dtype
        schema.append({"Column Name": column, "Data Type": str(col_type)})

    return schema, df

async def generate_incident_types_with_llama(num_records):
    """Generate unique medical incident types using the LLaMA model."""
    try:
        messages = [
            {
                "role": "user",
                "content": f"""Generate a list of random, medically relevant incident types, ensuring each incident type is unique and concise (limited to 2-3 words). The generated incident types should be directly related to medical scenarios, such as 'Pressure Ulcer', 'Equipment Failure', 'Infection Control', etc.

                    The output should:
                    
                    1.Contain only unique values with no duplicates.
                    2.It should only contain incident type. No other text should be generated apart from incident type.
                    3.Be formatted with one incident type per line.
                    4.Include only meaningful and realistic medical terms.
                    5.Please dont keep any values null.
                    6. Do not add numbers before adding the incident type in the table.

                    Avoid repetition or generic terms. Provide exactly the number of unique incident types requested."""
            }
        ]

        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=messages,
            max_tokens=500
        )

        incident_types = response["choices"][0]["message"]["content"].strip().split("\n")
        # Ensure enough records are generated
        while len(incident_types) < num_records:
            incident_types.extend(incident_types)  # Extend the list if not enough types are generated
        return [incident.strip() for incident in incident_types][:num_records]  # Trim to exact count

    except Exception as e:
        return [f"Error: {e}"] * num_records

def generate_random_data(df, num_records):
    """Generate random data based on the inferred schema."""
    random_data = pd.DataFrame()

    for column in df.columns:
        column_cleaned = column.strip().lower()
        if column_cleaned == "incident_id":
            random_data[column] = range(1, num_records + 1)  # Sequential unique values starting from 1
        elif column_cleaned == "likelihood":
            random_data[column] = [random.randint(1, 6) for _ in range(num_records)]  # Random integers between 1 and 6
        elif column_cleaned == "impact":
            random_data[column] = [random.randint(1, 6) for _ in range(num_records)]  # Random integers between 1 and 6
        else:
            random_data[column] = [None] * num_records  # Placeholder for other columns

    # Add Risk_Score column as product of Impact and Likelihood
    if "impact" in [col.strip().lower() for col in df.columns] and "likelihood" in [col.strip().lower() for col in df.columns]:
        random_data["Risk Score"] = (
            random_data[[col for col in df.columns if col.strip().lower() == "impact"][0]]
            * random_data[[col for col in df.columns if col.strip().lower() == "likelihood"][0]]
        )
    else:
        random_data["Risk Score"] = None  # Placeholder if columns are not available

    return random_data

# def main():
#     st.title("Risk Score Tool Generator")

#     st.write("Upload a CSV file to infer its schema and generate random data.")

#     # File uploader
#     uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

#     if uploaded_file is not None:
#         try:
#             # Infer schema
#             schema, df = infer_schema(uploaded_file)

#             # Get the number of records from the user
#             num_records = st.number_input("Enter the number of records to generate:")

#             if st.button("Generate Data"):
#                 # Generate random data
#                 random_data = generate_random_data(df, num_records)

#                 # Generate Incident Types using LLaMA model
#                 with st.spinner("Generating data for Risk Score dataset..."):
#                     incident_types = asyncio.run(generate_incident_types_with_llama(num_records))

#                 random_data["Incident Type"] = incident_types

#                 st.write("### Random Data Generated:")
#                 st.write(random_data)

#                 # Allow downloading of the generated data
#                 csv = random_data.to_csv(index=False).encode("utf-8")
#                 st.download_button(
#                     label="Download Risk Score Data as CSV",
#                     data=csv,
#                     file_name="Risk_Score.csv",
#                     mime="text/csv",
#                 )

#         except Exception as e:
#             st.error(f"An error occurred: {e}")

# if __name__ == "__main__":
#     main()

def main():
    st.title("Risk Score Tool Generator")

    st.write("Upload a CSV file to infer its schema and generate random data.")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            # Infer schema
            schema, df = infer_schema(uploaded_file)

            # Get the number of records from the user
            num_records = st.number_input(
                "Enter the number of records to generate:", min_value=1, step=1
            )

            if st.button("Generate Data"):
                # Convert num_records to integer
                num_records = int(num_records)

                # Generate random data
                random_data = generate_random_data(df, num_records)

                # Generate Incident Types using LLaMA model
                with st.spinner("Generating data for Risk Score dataset..."):
                    incident_types = asyncio.run(generate_incident_types_with_llama(num_records))

                random_data["Incident Type"] = incident_types

                st.write("### Random Data Generated:")
                st.write(random_data)

                # Allow downloading of the generated data
                csv = random_data.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Risk Score Data as CSV",
                    data=csv,
                    file_name="Risk_Score.csv",
                    mime="text/csv",
                )

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
