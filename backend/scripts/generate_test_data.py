#!/usr/bin/env python3
"""
Script to generate sample legal documents for testing the ingestion pipeline.
"""

import os
import json
import argparse
import random
from pathlib import Path

# Sample data
CASE_LAW_SAMPLES = [
    {
        "title": "Brown v. Educational Board",
        "citation": "456 U.S. 789",
        "content": """
MAJORITY OPINION

The Court holds that the state university's admissions program, which considers race as one factor in admissions decisions to further a compelling interest in obtaining the educational benefits that flow from a diverse student body, does not satisfy strict scrutiny because its implementation is not narrowly tailored to achieve this goal.

The Court emphasizes that any use of race in admissions must be narrowly tailored and subject to strict scrutiny. The Court finds that while diversity can constitute a compelling state interest, the university's program fails to employ race-neutral alternatives effectively.

The Court notes that quotas and racial balancing are unconstitutional, and that universities must demonstrate good faith consideration of race-neutral alternatives.
"""
    },
    {
        "title": "Smith v. Workplace Incorporated",
        "citation": "342 F.3d 698",
        "content": """
MAJORITY OPINION

This case presents an important question of employment discrimination law: whether a plaintiff can establish a prima facie case of gender discrimination solely with evidence of pay disparity between similarly situated employees of different genders.

The Court holds that while pay disparity is relevant evidence, it is not by itself sufficient to establish a prima facie case. The plaintiff must also demonstrate that the employer's explanation for the disparity is pretextual.

The Court notes that statistical evidence may be compelling when showing systematic discrimination across a workforce, but individualized assessment is required for specific claims.

The plaintiff in this case has shown both pay disparity and evidence suggesting the employer's justification was pretextual, and therefore has established a prima facie case that should proceed to trial.
"""
    },
    {
        "title": "Harris v. City of Metro",
        "citation": "567 F.2d 123",
        "content": """
MAJORITY OPINION

This case concerns allegations of discrimination in municipal hiring practices. The plaintiff alleges that the city's standardized testing requirement for firefighter positions has a disparate impact on minority applicants and is not job-related.

The Court applies the disparate impact framework established in Griggs v. Duke Power Co. Under this framework, once a plaintiff demonstrates that a facially neutral employment practice has a disparate impact on a protected group, the burden shifts to the employer to demonstrate that the practice is job-related and consistent with business necessity.

The evidence in this case establishes that the standardized test has a statistically significant disparate impact on minority applicants. The city has failed to demonstrate that the test accurately predicts job performance or is necessary for safe and efficient operations.

The Court therefore holds that the city's testing requirement violates Title VII of the Civil Rights Act and orders the city to develop alternative selection procedures that both serve legitimate business needs and minimize adverse impact on protected groups.
"""
    }
]

STATUTE_SAMPLES = [
    {
        "title": "Equal Pay Act",
        "section": "Section 1: Prohibition of Pay Discrimination",
        "content": """
No employer shall discriminate between employees on the basis of sex by paying wages to employees at a rate less than the rate paid to employees of the opposite sex for equal work on jobs requiring equal skill, effort, and responsibility, and which are performed under similar working conditions.

Exceptions may be made where payment is made pursuant to: (i) a seniority system; (ii) a merit system; (iii) a system which measures earnings by quantity or quality of production; or (iv) a differential based on any factor other than sex.

Any employer who violates the provisions of this section shall be liable to the employee or employees affected in the amount of their unpaid wages, and in an additional equal amount as liquidated damages.
"""
    },
    {
        "title": "Fair Housing Act",
        "section": "Section 3: Prohibited Discrimination",
        "content": """
It shall be unlawful to refuse to sell or rent after the making of a bona fide offer, or to refuse to negotiate for the sale or rental of, or otherwise make unavailable or deny, a dwelling to any person because of race, color, religion, sex, familial status, or national origin.

It shall be unlawful to discriminate against any person in the terms, conditions, or privileges of sale or rental of a dwelling, or in the provision of services or facilities in connection therewith, because of race, color, religion, sex, familial status, or national origin.

This section also prohibits: (a) making, printing, or publishing any notice, statement, or advertisement with respect to the sale or rental of a dwelling that indicates any preference, limitation, or discrimination; (b) representing that any dwelling is not available for inspection, sale, or rental when such dwelling is in fact available; and (c) inducing or attempting to induce, for profit, any person to sell or rent any dwelling by representations regarding the entry or prospective entry of persons of a particular race, color, religion, sex, familial status, or national origin.
"""
    },
    {
        "title": "Americans with Disabilities Act",
        "section": "Section 12112: Discrimination in Employment",
        "content": """
No covered entity shall discriminate against a qualified individual on the basis of disability in regard to job application procedures, the hiring, advancement, or discharge of employees, employee compensation, job training, and other terms, conditions, and privileges of employment.

The term "discriminate against a qualified individual on the basis of disability" includes:
(1) limiting, segregating, or classifying a job applicant or employee in a way that adversely affects the opportunities or status of such applicant or employee because of the disability of such applicant or employee;
(2) participating in a contractual or other arrangement or relationship that has the effect of subjecting a covered entity's qualified applicant or employee with a disability to discrimination;
(3) utilizing standards, criteria, or methods of administration that have the effect of discrimination on the basis of disability;
(4) excluding or otherwise denying equal jobs or benefits to a qualified individual because of the known disability of an individual with whom the qualified individual is known to have a relationship or association;
(5) not making reasonable accommodations to the known physical or mental limitations of an otherwise qualified individual with a disability who is an applicant or employee, unless such covered entity can demonstrate that the accommodation would impose an undue hardship on the operation of the business of such covered entity; or
(6) denying employment opportunities to a job applicant or employee who is an otherwise qualified individual with a disability, if such denial is based on the need of such covered entity to make reasonable accommodation to the physical or mental impairments of the employee or applicant.
"""
    }
]

