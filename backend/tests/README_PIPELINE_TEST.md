# End-to-End Pipeline Test Script

This script tests the complete legal research pipeline from user query to final response, connecting all components:

1. **Client Understanding** (Model A) - Analyzes and understands the client's query
2. **Legal Research** (Model B) - Conducts comprehensive legal research using vector search and internet search
3. **Final Response Generation** - Combines understanding and research to generate a client-friendly response

## Prerequisites

Before running the test script, ensure you have:

1. All required API keys in your `.env` file:
   - `COHERE_API_KEY` (required)
   - `SERPAPI_KEY` (required)

2. Python dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script with a test query:

```bash
# Basic usage
python tests/test_pipeline.py --query "What are my rights as a tenant in New York?"

# Save output to a specific file
python tests/test_pipeline.py --query "What are the tax brackets for 2023?" --output results.json

# Display verbose output with more details
python tests/test_pipeline.py --query "Is a verbal contract legally binding?" --verbose

# Specify a custom log file
python tests/test_pipeline.py --query "What are my parental leave rights?" --log custom_log.txt
```

## Output

The script produces:

1. **Console output** with a summary of the pipeline execution
2. **JSON output file** with detailed results from each stage of the pipeline
3. **Log file** with timestamped entries for debugging

## Example

```bash
python tests/test_pipeline.py --query "What are my rights as a tenant in New York?" --verbose
```

This will:
1. Process the query through the client understanding agent
2. Conduct legal research using vector database and internet sources
3. Generate a final client-friendly response
4. Display a summary of the results
5. Save detailed output to a JSON file
6. Save a log file with timestamps

## Troubleshooting

If you encounter errors:

1. **API Key Issues**: Ensure all required API keys are properly set in your `.env` file
2. **Import Errors**: Make sure you're running from the correct directory (backend/)
3. **Connection Errors**: Check your internet connection for web search functionality
4. **Service Errors**: Review the log file for detailed error messages

## Extending the Script

The script can be extended to include:

- Additional verification steps
- Multiple query testing
- Performance benchmarking
- Integration with the web interface 