#!/usr/bin/env python3
"""
Script to directly add documents to ChromaDB collections and sync with S3.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.embedding_service import embedding_service

# Sample documents for testing
CASE_LAW_DOCUMENTS = [
    {
        "id": "case_001",
        "document": """
CASE: Brown v. Educational Board
CITATION: 456 U.S. 789

MAJORITY OPINION

The Court holds that the state university's admissions program, which considers race as one factor in admissions decisions to further a compelling interest in obtaining the educational benefits that flow from a diverse student body, does not satisfy strict scrutiny because its implementation is not narrowly tailored to achieve this goal.

The Court emphasizes that any use of race in admissions must be narrowly tailored and subject to strict scrutiny. The Court finds that while diversity can constitute a compelling state interest, the university's program fails to employ race-neutral alternatives effectively.

The Court notes that quotas and racial balancing are unconstitutional, and that universities must demonstrate good faith consideration of race-neutral alternatives.
""",
        "metadata": {
            "title": "Brown v. Educational Board",
            "citation": "456 U.S. 789",
            "type": "case_law",
            "source": "test_data"
        }
    },
    {
        "id": "case_002",
        "document": """
CASE: Smith v. Workplace Incorporated
CITATION: 342 F.3d 698

MAJORITY OPINION

This case presents an important question of employment discrimination law: whether a plaintiff can establish a prima facie case of gender discrimination solely with evidence of pay disparity between similarly situated employees of different genders.

The Court holds that while pay disparity is relevant evidence, it is not by itself sufficient to establish a prima facie case. The plaintiff must also demonstrate that the employer's explanation for the disparity is pretextual.

The Court notes that statistical evidence may be compelling when showing systematic discrimination across a workforce, but individualized assessment is required for specific claims.

The plaintiff in this case has shown both pay disparity and evidence suggesting the employer's justification was pretextual, and therefore has established a prima facie case that should proceed to trial.
""",
        "metadata": {
            "title": "Smith v. Workplace Incorporated",
            "citation": "342 F.3d 698",
            "type": "case_law",
            "source": "test_data"
        }
    }
]

STATUTE_DOCUMENTS = [
    {
        "id": "statute_001",
        "document": """
TITLE: Equal Pay Act
Section 1: Prohibition of Pay Discrimination

No employer shall discriminate between employees on the basis of sex by paying wages to employees at a rate less than the rate paid to employees of the opposite sex for equal work on jobs requiring equal skill, effort, and responsibility, and which are performed under similar working conditions.

Exceptions may be made where payment is made pursuant to: (i) a seniority system; (ii) a merit system; (iii) a system which measures earnings by quantity or quality of production; or (iv) a differential based on any factor other than sex.

Any employer who violates the provisions of this section shall be liable to the employee or employees affected in the amount of their unpaid wages, and in an additional equal amount as liquidated damages.
""",
        "metadata": {
            "title": "Equal Pay Act",
            "section": "Section 1",
            "type": "statute",
            "source": "test_data"
        }
    },
    {
        "id": "statute_002",
        "document": """
TITLE: Fair Housing Act
Section 3: Prohibited Discrimination

It shall be unlawful to refuse to sell or rent after the making of a bona fide offer, or to refuse to negotiate for the sale or rental of, or otherwise make unavailable or deny, a dwelling to any person because of race, color, religion, sex, familial status, or national origin.

It shall be unlawful to discriminate against any person in the terms, conditions, or privileges of sale or rental of a dwelling, or in the provision of services or facilities in connection therewith, because of race, color, religion, sex, familial status, or national origin.

This section also prohibits: (a) making, printing, or publishing any notice, statement, or advertisement with respect to the sale or rental of a dwelling that indicates any preference, limitation, or discrimination; (b) representing that any dwelling is not available for inspection, sale, or rental when such dwelling is in fact available; and (c) inducing or attempting to induce, for profit, any person to sell or rent any dwelling by representations regarding the entry or prospective entry of persons of a particular race, color, religion, sex, familial status, or national origin.
""",
        "metadata": {
            "title": "Fair Housing Act",
            "section": "Section 3",
            "type": "statute",
            "source": "test_data"
        }
    }
]

REGULATION_DOCUMENTS = [
    {
        "id": "regulation_001",
        "document": """
