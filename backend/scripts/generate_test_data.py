import os
import json
import random
import datetime
from pathlib import Path

# Define the paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw_documents"
CASE_LAW_DIR = DATA_DIR / "case_law"
STATUTES_DIR = DATA_DIR / "statutes"

# Create the directories if they don't exist
CASE_LAW_DIR.mkdir(parents=True, exist_ok=True)
STATUTES_DIR.mkdir(parents=True, exist_ok=True)

# Sample data for case law
CASE_LAW_SAMPLES = [
    {
        "case_name": "Smith v. Jones",
        "citation": "123 F.3d 456",
        "jurisdiction": "Federal Circuit",
        "date": "2021-03-15",
        "text": """
        OPINION OF THE COURT
        
        The plaintiff, John Smith, alleges that defendant, Robert Jones, infringed on U.S. Patent No. 9,876,543 
        entitled "Method for Secure Electronic Transactions." The patent claims a method for processing electronic
        transactions using a novel encryption algorithm. Smith argues that Jones' product, SecurePay, implements 
        the same method and thus infringes on claims 1-5 of his patent.
        
        The District Court granted summary judgment in favor of Jones, finding that the claims of Smith's patent 
        were invalid under 35 U.S.C. § 101 as being directed to an abstract idea without adding significantly more.
        
        Upon review of the patent claims and the relevant case law, including Alice Corp. v. CLS Bank International,
        we find that the District Court correctly applied the two-step analysis. The claims are directed to the abstract
        idea of securing a transaction through encryption, and the implementation does not add significantly more to
        transform the abstract idea into patent-eligible subject matter.
        
        AFFIRMED.
        """
    },
    {
        "case_name": "Brown v. Educational Board",
        "citation": "456 U.S. 789",
        "jurisdiction": "Supreme Court",
        "date": "2022-06-28",
        "text": """
        MAJORITY OPINION
        
        This case presents the question of whether a state university's admissions policy that considers race as one
        factor among many in its holistic review process violates the Equal Protection Clause of the Fourteenth Amendment.
        
        Petitioner Lisa Brown, who was denied admission to State University, argues that the university's consideration 
        of race in admissions decisions violates her constitutional rights. The university contends that its limited use
        of race is narrowly tailored to achieve the compelling interest of educational diversity.
        
        After careful consideration of our precedents, including Grutter v. Bollinger and Fisher v. University of Texas,
        we conclude that the university's admissions program does not satisfy strict scrutiny. While educational diversity
        remains a compelling interest, the university has not shown that its use of race is narrowly tailored to achieve that
        interest. The university has not adequately demonstrated that race-neutral alternatives would be insufficient to
        achieve its diversity goals.
        
        REVERSED AND REMANDED.
        """
    },
    {
        "case_name": "Tech Innovations LLC v. MegaCorp Inc.",
        "citation": "789 F.Supp.2d 123",
        "jurisdiction": "S.D.N.Y.",
        "date": "2021-11-10",
        "text": """
        MEMORANDUM OPINION
        
        This trademark infringement action concerns the use of the mark "INNOVATE+" by defendant MegaCorp Inc.,
        which plaintiff Tech Innovations LLC alleges infringes on its registered trademark "INNOVATEPLUS." Both
        companies operate in the software development tools market.
        
        To prevail on a trademark infringement claim under the Lanham Act, a plaintiff must demonstrate that (1) it has
        a valid mark entitled to protection, and (2) the defendant's use of a similar mark is likely to cause confusion.
        
        Applying the Polaroid factors, the Court finds that there is a substantial likelihood of consumer confusion.
        The marks are visually and phonetically similar, the parties offer competing products in the same market to
        the same customers, and there is evidence of actual confusion in the marketplace.
        
        The defendant's motion for summary judgment is DENIED, and the plaintiff's motion for a preliminary injunction
        is GRANTED.
        """
    }
]