REGULATION_SAMPLES = [
    {
        "title": "Equal Employment Opportunity Commission Regulations",
        "section": "29 CFR § 1604.11 - Sexual harassment",
        "content": """
(a) Harassment on the basis of sex is a violation of section 703 of title VII. Unwelcome sexual advances, requests for sexual favors, and other verbal or physical conduct of a sexual nature constitute sexual harassment when:
(1) submission to such conduct is made either explicitly or implicitly a term or condition of an individual's employment,
(2) submission to or rejection of such conduct by an individual is used as the basis for employment decisions affecting such individual, or
(3) such conduct has the purpose or effect of unreasonably interfering with an individual's work performance or creating an intimidating, hostile, or offensive working environment.

(b) In determining whether alleged conduct constitutes sexual harassment, the Commission will look at the record as a whole and at the totality of the circumstances, such as the nature of the sexual advances and the context in which the alleged incidents occurred. The determination of the legality of a particular action will be made from the facts, on a case by case basis.

(c) Applying general title VII principles, an employer, employment agency, joint apprenticeship committee or labor organization (hereinafter collectively referred to as "employer") is responsible for its acts and those of its agents and supervisory employees with respect to sexual harassment regardless of whether the specific acts complained of were authorized or even forbidden by the employer and regardless of whether the employer knew or should have known of their occurrence.
"""
    },
    {
        "title": "Department of Housing and Urban Development Regulations",
        "section": "24 CFR § 100.400 - Prohibited interference, coercion, or intimidation",
        "content": """
(a) This section provides the Department's interpretation of the conduct that is unlawful under section 818 of the Fair Housing Act.

(b) It shall be unlawful to coerce, intimidate, threaten, or interfere with any person in the exercise or enjoyment of, or on account of that person having exercised or enjoyed, or on account of that person having aided or encouraged any other person in the exercise or enjoyment of, any right granted or protected by this part.

(c) Conduct made unlawful under this section includes, but is not limited to, the following:
(1) Coercing a person, either orally, in writing, or by other means, to deny or limit the benefits provided that person in connection with the sale or rental of a dwelling or in connection with a residential real estate-related transaction because of race, color, religion, sex, handicap, familial status, or national origin.
(2) Threatening, intimidating or interfering with persons in their enjoyment of a dwelling because of the race, color, religion, sex, handicap, familial status, or national origin of such persons, or of visitors or associates of such persons.
(3) Threatening an employee or agent with dismissal or an adverse employment action, or taking such adverse employment action, for any effort to assist a person seeking access to the sale or rental of a dwelling or seeking access to any residential real estate-related transaction, because of the race, color, religion, sex, handicap, familial status, or national origin of that person or of any person associated with that person.
(4) Intimidating or threatening any person because that person is engaging in activities designed to make other persons aware of, or encouraging such other persons to exercise, rights granted or protected by this part.
(5) Retaliating against any person because that person has made a complaint, testified, assisted, or participated in any manner in a proceeding under the Fair Housing Act.
"""
    },
    {
        "title": "Department of Labor Regulations",
        "section": "29 CFR § 1620.13 - Equal Pay for Equal Work",
        "content": """
(a) In general. The equal pay provisions apply to any employer who pays different wages to employees of opposite sexes for equal work on jobs requiring equal skill, effort, and responsibility, and which are performed under similar working conditions in the same establishment. The employer against whom a charge is lodged or a suit brought has the burden of proving that a factor other than sex is the basis for the wage differential.

(b) "Establishment." The prohibition against compensation discrimination under the equal pay provisions applies only to wage differentials as between employees in the same establishment. An "establishment" is a distinct physical place of business rather than an entire business or "enterprise" which may include several separate places of business. Accordingly, each physical location is a separate establishment.

(c) Application to jobs. The equal pay provisions of the Act apply to jobs requiring equal skill, effort, and responsibility, and which are performed under similar working conditions within the same establishment. Where these factors are the same, the Act requires that men and women performing equal work must receive the same rate of pay. The job content, not the job title or classification, determines the equality of jobs. Application of the equal pay standard is not dependent on job classifications or titles but depends rather on actual job requirements and performance.
"""
    }
]