TITLE: Equal Employment Opportunity Commission Regulations
SECTION: 29 CFR § 1604.11 - Sexual harassment

(a) Harassment on the basis of sex is a violation of section 703 of title VII. Unwelcome sexual advances, requests for sexual favors, and other verbal or physical conduct of a sexual nature constitute sexual harassment when:
(1) submission to such conduct is made either explicitly or implicitly a term or condition of an individual's employment,
(2) submission to or rejection of such conduct by an individual is used as the basis for employment decisions affecting such individual, or
(3) such conduct has the purpose or effect of unreasonably interfering with an individual's work performance or creating an intimidating, hostile, or offensive working environment.

(b) In determining whether alleged conduct constitutes sexual harassment, the Commission will look at the record as a whole and at the totality of the circumstances, such as the nature of the sexual advances and the context in which the alleged incidents occurred. The determination of the legality of a particular action will be made from the facts, on a case by case basis.

(c) Applying general title VII principles, an employer, employment agency, joint apprenticeship committee or labor organization (hereinafter collectively referred to as "employer") is responsible for its acts and those of its agents and supervisory employees with respect to sexual harassment regardless of whether the specific acts complained of were authorized or even forbidden by the employer and regardless of whether the employer knew or should have known of their occurrence.
""",
        "metadata": {
            "title": "EEOC Regulations",
            "section": "29 CFR § 1604.11",
            "type": "regulation",
            "source": "test_data"
        }
    },
    {
        "id": "regulation_002",
        "document": """
TITLE: Department of Labor Regulations
SECTION: 29 CFR § 1620.13 - Equal Pay for Equal Work

(a) In general. The equal pay provisions apply to any employer who pays different wages to employees of opposite sexes for equal work on jobs requiring equal skill, effort, and responsibility, and which are performed under similar working conditions in the same establishment. The employer against whom a charge is lodged or a suit brought has the burden of proving that a factor other than sex is the basis for the wage differential.

(b) "Establishment." The prohibition against compensation discrimination under the equal pay provisions applies only to wage differentials as between employees in the same establishment. An "establishment" is a distinct physical place of business rather than an entire business or "enterprise" which may include several separate places of business. Accordingly, each physical location is a separate establishment.

