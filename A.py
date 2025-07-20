# main.py
import io
import pdfplumber
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Initialize the FastAPI app
app = FastAPI(
    title="FinSight Invoice Analyzer",
    description="An API to analyze PDF invoices and calculate spending.",
    version="1.0.0"
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows the API to be called from any web page.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.post("/analyze")
async def analyze_invoice(file: UploadFile = File(...)):
    """
    This endpoint accepts a PDF invoice, extracts tables, and calculates the
    sum of the 'Total' column for all rows where the 'Product' is 'Thingamajig'.

    Args:
        file (UploadFile): The PDF file uploaded by the user.

    Returns:
        dict: A JSON object with the calculated sum, e.g., {"sum": 358}.
    """
    total_sum = 0
    
    try:
        # Read the uploaded file into a byte stream
        pdf_content = await file.read()
        
        # Use a context manager to open the PDF from the byte stream
        with io.BytesIO(pdf_content) as pdf_stream:
            with pdfplumber.open(pdf_stream) as pdf:
                # Iterate over each page in the PDF
                for page in pdf.pages:
                    # Extract tables from the current page
                    tables = page.extract_tables()
                    for table in tables:
                        # Assuming the first row is the header
                        header = [h.replace('\n', ' ') for h in table[0]]
                        
                        # Find the indices for 'Product' and 'Total' columns
                        try:
                            product_idx = header.index("Product")
                            total_idx = header.index("Total")
                        except ValueError:
                            # If columns are not found, skip this table
                            continue

                        # Iterate over the data rows (skipping the header)
                        for row in table[1:]:
                            product_name = row[product_idx]
                            
                            # Check if the product is 'Thingamajig'
                            if product_name and 'Thingamajig' in product_name:
                                try:
                                    # Get the total value and convert it to a number
                                    total_value_str = row[total_idx]
                                    if total_value_str:
                                        total_sum += float(total_value_str)
                                except (ValueError, TypeError):
                                    # Handle cases where conversion fails
                                    continue
                                    
    except Exception as e:
        # Handle potential errors during file processing
        return {"error": f"Failed to process PDF: {str(e)}"}

    # Return the final sum in the required JSON format
    return {"sum": total_sum}

# To run this FastAPI application:
# 1. Make sure you have FastAPI, uvicorn, and pdfplumber installed:
#    pip install "fastapi[all]" pdfplumber
#
# 2. Save this code as a Python file (e.g., main.py).
#
# 3. Run the server from your terminal:
#    uvicorn main:app --reload
#
# 4. The API will be available at http://127.0.0.1:8000
#
# 5. You can access the interactive API documentation at http://127.0.0.1:8000/docs

if __name__ == "__main__":
    # This block allows running the app directly with Python
    # It's useful for development but for production, it's better
    # to use a process manager like Gunicorn with uvicorn workers.
    uvicorn.run(app, host="0.0.0.0", port=8000)

