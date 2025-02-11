import streamlit as st
import sys
import os
import pandas as pd
from pathlib import Path

# Add the backend directory to the path so we can import from it
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_dir))

from processor import process_query

def main():
    st.set_page_config(
        page_title="F1 Data Query Pipeline",
        page_icon="🏎️",
        layout="wide"
    )

    st.title("🏎️ F1 Data Query Pipeline")
    st.markdown("""
    Ask questions about Formula 1 data in natural language. For example:
    - "Show me Lewis Hamilton's race results from 2023"
    - "Compare Max Verstappen and Sergio Perez's performance in 2023"
    - "Get the qualifying results for the 2023 Monaco Grand Prix"
    """)

    # Query input
    query = st.text_input("Enter your query:", placeholder="e.g., Show me Lewis Hamilton's race results from 2023")

    if st.button("Submit Query"):
        if query:
            with st.spinner("Processing query..."):
                try:
                    results = process_query(query)
                    
                    # Display results
                    if isinstance(results, list):
                        for i, result in enumerate(results, 1):
                            if isinstance(result, pd.DataFrame) and not result.empty:
                                st.subheader(f"Result {i}")
                                st.dataframe(result, use_container_width=True)
                    else:
                        st.error("No results found")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a query")

    # Add a sidebar with information
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This application provides a natural language interface for querying Formula 1 race data using the Ergast API.
        
        **Features:**
        - Natural language query processing
        - Race results
        - Driver standings
        - Qualifying results
        - Lap times and status
        """)

if __name__ == "__main__":
    main() 