# Sample data for statutes
STATUTE_SAMPLES = [
    {
        "statute_name": "Intellectual Property Protection Act",
        "jurisdiction": "Federal",
        "effective_date": "2020-01-01",
        "sections": [
            {
                "section_number": "101",
                "title": "Definitions",
                "text": """
                As used in this Act:
                (1) "Intellectual property" means any patent, trademark, copyright, trade secret, or other proprietary information.
                (2) "Infringement" means the unauthorized use, reproduction, distribution, or display of intellectual property.
                (3) "Digital medium" means any electronic platform or technology used to store, transmit, or display content.
                """
            },
            {
                "section_number": "102",
                "title": "Digital Copyright Protections",
                "text": """
                (a) UNAUTHORIZED ACCESS.—Any person who willfully circumvents a technological measure that effectively
                controls access to a protected work shall be liable for civil penalties.
                
                (b) PENALTIES.—Any person who violates subsection (a) shall be subject to:
                  (1) Statutory damages of not less than $1,000 and not more than $25,000 per act of circumvention.
                  (2) Injunctive relief to prevent further violations.
                  (3) Reasonable attorney fees and costs to the prevailing party.
                """
            },
            {
                "section_number": "103",
                "title": "Fair Use Exception",
                "text": """
                Notwithstanding the provisions of section 102, it is not a violation of this Act to circumvent a technological
                measure for the purpose of:
                
                (a) Criticism, comment, news reporting, teaching, scholarship, or research;
                (b) Making a backup copy of legally acquired digital content for personal use;
                (c) Security testing of computer systems with authorization from the owner; or
                (d) Reverse engineering to achieve interoperability between computer programs.
                """
            }
        ]
    },
    {
        "statute_name": "Data Privacy Act",
        "jurisdiction": "Federal",
        "effective_date": "2021-05-15",
        "sections": [
            {
                "section_number": "201",
                "title": "Purpose and Scope",
                "text": """
                (a) PURPOSE.—The purpose of this Act is to protect the privacy of individuals with respect to the collection,
                use, and disclosure of personal information by businesses and government entities.
                
                (b) SCOPE.—This Act applies to any entity that:
                  (1) Is established or operates in the United States;
                  (2) Collects, processes, or stores personal information of U.S. residents; and
                  (3) Has annual gross revenues exceeding $5,000,000 or processes personal information of more than 50,000 individuals.
                """
            },
            {
                "section_number": "202",
                "title": "Consumer Rights",
                "text": """
                Consumers shall have the following rights with respect to their personal information:
                
                (a) RIGHT TO ACCESS.—The right to request and access their personal information collected by a covered entity.
                
                (b) RIGHT TO DELETE.—The right to request deletion of personal information collected from them, subject to exceptions
                for legitimate business purposes, legal obligations, or security purposes.
                
                (c) RIGHT TO CORRECT.—The right to request correction of inaccurate personal information.
                
                (d) RIGHT TO DATA PORTABILITY.—The right to obtain their personal information in a structured, commonly used,
                and machine-readable format.
                """
            },
            {
                "section_number": "203",
                "title": "Business Obligations",
                "text": """
                (a) PRIVACY NOTICE.—Each covered entity shall provide a privacy notice that includes:
                  (1) Categories of personal information collected;
                  (2) Purposes for which personal information is used;
                  (3) Categories of third parties with whom personal information is shared; and
                  (4) How consumers can exercise their rights under section 202.
                
                (b) DATA SECURITY.—Each covered entity shall implement reasonable security procedures and practices appropriate to
                the nature of the personal information to protect it from unauthorized access, destruction, use, modification, or disclosure.
                """
            }
        ]
    }
]

def generate_test_case_law():
    """Generate test case law documents"""
    print("Generating test case law documents...")
    
    for i, case in enumerate(CASE_LAW_SAMPLES):
        # Create a unique filename
        filename = f"{case['citation'].replace(' ', '_')}.json"
        file_path = CASE_LAW_DIR / filename
        
        # Write the case to file
        with open(file_path, 'w') as f:
            json.dump(case, f, indent=2)
            
        print(f"Created case law document: {filename}")
    
    # Also create some plain text versions for testing
    for i, case in enumerate(CASE_LAW_SAMPLES):
        # Create a unique filename
        filename = f"[{case['citation']}] {case['case_name']}.txt"
        file_path = CASE_LAW_DIR / filename
        
        # Write the case to file
        with open(file_path, 'w') as f:
            f.write(f"Case: {case['case_name']}\n")
            f.write(f"Citation: {case['citation']}\n")
            f.write(f"Jurisdiction: {case['jurisdiction']}\n")
            f.write(f"Date: {case['date']}\n\n")
            f.write(case['text'])
            
        print(f"Created case law text document: {filename}")

def generate_test_statutes():
    """Generate test statute documents"""
    print("Generating test statute documents...")
    
    for i, statute in enumerate(STATUTE_SAMPLES):
        # Create a unique filename
        filename = f"{statute['statute_name'].replace(' ', '_')}.json"
        file_path = STATUTES_DIR / filename
        
        # Write the statute to file
        with open(file_path, 'w') as f:
            json.dump(statute, f, indent=2)
            
        print(f"Created statute document: {filename}")
    
    # Also create CSV versions for testing
    for i, statute in enumerate(STATUTE_SAMPLES):
        # Create a unique filename
        filename = f"{statute['statute_name'].replace(' ', '_')}.csv"
        file_path = STATUTES_DIR / filename
        
        # Write header and rows to CSV
        with open(file_path, 'w') as f:
            f.write("section_number,title,text\n")
            for section in statute['sections']:
                # Clean up text for CSV
                text = section['text'].replace('\n', ' ').replace('"', '""')
                f.write(f"{section['section_number']},\"{section['title']}\",\"{text}\"\n")
            
        print(f"Created statute CSV document: {filename}")

if __name__ == "__main__":
    print("Generating test data for legal vector databases...")
    generate_test_case_law()
    generate_test_statutes()
    print("Test data generation complete.") 