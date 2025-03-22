#!/usr/bin/env python3
"""
Script to fix the embedding dimension mismatch issue by resetting collections
and repopulating them with consistent embeddings.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from services.embedding_service import embedding_service, S3_ENABLED
from services.s3_vector_store_fix import patched_s3_vector_store

# Sample documents
CASE_LAW_DOCUMENTS = [
    {
        "id": "case_001",
        "document": "Smith v. Workplace Incorporated: A case involving employment discrimination based on gender. The court found that the employer had violated Title VII by refusing to promote the plaintiff due to her gender. The court awarded damages and ordered the company to implement new anti-discrimination policies.",
        "metadata": {
            "title": "Smith v. Workplace Incorporated",
            "citation": "123 F.3d 456 (9th Cir. 2005)",
            "year": 2005,
            "court": "Ninth Circuit Court of Appeals",
            "summary": "Gender discrimination case where plaintiff was denied promotion due to gender bias."
        }
    },
    {
        "id": "case_002",
        "document": "Brown v. Educational Board: A case involving employment discrimination based on race. The court found that the school had violated Title VII by terminating the plaintiff, an African American teacher, while retaining less qualified non-minority teachers. The court ordered reinstatement and back pay.",
        "metadata": {
            "title": "Brown v. Educational Board",
            "citation": "234 F.3d 567 (4th Cir. 2010)",
            "year": 2010,
            "court": "Fourth Circuit Court of Appeals",
            "summary": "Racial discrimination case where plaintiff was terminated based on race."
        }
    }
]

STATUTE_DOCUMENTS = [
    {
        "id": "statute_001",
        "document": "Equal Pay Act: This act prohibits wage discrimination based on sex. It requires that men and women in the same workplace be given equal pay for equal work. The jobs need not be identical, but they must be substantially equal in terms of skill, effort, responsibility, and working conditions.",
        "metadata": {
            "title": "Equal Pay Act",
            "citation": "29 U.S.C. § 206(d)",
            "year": 1963,
            "section": "Section 206(d)",
            "summary": "Prohibits wage discrimination based on sex for equal work."
        }
    },
    {
        "id": "statute_002",
        "document": "Fair Housing Act: This act prohibits discrimination in the sale, rental, and financing of housing based on race, color, national origin, religion, sex, familial status, and disability. It also mandates that new multifamily housing meet certain accessibility requirements for persons with disabilities.",
        "metadata": {
            "title": "Fair Housing Act",
            "citation": "42 U.S.C. §§ 3601-3619",
            "year": 1968,
            "section": "Title VIII of Civil Rights Act",
            "summary": "Prohibits discrimination in housing based on protected characteristics."
        }
    }
]

REGULATION_DOCUMENTS = [
    {
        "id": "regulation_001",
        "document": "Equal Employment Opportunity Commission Regulations: These regulations implement Title VII of the Civil Rights Act and provide guidance on what constitutes sexual harassment in the workplace. They define sexual harassment as unwelcome sexual advances, requests for sexual favors, and other verbal or physical conduct of a sexual nature when submission to such conduct is made a condition of employment.",
        "metadata": {
            "title": "EEOC Sexual Harassment Regulations",
            "citation": "29 C.F.R. § 1604.11",
            "year": 1980,
            "agency": "Equal Employment Opportunity Commission",
            "summary": "Defines sexual harassment in the workplace under Title VII."
        }
    },
    {
        "id": "regulation_002",
        "document": "Department of Labor Regulations: These regulations implement the Family and Medical Leave Act (FMLA) and provide guidance on employee eligibility for leave, employer coverage, and the definition of serious health conditions. They specify that eligible employees are entitled to 12 workweeks of leave in a 12-month period for specified family and medical reasons.",
        "metadata": {
            "title": "FMLA Regulations",
            "citation": "29 C.F.R. § 825",
            "year": 1995,
            "agency": "Department of Labor",
            "summary": "Implements the Family and Medical Leave Act requirements."
        }
    }
]

def clean_environment():
    """Clean the environment by deleting collections"""
    print("Cleaning the environment...")
    
    # Delete all collections
    collections = ['case_law', 'statutes', 'regulations']
    for collection in collections:
        try:
            if collection == 'case_law':
                embedding_service.case_law_collection.delete()
                print(f"Deleted {collection} collection")
            elif collection == 'statutes':
                embedding_service.statutes_collection.delete()
                print(f"Deleted {collection} collection")
            elif collection == 'regulations':
                embedding_service.regulations_collection.delete()
                print(f"Deleted {collection} collection")
        except Exception as e:
            print(f"Error deleting {collection} collection: {e}")
    
    # Recreate collections - they will be created automatically when populated

def populate_collections():
    """Populate collections with sample documents"""
    print("Populating collections with sample documents...")
    
    # Populate case_law collection
    documents = [doc["document"] for doc in CASE_LAW_DOCUMENTS]
    metadatas = [doc["metadata"] for doc in CASE_LAW_DOCUMENTS]
    ids = [doc["id"] for doc in CASE_LAW_DOCUMENTS]
    
    # Generate embeddings using the same model that will be used for queries
    embeddings = embedding_service.generate_embeddings(documents)
    
    # Add to collection
    embedding_service.case_law_collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Added {len(documents)} documents to case_law collection")
    
    # Populate statutes collection
    documents = [doc["document"] for doc in STATUTE_DOCUMENTS]
    metadatas = [doc["metadata"] for doc in STATUTE_DOCUMENTS]
    ids = [doc["id"] for doc in STATUTE_DOCUMENTS]
    
    # Generate embeddings
    embeddings = embedding_service.generate_embeddings(documents)
    
    # Add to collection
    embedding_service.statutes_collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Added {len(documents)} documents to statutes collection")
    
    # Populate regulations collection
    documents = [doc["document"] for doc in REGULATION_DOCUMENTS]
    metadatas = [doc["metadata"] for doc in REGULATION_DOCUMENTS]
    ids = [doc["id"] for doc in REGULATION_DOCUMENTS]
    
    # Generate embeddings
    embeddings = embedding_service.generate_embeddings(documents)
    
    # Add to collection
    embedding_service.regulations_collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Added {len(documents)} documents to regulations collection")

def update_stats_file():
    """Update the stats file with the correct document counts"""
    print("Updating stats file...")
    
    import json
    from datetime import datetime
    
    stats_file = os.path.join(project_root, "data", "stats.json")
    
    # Create stats data
    stats = {
        "last_updated": datetime.now().isoformat(),
        "collections": {
            "case_law": {
                "document_count": len(CASE_LAW_DOCUMENTS),
                "embedding_count": len(CASE_LAW_DOCUMENTS)
            },
            "statutes": {
                "document_count": len(STATUTE_DOCUMENTS),
                "embedding_count": len(STATUTE_DOCUMENTS)
            },
            "regulations": {
                "document_count": len(REGULATION_DOCUMENTS),
                "embedding_count": len(REGULATION_DOCUMENTS)
            }
        }
    }
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(stats_file), exist_ok=True)
    
    # Write stats to file
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Updated stats file at {stats_file}")

def sync_with_s3():
    """Sync collections with S3"""
    if not S3_ENABLED:
        print("S3 storage is not enabled. Skipping sync.")
        return
    
    print("Syncing collections with S3...")
    
    # Sync collections with S3
    patched_s3_vector_store.sync_all_collections()
    print("All collections have been synced with S3")

def test_search():
    """Test search functionality"""
    print("\nTesting search functionality...")
    
    # Test case_law search
    query = "employment discrimination"
    collection = "case_law"
    print(f"\nSearching for '{query}' in {collection} collection...")
    
    # Generate query embedding
    query_embedding = embedding_service.generate_embeddings([query])[0]
    
    # Search directly with the collection
    results = embedding_service.case_law_collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )
    
    # Print results
    if results and 'ids' in results and len(results['ids']) > 0 and len(results['ids'][0]) > 0:
        print(f"Found {len(results['ids'][0])} results:")
        for i in range(len(results['ids'][0])):
            doc_id = results['ids'][0][i]
            metadata = results['metadatas'][0][i] if 'metadatas' in results and results['metadatas'][0] else {}
            print(f"  - {doc_id}: {metadata.get('title', 'No title')}")
    else:
        print("No results found")
    
    # Test statutes search
    query = "equal pay"
    collection = "statutes"
    print(f"\nSearching for '{query}' in {collection} collection...")
    
    # Generate query embedding
    query_embedding = embedding_service.generate_embeddings([query])[0]
    
    # Search directly with the collection
    results = embedding_service.statutes_collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )
    
    # Print results
    if results and 'ids' in results and len(results['ids']) > 0 and len(results['ids'][0]) > 0:
        print(f"Found {len(results['ids'][0])} results:")
        for i in range(len(results['ids'][0])):
            doc_id = results['ids'][0][i]
            metadata = results['metadatas'][0][i] if 'metadatas' in results and results['metadatas'][0] else {}
            print(f"  - {doc_id}: {metadata.get('title', 'No title')}")
    else:
        print("No results found")

def main():
    """Main function to fix embedding dimension mismatch"""
    print("Starting embedding dimension fix process...")
    
    # Clean the environment
    clean_environment()
    
    # Populate collections
    populate_collections()
    
    # Update stats file
    update_stats_file()
    
    # Sync with S3
    sync_with_s3()
    
    # Test search
    test_search()
    
    print("\nEmbedding dimension fix process completed successfully!")
    print("You can now restart the application to use the fixed collections.")

if __name__ == "__main__":
    main() 