# import pandas as pd
# import streamlit as st
# import asyncio
# from huggingface_hub import InferenceClient
# # import os
# # from dotenv import load_dotenv
# import re

# # load_dotenv()

# # Load API keys
# HF_API_KEY = st.secrets["HF_API_KEY"]

# # Initialize Hugging Face client
# client = InferenceClient(api_key=HF_API_KEY)

# def infer_schema(file):
#     """Infer schema of the uploaded CSV file."""
#     df = pd.read_csv(file)
#     schema = [{"Column Name": column, "Data Type": str(df[column].dtype)} for column in df.columns]
#     return schema, df

# async def generate_incident_data_with_llama(num_records):
#     """Generate incident types along with Impact and Likelihood scores using the LLaMA model."""
#     try:
#         messages = [{
#             "role": "user",
#             "content": f"""Generate exactly {num_records} random, medically relevant incident types, ensuring each incident type is unique and concise (limited to 2-3 words). The generated incident types should be directly related to medical scenarios, such as 'Pressure Ulcer', 'Equipment Failure', 'Infection Control', etc.
                    
#             The output should:
#             1. Contain only unique values with no duplicates.
#             2. It should only contain incident type. No other text should be generated apart from incident type.
#             3. Be formatted with one incident type per line.
#             4. Include only meaningful and realistic medical terms.
#             5. Please don't keep any values null.
#             6. Srictly make sure that you do not add any numbers in the incident type column while generating the response. If it gets generated just remove them and only get the incident type details.
                    
#             Additionally, for each incident type, assign an Impact score and a Likelihood score.Impact and Likelihood should be integers between 1 and 10, where 1 represents the lowest severity or probability and 6 represents the highest severity or probability.
            
#             The output should be formatted as follows:
#             Incident Type: Impact, Likelihood
            
#             Example:
#             Pressure Ulcer: 4, 5
#             Equipment Failure: 5, 3
            
#             Provide exactly {num_records} unique incident types with their corresponding Impact and Likelihood values.
            
#             """
#         }]

#         response = await asyncio.to_thread(
#             client.chat.completions.create,
#             model="meta-llama/Llama-3.3-70B-Instruct",
#             messages=messages,
#             max_tokens=2000
#         )
        
#         lines = response["choices"][0]["message"]["content"].strip().split("\n")
#         incident_data = []

#         for line in lines:
#             match = re.match(r"^([^\d:]+):\s*(\d),\s*(\d)$", line)
#             if match:
#                 incident_type, impact, likelihood = match.groups()
#                 incident_type = incident_type.strip()
#                 if incident_type and impact.isdigit() and likelihood.isdigit():
#                     incident_data.append((incident_type, int(impact), int(likelihood)))
        
#         if len(incident_data) < num_records:
#             missing_count = num_records - len(incident_data)
#             existing_samples = incident_data.copy()
#             while len(incident_data) < num_records:
#                 random_sample = existing_samples[len(incident_data) % len(existing_samples)]
#                 incident_data.append(random_sample)
#         return incident_data[:num_records]
#     except Exception as e:
#         return [("Error: AI generation failed", 3, 3)] * num_records

# def main():
#     st.title("Risk Score Tool Generator")
#     st.write("Upload a CSV file, generate random data, and calculate risk scores using AI.")
    
#     st.sidebar.header("Settings")
#     uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type="csv")
#     num_records = st.sidebar.number_input("Enter the number of records to generate:", min_value=1, step=1, value=10)
#     generate_button = st.sidebar.button("Generate Data")
    
#     if uploaded_file is not None:
#         try:
#             schema, df = infer_schema(uploaded_file)

#             if generate_button:
#                 with st.spinner("Generating Incident Data..."):
#                     incident_data = asyncio.run(generate_incident_data_with_llama(num_records))
                
#                 generated_data = pd.DataFrame({
#                     "Incident ID": range(1, num_records + 1),
#                     "Incident Type": [item[0] for item in incident_data],
#                     "Impact": [item[1] for item in incident_data],
#                     "Likelihood": [item[2] for item in incident_data],
#                 })

#                 generated_data["Risk Score"] = generated_data["Impact"] * generated_data["Likelihood"]
                
#                 st.write("### Generated Risk Score Data:")
#                 st.write(generated_data)