(c) Application to jobs. The equal pay provisions of the Act apply to jobs requiring equal skill, effort, and responsibility, and which are performed under similar working conditions within the same establishment. Where these factors are the same, the Act requires that men and women performing equal work must receive the same rate of pay. The job content, not the job title or classification, determines the equality of jobs. Application of the equal pay standard is not dependent on job classifications or titles but depends rather on actual job requirements and performance.
""",
        "metadata": {
            "title": "Department of Labor Regulations",
            "section": "29 CFR § 1620.13",
            "type": "regulation",
            "source": "test_data"
        }
    }
]

def populate_case_law():
    """Add sample case law documents to the vector database"""
    print("Adding case law documents...")
    
    collection = embedding_service.case_law_collection
    
    # Get existing IDs to avoid duplicates
    try:
        existing = collection.get()
        existing_ids = set(existing["ids"])
    except Exception:
        existing_ids = set()
    
    # Add documents
    docs_to_add = []
    ids_to_add = []
    metadatas_to_add = []
    
    for doc in CASE_LAW_DOCUMENTS:
        if doc["id"] not in existing_ids:
            docs_to_add.append(doc["document"])
            ids_to_add.append(doc["id"])
            metadatas_to_add.append(doc["metadata"])
    
    if docs_to_add:
        collection.add(
            documents=docs_to_add,
            ids=ids_to_add,
            metadatas=metadatas_to_add
        )
        print(f"Added {len(docs_to_add)} case law documents")
    else:
        print("No new case law documents to add")
    
    # Save to S3
    if hasattr(embedding_service, '_save_collection_to_s3'):
        embedding_service._save_collection_to_s3('case_law')
        print("Saved case law collection to S3")

def populate_statutes():
    """Add sample statute documents to the vector database"""
    print("Adding statute documents...")
    
    collection = embedding_service.statutes_collection
    
    # Get existing IDs to avoid duplicates
    try:
        existing = collection.get()
        existing_ids = set(existing["ids"])
    except Exception:
        existing_ids = set()
    
    # Add documents
    docs_to_add = []
    ids_to_add = []
    metadatas_to_add = []
    
    for doc in STATUTE_DOCUMENTS:
        if doc["id"] not in existing_ids:
            docs_to_add.append(doc["document"])
            ids_to_add.append(doc["id"])
            metadatas_to_add.append(doc["metadata"])
    
    if docs_to_add:
        collection.add(
            documents=docs_to_add,
            ids=ids_to_add,
            metadatas=metadatas_to_add
        )
        print(f"Added {len(docs_to_add)} statute documents")
    else:
        print("No new statute documents to add")
    
    # Save to S3
    if hasattr(embedding_service, '_save_collection_to_s3'):
        embedding_service._save_collection_to_s3('statutes')
        print("Saved statutes collection to S3")

def populate_regulations():
    """Add sample regulation documents to the vector database"""
    print("Adding regulation documents...")
    
    collection = embedding_service.regulations_collection
    
    # Get existing IDs to avoid duplicates
    try:
        existing = collection.get()
        existing_ids = set(existing["ids"])
    except Exception:
        existing_ids = set()
    
    # Add documents
    docs_to_add = []
    ids_to_add = []
    metadatas_to_add = []
    
    for doc in REGULATION_DOCUMENTS:
        if doc["id"] not in existing_ids:
            docs_to_add.append(doc["document"])
            ids_to_add.append(doc["id"])
            metadatas_to_add.append(doc["metadata"])
    
    if docs_to_add:
        collection.add(
            documents=docs_to_add,
            ids=ids_to_add,
            metadatas=metadatas_to_add
        )
        print(f"Added {len(docs_to_add)} regulation documents")
    else:
        print("No new regulation documents to add")
    
    # Save to S3
    if hasattr(embedding_service, '_save_collection_to_s3'):
        embedding_service._save_collection_to_s3('regulations')
        print("Saved regulations collection to S3")

def check_collections():
    """Check the contents of all collections"""
    print("\nChecking collection contents:")
    
    # Case Law
    try:
        case_law = embedding_service.case_law_collection.get()
        print(f"Case Law: {len(case_law['ids'])} documents")
        if case_law['ids']:
            print(f"  Sample IDs: {case_law['ids'][:3]}")
    except Exception as e:
        print(f"Error getting case law collection: {e}")
    
    # Statutes
    try:
        statutes = embedding_service.statutes_collection.get()
        print(f"Statutes: {len(statutes['ids'])} documents")
        if statutes['ids']:
            print(f"  Sample IDs: {statutes['ids'][:3]}")
    except Exception as e:
        print(f"Error getting statutes collection: {e}")
    
    # Regulations
    try:
        regulations = embedding_service.regulations_collection.get()
        print(f"Regulations: {len(regulations['ids'])} documents")
        if regulations['ids']:
            print(f"  Sample IDs: {regulations['ids'][:3]}")
    except Exception as e:
        print(f"Error getting regulations collection: {e}")

def sync_with_s3():
    """Force sync all collections with S3"""
    print("\nSyncing collections with S3...")
    
    collections = ["case_law", "statutes", "regulations"]
    for collection_name in collections:
        if hasattr(embedding_service, '_save_collection_to_s3'):
            embedding_service._save_collection_to_s3(collection_name)
            print(f"Synced {collection_name} collection to S3")
        else:
            print(f"Warning: Embedding service doesn't have _save_collection_to_s3 method")
            break

def main():
    """Main entry point"""
    print("Populating vector database with sample documents...")
    
    populate_case_law()
    populate_statutes()
    populate_regulations()
    
    check_collections()
    sync_with_s3()
    
    print("\nDone! The vector database has been populated with sample documents.")
    print("You can now test the vector search functionality with queries like:")
    print('  curl -X POST http://localhost:5001/api/search -H "Content-Type: application/json" -d \'{"query": "gender discrimination in employment", "collection": "case_law", "top_k": 2}\'')

if __name__ == "__main__":
    main() 