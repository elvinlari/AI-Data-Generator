import os
import pandas as pd
from io import StringIO
from openai import OpenAI
from prompts import *
from deal_tracker import DealTracker

# set up the Perplexity API key
if not os.getenv("PERPLEXITY_API_KEY"):
    os.environ["PERPLEXITY_API_KEY"] = input("Please enter your perplexity API key: ")

# Create the Perplexity client
base_url = "https://api.perplexity.ai"
client = OpenAI(api_key=os.getenv("PERPLEXITY_API_KEY"), base_url=base_url)
model = "llama-3.1-sonar-small-128k-online"

def read_data(file_path):
    """Read data from CSV file into a pandas DataFrame"""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return pd.DataFrame()

def save_data(data_df, output_file):
    """Save the generated data to a file"""
    try:
        # Get the file extension
        file_ext = os.path.splitext(output_file)[1].lower()
        
        # Save based on file type
        if file_ext == '.csv':
            data_df.to_csv(output_file, index=False)
        elif file_ext in ['.xlsx', '.xls']:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                data_df.to_excel(writer, index=False, sheet_name='Generated Data')
        else:
            print(f"Unsupported file format: {file_ext}")
            return False
            
        print(f"Successfully saved data to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving data: {str(e)}")
        return False

def parse_generated_data(data_text, columns):
    """Parse the generated data text into a DataFrame"""
    try:
        # Clean up the text and split into rows
        rows = []
        data_lines = [line.strip() for line in data_text.split('\n') if line.strip()]
        
        for line in data_lines:
            if not (line.startswith('[') and line.endswith(']')):
                continue
                
            # Remove brackets
            line = line[1:-1].strip()
            
            # Split by detecting column boundaries
            values = []
            current_value = ""
            quote_count = 0
            
            for char in line:
                if char == '"':
                    quote_count += 1
                elif char == ',' and quote_count % 2 == 0:
                    values.append(current_value.strip().strip('"'))
                    current_value = ""
                else:
                    current_value += char
            
            # Add the last value
            if current_value:
                values.append(current_value.strip().strip('"'))
            
            # Only keep rows with correct number of columns
            if len(values) == len(columns):
                rows.append(values)
            else:
                print(f"Skipping row with {len(values)} columns: {values}")
        
        if not rows:
            print("No valid rows were parsed from the generated data")
            print("Generated text:", data_text)
            return pd.DataFrame(columns=columns)
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=columns)
        
        # Clean the data
        df = df.apply(lambda x: x.str.strip() if isinstance(x, pd.Series) and x.dtype == "object" else x)
        df = df.replace('', pd.NA)
        
        return df
    except Exception as e:
        print(f"Error parsing generated data: {str(e)}")
        print("Data causing the error:", data_text)
        return pd.DataFrame(columns=columns)

def analyzer_agent(data_df):
    """Analyze the input data using the AI model"""
    try:
        # Get column information
        col_info = pd.DataFrame({
            'Column': data_df.columns,
            'Type': data_df.dtypes,
            'Non-Null': data_df.count(),
            'Unique': data_df.nunique()
        }).to_string()
        
        # Get sample data
        sample_data = data_df.head().to_string()
        
        # Create the analysis prompt
        analysis_prompt = f"""
        Please analyze this dataset and provide:
        1. The structure and format of the data
        2. The relationships between columns
        3. Any patterns or trends in the values
        4. Rules or constraints that should be maintained
        
        Column Information:
        {col_info}
        
        Sample Data:
        {sample_data}
        """
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a data analysis expert. Analyze the provided dataset and explain its structure, patterns, and important characteristics."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in analyzer agent: {str(e)}")
        return ""