#                 csv = generated_data.to_csv(index=False).encode("utf-8")
#                 st.download_button(
#                     label="Download Risk Score Data as CSV",
#                     data=csv,
#                     file_name="Risk_Score.csv",
#                     mime="text/csv",
#                 )
#         except Exception as e:
#             st.error(f"An error occurred: {e}")
#     else:
#         st.info("Please upload a CSV file in the sidebar to begin.")

# if __name__ == "__main__":
#     main()


import pandas as pd
import streamlit as st
import asyncio
from huggingface_hub import InferenceClient
# import os
# from dotenv import load_dotenv
import re

# load_dotenv()

# Load API keys
HF_API_KEY = st.secrets["HF_API_KEY"]

# Initialize Hugging Face client
client = InferenceClient(api_key=HF_API_KEY)

def infer_schema(file):
    """Infer schema of the uploaded CSV file."""
    df = pd.read_csv(file)
    schema = [{"Column Name": column, "Data Type": str(df[column].dtype)} for column in df.columns]
    return schema, df

async def generate_incident_data_with_llama(num_records):
    """Generate incident types along with Impact and Likelihood scores using the LLaMA model."""
    try:
        messages = [{
            "role": "user",
            "content": f"""Generate unique medically relevant incident types 1.5 times more than the records provided as input {num_records}, ensuring each incident type is unique and concise (limited to 2-3 words). The generated incident types should be directly related to medical scenarios, such as 'Pressure Ulcer', 'Equipment Failure', 'Infection Control', etc.
                    
            The output should:
            1. Contain only unique values with no duplicates.
            2. It should only contain incident type. No other text should be generated apart from incident type.
            3. Be formatted with one incident type per line.
            4. Include only meaningful and realistic medical terms.
            5. Please don't keep any values null.
            6. Srictly make sure that you do not add any numbers in the incident type column while generating the response. If it gets generated just remove them and only get the incident type details.
                    
            Additionally, for each incident type, assign an Impact score and a Likelihood score.Impact and Likelihood should be integers between 1 and 10, where 1 represents the lowest severity or probability and 6 represents the highest severity or probability.
            
            The output should be formatted as follows:
            Incident Type: Impact, Likelihood
            
            Example:
            Pressure Ulcer: 4, 5
            Equipment Failure: 5, 3
            
            
            
            """
        }]

        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=messages,
            max_tokens=2000
        )
        
        lines = response["choices"][0]["message"]["content"].strip().split("\n")
        incident_data = []

        for line in lines:
            match = re.match(r"^([^\d:]+):\s*(\d),\s*(\d)$", line)
            if match:
                incident_type, impact, likelihood = match.groups()
                incident_type = incident_type.strip()
                if incident_type and impact.isdigit() and likelihood.isdigit():
                    incident_data.append((incident_type, int(impact), int(likelihood)))
        
        if len(incident_data) < num_records:
            missing_count = num_records - len(incident_data)
            existing_samples = incident_data.copy()
            while len(incident_data) < num_records:
                random_sample = existing_samples[len(incident_data) % len(existing_samples)]
                incident_data.append(random_sample)
        return incident_data[:num_records]
    except Exception as e:
        return [("Error: AI generation failed", 3, 3)] * num_records

def main():
    st.title("Risk Score Tool Generator")
    st.write("Upload a CSV file, generate random data, and calculate risk scores using AI.")
    
    st.sidebar.header("Settings")
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type="csv")
    num_records = st.sidebar.number_input("Enter the number of records to generate:", min_value=1, step=1, value=10)
    generate_button = st.sidebar.button("Generate Data")
    
    if uploaded_file is not None:
        try:
            schema, df = infer_schema(uploaded_file)

            if generate_button:
                with st.spinner("Generating Incident Data..."):
                    incident_data = asyncio.run(generate_incident_data_with_llama(num_records))
                
                generated_data = pd.DataFrame({
                    "Incident ID": range(1, num_records + 1),
                    "Incident Type": [item[0] for item in incident_data],
                    "Impact": [item[1] for item in incident_data],
                    "Likelihood": [item[2] for item in incident_data],
                })

                generated_data["Risk Score"] = generated_data["Impact"] * generated_data["Likelihood"]
                
                st.write("### Generated Risk Score Data:")
                st.write(generated_data)

                csv = generated_data.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Risk Score Data as CSV",
                    data=csv,
                    file_name="Risk_Score.csv",
                    mime="text/csv",
                )
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.info("Please upload a CSV file in the sidebar to begin.")

if __name__ == "__main__":
    main()