def create_directory_structure():
    """Create the directory structure for test documents"""
    base_dir = Path(__file__).resolve().parent.parent
    
    # Create directories
    for source_type in ["case_law", "statutes", "regulations"]:
        source_dir = base_dir / "data" / "raw_documents" / source_type
        source_dir.mkdir(parents=True, exist_ok=True)
    
    return base_dir

def generate_case_law(base_dir, num_samples=3):
    """Generate sample case law documents"""
    case_law_dir = base_dir / "data" / "raw_documents" / "case_law"
    
    # Clear existing files if any
    for file in case_law_dir.glob("*.txt"):
        file.unlink()
    
    # Generate new files
    count = 0
    for i in range(num_samples):
        sample = random.choice(CASE_LAW_SAMPLES)
        filename = f"[{sample['citation']}] {sample['title']}.txt"
        file_path = case_law_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"CASE: {sample['title']}\n")
            f.write(f"CITATION: {sample['citation']}\n\n")
            f.write(sample['content'])
        
        count += 1
    
    return count

def generate_statutes(base_dir, num_samples=3):
    """Generate sample statute documents"""
    statutes_dir = base_dir / "data" / "raw_documents" / "statutes"
    
    # Clear existing files if any
    for file in statutes_dir.glob("*.txt"):
        file.unlink()
    
    # Generate new files
    count = 0
    for i in range(num_samples):
        sample = random.choice(STATUTE_SAMPLES)
        filename = f"{sample['title']}.txt"
        file_path = statutes_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"TITLE: {sample['title']}\n")
            f.write(f"{sample['section']}\n\n")
            f.write(sample['content'])
        
        count += 1
    
    return count

def generate_regulations(base_dir, num_samples=3):
    """Generate sample regulation documents"""
    regulations_dir = base_dir / "data" / "raw_documents" / "regulations"
    
    # Clear existing files if any
    for file in regulations_dir.glob("*.txt"):
        file.unlink()
    
    # Generate new files
    count = 0
    for i in range(num_samples):
        sample = random.choice(REGULATION_SAMPLES)
        filename = f"{sample['section']} - {sample['title']}.txt"
        file_path = regulations_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"TITLE: {sample['title']}\n")
            f.write(f"SECTION: {sample['section']}\n\n")
            f.write(sample['content'])
        
        count += 1
    
    return count

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Generate sample legal documents for testing')
    parser.add_argument('--count', type=int, default=3, help='Number of samples to generate for each type')
    parser.add_argument('--type', choices=['case_law', 'statutes', 'regulations', 'all'], default='all',
                        help='Type of documents to generate')
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_args()
    base_dir = create_directory_structure()
    
    # Generate documents
    case_law_count = 0
    statutes_count = 0
    regulations_count = 0
    
    if args.type == 'case_law' or args.type == 'all':
        case_law_count = generate_case_law(base_dir, args.count)
        print(f"Generated {case_law_count} case law documents")
    
    if args.type == 'statutes' or args.type == 'all':
        statutes_count = generate_statutes(base_dir, args.count)
        print(f"Generated {statutes_count} statute documents")
        
    if args.type == 'regulations' or args.type == 'all':
        regulations_count = generate_regulations(base_dir, args.count)
        print(f"Generated {regulations_count} regulation documents")
    
    # Print summary
    total = case_law_count + statutes_count + regulations_count
    print(f"\nSuccessfully generated {total} sample documents")
    print(f"Location: {base_dir / 'data' / 'raw_documents'}")
    
    print("\nNext steps:")
    print("1. Run the ingestion script to import these documents into the vector database:")
    print("   python scripts/ingest_documents.py")

if __name__ == "__main__":
    main() 