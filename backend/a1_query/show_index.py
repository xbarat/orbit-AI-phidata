#!/usr/bin/env python3
from query_index import query_index
import argparse

def main():
    parser = argparse.ArgumentParser(description='Display F1 Query Index')
    parser.add_argument('--category', '-c', help='Filter by category (e.g., history, focus-basic)')
    parser.add_argument('--list-categories', '-l', action='store_true', help='List all available categories')
    
    args = parser.parse_args()
    
    if args.list_categories:
        categories = {data['category'] for data in query_index.queries.values()}
        print("\nAvailable Categories:")
        print("=" * 50)
        for category in sorted(categories):
            count = len(query_index.get_category_indices(category))
            print(f"{category}: {count} queries")
        return
        
    query_index.display_index(args.category)

if __name__ == "__main__":
    main() 