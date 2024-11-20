import streamlit as st
import pandas as pd
from agents import process_data

def main():
    # Configure the page
    st.set_page_config(
        page_title="AI Data Generator",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Add content
    st.title("AI Data Generator")
    st.subheader("Generate structured data using AI")

    # Sidebar information
    with st.sidebar:
        st.header("About")
        st.write("""
        This application uses AI to analyze and generate structured data based on your input CSV file.
        
        How it works:
        1. Upload your sample CSV file
        2. Our AI analyzes the patterns, relationships, and structure
        3. Generate new data that matches your sample's characteristics
        4. Download the generated data in CSV format
        
        Use cases:
        - Generate test data for development
        - Create synthetic datasets for training
        - Expand small datasets
        - Generate realistic mock data
        """)

    # Main content
    st.write("Upload your CSV file to get started. The AI will analyze its structure and generate similar data.")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

    if uploaded_file is not None:
        try:
            # Read and display the input data
            st.subheader("Input Data")
            input_df = pd.read_csv(uploaded_file)
            
            # Display sample info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Number of Rows", len(input_df))
            with col2:
                st.metric("Number of Columns", len(input_df.columns))
            with col3:
                st.metric("Sample Size", min(5, len(input_df)))
            
            # Show data preview
            with st.expander("Preview Input Data"):
                st.dataframe(input_df)
            
            # Display column information
            with st.expander("Column Information"):
                col_info = pd.DataFrame({
                    'Data Type': input_df.dtypes,
                    'Non-Null Count': input_df.count(),
                    'Null Count': input_df.isnull().sum(),
                    'Unique Values': input_df.nunique()
                })
                st.dataframe(col_info)
            
            # Save the uploaded file temporarily
            input_df.to_csv("input.csv", index=False)
            
            # Generation options
            st.subheader("Generation Options")
            col1, col2 = st.columns(2)
            
            with col1:
                num_rows = st.number_input(
                    "Number of rows to generate", 
                    min_value=1,
                    max_value=1000,
                    value=min(30, len(input_df))
                )
            
            with col2:
                maintain_ratios = st.checkbox(
                    "Maintain data distributions",
                    value=True,
                    help="Try to maintain similar distributions of values as in the input data"
                )
            
            # Add generate button
            if st.button("Generate Data", key='generate_button'):
                with st.spinner("Analyzing and generating data..."):
                    try:
                        # Process the data
                        output_file = "generated_data.csv"
                        result_df, result_message = process_data(
                            "input.csv", 
                            output_file, 
                            num_rows,
                            maintain_distributions=maintain_ratios
                        )
                        
                        # Display results
                        if result_df is not None:
                            st.success("Successfully generated data!")
                            
                            # Display analysis
                            with st.expander("View Analysis"):
                                st.write(result_message)
                            
                            # Compare distributions if requested
                            if maintain_ratios:
                                st.subheader("Data Distribution Comparison")
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write("Original Data Sample")
                                    st.dataframe(input_df.head())
                                
                                with col2:
                                    st.write("Generated Data Sample")
                                    st.dataframe(result_df.head())
                            
                            # Display generated data
                            st.subheader("Generated Data")
                            st.dataframe(result_df)
                            
                            # Add download options
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    label="Download as CSV",
                                    data=result_df.to_csv(index=False),
                                    file_name="generated_data.csv",
                                    mime="text/csv"
                                )
                            with col2:
                                st.download_button(
                                    label="Download as Excel",
                                    data=result_df.to_excel(index=False),
                                    file_name="generated_data.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                            
                        else:
                            st.error(f"Error: {result_message}")
                            
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.write("Please check that:")
                        st.write("- The CSV file is properly formatted")
                        st.write("- All required columns have valid data")
                        st.write("- There are no special characters causing issues")
        
        except Exception as e:
            st.error(f"Error reading the file: {str(e)}")
            st.write("Please make sure the CSV file is properly formatted.")

if __name__ == "__main__":
    main()