def generator_agent(analysis_result, sample_df, num_rows=30, maintain_distributions=True):
    """Generate new data based on analysis"""
    try:
        # Get column information and constraints
        columns = sample_df.columns.tolist()
        col_info = pd.DataFrame({
            'Column': columns,
            'Type': sample_df.dtypes,
            'Non-Null': sample_df.count(),
            'Unique': sample_df.nunique(),
            'Sample_Values': [sample_df[col].dropna().sample(min(3, len(sample_df))).tolist() for col in columns]
        }).to_string()
        
        # Create the generation prompt
        generation_prompt = f"""
        Generate {num_rows} rows of data that match these specifications:

        Columns ({len(columns)}):
        {', '.join(columns)}

        Analysis Results:
        {analysis_result}

        Column Information:
        {col_info}

        Requirements:
        1. Generate EXACTLY {num_rows} rows
        2. Each row MUST have {len(columns)} values in the EXACT order of columns shown above
        3. Use semicolons or dashes instead of commas in descriptions
        4. {"Maintain similar value distributions as the original data" if maintain_distributions else "Create diverse but realistic values"}

        CRITICAL FORMAT INSTRUCTIONS:
        1. Output ONLY rows of data in this EXACT format, with values separated by commas:
           ["Title", "A description without commas", "Theme1; Theme2", "Genre", "Author"]
        2. One row per line
        3. NO explanatory text
        4. NO headers or footers
        5. ONLY the data rows in square brackets
        6. EXACTLY {len(columns)} values per row
        7. Use semicolons (;) or dashes (-) instead of commas within text values
        8. Each value should be in quotes

        Example of EXACT format needed:
        ["The Great Gatsby", "A story about the American Dream in the roaring twenties", "wealth; society; dreams", "Fiction", "F. Scott Fitzgerald"]
        ["1984", "A dystopian tale of surveillance and control", "totalitarianism; freedom; control", "Science Fiction", "George Orwell"]
        
        Begin generating {num_rows} rows now:
        """
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a data generation expert. Generate data that EXACTLY matches the specified format. Output ONLY the data rows in the specified format, no other text."},
                {"role": "user", "content": generation_prompt}
            ],
            temperature=0.8,
            max_tokens=4000
        )
        
        # Parse generated data into DataFrame
        generated_df = parse_generated_data(response.choices[0].message.content, columns)
        
        # Validate the generated data
        if len(generated_df.columns) != len(columns):
            print(f"Column count mismatch. Expected {len(columns)}, got {len(generated_df.columns)}")
            print("Expected columns:", columns)
            print("Generated columns:", generated_df.columns.tolist())
            return pd.DataFrame(columns=columns)
        
        # Ensure column order matches
        generated_df = generated_df[columns]
        
        # Clean the data
        generated_df = generated_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        generated_df = generated_df.replace('', pd.NA)
        
        return generated_df
    except Exception as e:
        print(f"Error in generator agent: {str(e)}")
        return pd.DataFrame(columns=columns)

def process_data(input_file, output_file, num_rows=30, maintain_distributions=True):
    """Main data processing workflow"""
    try:
        # Read input data
        input_df = read_data(input_file)
        if input_df.empty:
            return None, "Error reading input data"

        # Analyze data
        analysis_result = analyzer_agent(input_df)
        if not analysis_result:
            return None, "Error analyzing data"

        # Generate new data
        generated_df = generator_agent(
            analysis_result, 
            input_df, 
            num_rows,
            maintain_distributions
        )
        if generated_df.empty:
            return None, "Error generating data"

        # Save results
        if save_data(generated_df, output_file):
            return generated_df, analysis_result
        else:
            return None, "Error saving generated data"

    except Exception as e:
        return None, f"Error in data processing: {str(e)}"

# # Main execution flow

# # Get input from the user
# file_path = input("\nEnter the name of your CSV file: ")
# file_path = os.path.join("/home/elvin/DEVELOPMENT/agents/blackfriday-offers-v3", file_path) 
# desired_rows = int(input("Enter the number of rows you want in the new dataset: "))

# # Process data
# output_file = "new_dataset.csv"
# result_df, result_message = process_data(file_path, output_file, desired_rows)

# # Inform the user that the process is complete
# print(f"\n{result_message}")
# if result_df is not None:
#     print(f"Generated data has been saved to {output_file}")