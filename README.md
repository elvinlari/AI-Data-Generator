# AI Data Generator

A versatile AI-powered tool that generates structured data from any CSV input. Perfect for creating test data, augmenting datasets, or generating synthetic data while maintaining the original data's patterns and relationships.

## 🚀 Key Features

- Universal CSV input support
- AI-powered data analysis and generation
- Distribution pattern maintenance
- Multiple export formats (CSV/Excel)
- Interactive web interface

## 🛠️ Quick Start

1. **Setup Environment**
```bash
# Clone and setup
git clone <repository-url>
cd ai-data-generator
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

2. **Configure API**
```bash
# Create .env file with your API key
echo "PERPLEXITY_API_KEY=your_api_key_here" > .env
```

3. **Run Application**
```bash
streamlit run app.py
```

## 💻 Usage

1. **Upload Data**
   - Click 'Upload CSV' button
   - Select any structured CSV file
   - Preview data automatically

2. **Configure Generation**
   - Set number of rows
   - Toggle distribution maintenance
   - Choose export format

3. **Generate & Download**
   - Click 'Generate Data'
   - Preview results
   - Download in preferred format

## 📊 Interface

### Data Upload
![Upload](images/upload.png)
*Upload and preview your data*

### Analysis View
![Analysis](images/analysis.png)
*Analyze patterns and distributions*

### Generation Options
![Options](images/options.png)
*Configure generation settings*

### Results
![Results](images/results.png)
*View and download generated data*

## 📋 Requirements

- Python 3.8+
- Internet connection for API access
- CSV input file
- Dependencies listed in requirements.txt

## 🔧 Project Structure

```
ai-data-generator/
├── app.py           # Web interface
├── agents.py        # Core logic
├── .env            # API configuration
├── requirements.txt # Dependencies
└── README.md       # Documentation
```

## 🚨 Common Issues

1. **API Errors**
   ```
   Solution: Check API key in .env
   ```

2. **CSV Format**
   ```
   Solution: Ensure consistent headers and data types
   ```

3. **Generation Issues**
   ```
   Solution: Try smaller batch sizes or check memory
   ```

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## 📫 Support

Open an issue for bugs or feature requests.
