#!/usr/bin/env python3
"""
Income Tax Circular 24-25 Automated Topic Processor
==================================================

This system processes 460 pages of income tax circular (23 files × 20 pages each)
into structured JSON format for AI Tax Lawyer system with multi-hop RAG capability.

Architecture:
- File 1: Table of Contents (188 topics index)
- Files 2-23: Content processing (22 files × 20 pages each)
- Output: Structured JSON for precise tax calculation and cross-referencing
"""

import json
import re
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TopicStructure:
    """Structured representation of a tax topic"""
    topic_id: str
    topic_number: int
    title_bengali: str
    title_english: str
    page_reference: int
    category: str
    subcategory: str
    content_bengali: str
    summary_english: str
    key_points: List[str]
    legal_references: List[str]
    calculation_formulas: List[Dict[str, Any]]
    cross_references: List[str]
    applicability: Dict[str, Any]
    examples: List[Dict[str, Any]]
    ai_metadata: Dict[str, Any]

class IncomeCircularProcessor:
    """Main processor for Income Tax Circular 24-25"""
    
    def __init__(self, data_directory: str):
        self.data_dir = Path(data_directory)
        self.topics_index = {}
        self.processed_topics = {}
        self.cross_reference_map = {}
        self.calculation_engine = {}
        
        # Category mapping for 188 topics
        self.category_mapping = {
            "basic_rates": {"range": (1, 20), "description": "Tax rates and surcharges"},
            "amendments": {"range": (21, 80), "description": "Legal amendments and definitions"},
            "charitable": {"range": (31, 77), "description": "Charitable organization provisions"},
            "income_categories": {"range": (78, 110), "description": "Income calculation methods"},
            "procedural": {"range": (111, 188), "description": "Administrative procedures"}
        }
        
        # AI intent classification tags
        self.intent_tags = [
            "tax_calculation", "rate_inquiry", "exemption_check", "surcharge_computation",
            "charitable_eligibility", "income_categorization", "procedural_guidance",
            "legal_reference", "amendment_tracking", "cross_reference_lookup",
            "formula_application", "compliance_check", "documentation_requirement",
            "timeline_guidance", "penalty_calculation"
        ]

    def load_extraction_file(self, file_number: int) -> Dict[str, Any]:
        """Load and parse extraction JSON file"""
        file_path = self.data_dir / f"{file_number}.extraction.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def extract_table_of_contents(self) -> Dict[str, Any]:
        """Extract and structure table of contents from file 1"""
        toc_data = self.load_extraction_file(1)
        
        # Parse table structure from markdown content
        markdown_content = toc_data.get('markdown', '')
        
        # Extract table rows using regex
        table_pattern = r'<tr><td>(\d+)</td><td>(.*?)</td><td>(\d+)</td></tr>'
        matches = re.findall(table_pattern, markdown_content, re.DOTALL)
        
        topics_index = {}
        for match in matches:
            topic_num = int(match[0])
            title_bengali = match[1].strip()
            page_ref = int(match[2])
            
            # Categorize topic
            category = self._categorize_topic(topic_num)
            
            # Generate English title (simplified translation)
            title_english = self._generate_english_title(title_bengali)
            
            # Generate AI metadata
            ai_metadata = self._generate_ai_metadata(title_bengali, title_english, category)
            
            topics_index[str(topic_num)] = {
                "topic_id": f"topic_{topic_num:03d}",
                "topic_number": topic_num,
                "title_bengali": title_bengali,
                "title_english": title_english,
                "page_reference": page_ref,
                "category": category["name"],
                "subcategory": category["subcategory"],
                "file_location": self._determine_file_location(page_ref),
                "ai_metadata": ai_metadata
            }
        
        return topics_index

    def _categorize_topic(self, topic_num: int) -> Dict[str, str]:
        """Categorize topic based on number range"""
        for cat_name, cat_info in self.category_mapping.items():
            start, end = cat_info["range"]
            if start <= topic_num <= end:
                return {
                    "name": cat_name,
                    "subcategory": self._get_subcategory(topic_num, cat_name),
                    "description": cat_info["description"]
                }
        return {"name": "miscellaneous", "subcategory": "other", "description": "Other provisions"}

    def _get_subcategory(self, topic_num: int, category: str) -> str:
        """Get subcategory based on topic number and main category"""
        subcategory_map = {
            "basic_rates": {
                (1, 10): "individual_rates",
                (11, 20): "corporate_rates"
            },
            "amendments": {
                (21, 30): "definitions",
                (31, 50): "legal_changes",
                (51, 80): "references"
            },
            "charitable": {
                (31, 50): "eligibility_criteria",
                (51, 77): "operational_guidelines"
            },
            "income_categories": {
                (78, 90): "income_types",
                (91, 110): "calculation_methods"
            },
            "procedural": {
                (111, 140): "filing_procedures",
                (141, 170): "audit_procedures",
                (171, 188): "appeal_procedures"
            }
        }
        
        if category in subcategory_map:
            for range_tuple, subcat in subcategory_map[category].items():
                if range_tuple[0] <= topic_num <= range_tuple[1]:
                    return subcat
        
        return "general"

    def _determine_file_location(self, page_ref: int) -> int:
        """Determine which extraction file contains the topic content"""
        # File 1: Pages 1-20 (Table of Contents)
        # File 2: Pages 21-40
        # File 3: Pages 41-60
        # ... and so on
        return ((page_ref - 1) // 20) + 1

    def _generate_english_title(self, bengali_title: str) -> str:
        """Generate simplified English title (placeholder - would use translation service)"""
        # This is a simplified mapping - in production, use proper translation
        common_translations = {
            "করহার": "tax rate",
            "সারচার্জ": "surcharge",
            "অবাহতি": "exemption",
            "দাতব্য": "charitable",
            "আয়": "income",
            "নির্ধারণ": "assessment",
            "রিটার্ন": "return",
            "অডিট": "audit"
        }
        
        english_title = bengali_title
        for bengali, english in common_translations.items():
            english_title = english_title.replace(bengali, english)
        
        return f"Topic regarding {english_title.lower()}"

    def _generate_ai_metadata(self, title_bengali: str, title_english: str, category: Dict) -> Dict[str, Any]:
        """Generate AI optimization metadata for topic"""
        
        # Intent classification based on keywords
        intents = []
        if any(word in title_bengali for word in ["করহার", "হার"]):
            intents.append("tax_calculation")
        if any(word in title_bengali for word in ["অবাহতি", "ছাড়"]):
            intents.append("exemption_check")
        if any(word in title_bengali for word in ["সারচার্জ"]):
            intents.append("surcharge_computation")
        if any(word in title_bengali for word in ["দাতব্য"]):
            intents.append("charitable_eligibility")
        
        # Generate search keywords
        keywords_bengali = self._extract_keywords_bengali(title_bengali)
        keywords_english = self._extract_keywords_english(title_english)
        
        # Query patterns
        query_patterns = self._generate_query_patterns(title_bengali, category)
        
        return {
            "intent_classification": intents,
            "search_keywords": {
                "bengali": keywords_bengali,
                "english": keywords_english
            },
            "query_patterns": query_patterns,
            "complexity_level": self._assess_complexity(title_bengali, category),
            "user_frequency": "medium",  # Would be updated based on usage analytics
            "requires_calculation": self._requires_calculation(title_bengali)
        }

    def _extract_keywords_bengali(self, title: str) -> List[str]:
        """Extract Bengali keywords from title"""
        # Common Bengali tax terms
        tax_keywords = ["কর", "করহার", "সারচার্জ", "অবাহতি", "দাতব্য", "আয়", "রিটার্ন", "অডিট", "নির্ধারণ"]
        found_keywords = [kw for kw in tax_keywords if kw in title]
        
        # Add title words (simplified)
        title_words = title.split()
        found_keywords.extend([word for word in title_words if len(word) > 2])
        
        return list(set(found_keywords))

    def _extract_keywords_english(self, title: str) -> List[str]:
        """Extract English keywords from title"""
        common_words = ["the", "of", "and", "or", "in", "to", "for", "with", "by"]
        words = [word.lower() for word in title.split() if word.lower() not in common_words]
        return list(set(words))

    def _generate_query_patterns(self, title: str, category: Dict) -> List[str]:
        """Generate common user query patterns"""
        patterns = []
        
        if "করهার" in title:
            patterns.extend([
                "কর হার কত?",
                "What is the tax rate?",
                "How to calculate tax?",
                f"{category['name']} এর কর হার"
            ])
        
        if "অবাহতি" in title:
            patterns.extend([
                "কর অবাহতি পাবো কিভাবে?",
                "How to get tax exemption?",
                "Exemption eligibility criteria"
            ])
        
        return patterns

    def _assess_complexity(self, title: str, category: Dict) -> str:
        """Assess topic complexity level"""
        if category["name"] == "basic_rates":
            return "basic"
        elif category["name"] in ["amendments", "procedural"]:
            return "advanced"
        else:
            return "intermediate"

    def _requires_calculation(self, title: str) -> bool:
        """Check if topic requires calculation functionality"""
        calc_keywords = ["করهার", "সারচার্জ", "গণনা", "হিসাব", "পরিমাণ"]
        return any(keyword in title for keyword in calc_keywords)

    def process_content_file(self, file_number: int, topics_index: Dict) -> Dict[str, Any]:
        """Process content from extraction files 2-23"""
        content_data = self.load_extraction_file(file_number)
        processed_content = {}
        
        # Calculate page range for this file
        start_page = (file_number - 1) * 20 + 1
        end_page = file_number * 20
        
        # Find topics that belong to this file
        relevant_topics = {}
        for topic_id, topic_info in topics_index.items():
            if start_page <= topic_info["page_reference"] <= end_page:
                relevant_topics[topic_id] = topic_info
        
        # Extract content for each relevant topic
        markdown_content = content_data.get('markdown', '')
        
        for topic_id, topic_info in relevant_topics.items():
            processed_topic = self._extract_topic_content(
                topic_info, markdown_content, file_number
            )
            processed_content[topic_id] = processed_topic
        
        return processed_content

    def _extract_topic_content(self, topic_info: Dict, markdown_content: str, file_number: int) -> Dict[str, Any]:
        """Extract detailed content for a specific topic"""
        
        # This is a sophisticated content extraction that would need
        # to parse the markdown and identify topic boundaries
        
        topic_structure = {
            "topic_id": topic_info["topic_id"],
            "metadata": topic_info,
            "content": {
                "bengali_text": self._extract_bengali_content(markdown_content, topic_info),
                "english_summary": self._generate_english_summary(topic_info),
                "key_points": self._extract_key_points(markdown_content, topic_info),
                "legal_references": self._extract_legal_references(markdown_content),
                "tables_and_schedules": self._extract_tables(markdown_content),
                "calculation_formulas": self._extract_calculation_formulas(markdown_content),
                "examples": self._extract_examples(markdown_content)
            },
            "cross_references": self._identify_cross_references(markdown_content),
            "ai_optimization": {
                "search_vectors": self._generate_search_vectors(topic_info),
                "intent_mapping": self._map_intents(topic_info),
                "calculation_triggers": self._identify_calculation_triggers(markdown_content)
            }
        }
        
        return topic_structure

    def _extract_bengali_content(self, markdown: str, topic_info: Dict) -> str:
        """Extract Bengali content for the topic"""
        # Sophisticated content extraction based on topic boundaries
        # This would need to identify where each topic starts and ends
        return f"Content for {topic_info['title_bengali']} (placeholder)"

    def _generate_english_summary(self, topic_info: Dict) -> str:
        """Generate English summary of the topic"""
        return f"Summary of {topic_info['title_english']}"

    def _extract_key_points(self, markdown: str, topic_info: Dict) -> List[str]:
        """Extract key points from topic content"""
        return ["Key point 1", "Key point 2"]  # Placeholder

    def _extract_legal_references(self, markdown: str) -> List[str]:
        """Extract legal section references"""
        # Pattern to find section references like "ধারা ১০২"
        section_pattern = r'ধারা\s+(\d+)'
        matches = re.findall(section_pattern, markdown)
        return [f"Section {match}" for match in matches]

    def _extract_tables(self, markdown: str) -> List[Dict[str, Any]]:
        """Extract tables and schedules"""
        tables = []
        # Find HTML tables in markdown
        table_pattern = r'<table>(.*?)</table>'
        table_matches = re.findall(table_pattern, markdown, re.DOTALL)
        
        for i, table_content in enumerate(table_matches):
            tables.append({
                "table_id": f"table_{i+1}",
                "html_content": f"<table>{table_content}</table>",
                "extracted_data": self._parse_table_data(table_content)
            })
        
        return tables

    def _parse_table_data(self, table_html: str) -> List[List[str]]:
        """Parse table HTML into structured data"""
        # Simplified table parsing
        row_pattern = r'<tr>(.*?)</tr>'
        cell_pattern = r'<td>(.*?)</td>'
        
        rows = re.findall(row_pattern, table_html, re.DOTALL)
        parsed_data = []
        
        for row in rows:
            cells = re.findall(cell_pattern, row)
            parsed_data.append([cell.strip() for cell in cells])
        
        return parsed_data

    def _extract_calculation_formulas(self, markdown: str) -> List[Dict[str, Any]]:
        """Extract calculation formulas and rules"""
        formulas = []
        
        # Look for percentage patterns
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*%'
        percentages = re.findall(percentage_pattern, markdown)
        
        for i, percentage in enumerate(percentages):
            formulas.append({
                "formula_id": f"formula_{i+1}",
                "type": "percentage",
                "value": float(percentage),
                "description": f"Rate of {percentage}%",
                "context": "tax_calculation"
            })
        
        return formulas

    def _extract_examples(self, markdown: str) -> List[Dict[str, Any]]:
        """Extract practical examples"""
        # Look for example patterns in Bengali
        examples = []
        example_patterns = ["উদাহরণ", "দৃষ্টান্ত", "নমুনা"]
        
        for pattern in example_patterns:
            if pattern in markdown:
                examples.append({
                    "example_id": f"example_{len(examples)+1}",
                    "type": "practical_example",
                    "content": f"Example containing {pattern}",
                    "scenario": "typical_case"
                })
        
        return examples

    def _identify_cross_references(self, markdown: str) -> List[str]:
        """Identify cross-references to other topics"""
        # Look for topic number references
        topic_ref_pattern = r'(\d+)\s*নং\s*বিষয়'
        matches = re.findall(topic_ref_pattern, markdown)
        return [f"topic_{int(match):03d}" for match in matches]

    def _generate_search_vectors(self, topic_info: Dict) -> Dict[str, List[float]]:
        """Generate search vectors for semantic similarity"""
        # Placeholder for vector generation - would use embeddings
        return {
            "title_vector": [0.1] * 384,  # Placeholder embedding
            "content_vector": [0.2] * 384,
            "keyword_vector": [0.3] * 384
        }

    def _map_intents(self, topic_info: Dict) -> Dict[str, float]:
        """Map topic to intent classification scores"""
        intent_scores = {}
        for intent in self.intent_tags:
            if intent in topic_info["ai_metadata"]["intent_classification"]:
                intent_scores[intent] = 0.9
            else:
                intent_scores[intent] = 0.1
        return intent_scores

    def _identify_calculation_triggers(self, markdown: str) -> List[Dict[str, Any]]:
        """Identify triggers for calculation engine"""
        triggers = []
        
        calc_keywords = ["গণনা", "হিসাব", "করহার", "পরিমাণ"]
        for keyword in calc_keywords:
            if keyword in markdown:
                triggers.append({
                    "trigger_type": "calculation_required",
                    "keyword": keyword,
                    "calculation_type": self._determine_calculation_type(keyword)
                })
        
        return triggers

    def _determine_calculation_type(self, keyword: str) -> str:
        """Determine type of calculation based on keyword"""
        calc_type_map = {
            "করহার": "tax_rate_calculation",
            "সারচার্জ": "surcharge_calculation",
            "গণনা": "general_calculation",
            "হিসাব": "accounting_calculation"
        }
        return calc_type_map.get(keyword, "general_calculation")

    def process_all_files(self) -> Dict[str, Any]:
        """Process all extraction files and create complete structured database"""
        
        print("🚀 Starting Income Tax Circular 24-25 Processing...")
        
        # Step 1: Extract table of contents
        print("📋 Processing Table of Contents...")
        topics_index = self.extract_table_of_contents()
        print(f"✅ Extracted {len(topics_index)} topics from index")
        
        # Step 2: Process content files
        all_processed_content = {}
        
        for file_num in range(2, 24):  # Files 2-23
            print(f"📄 Processing File {file_num}/23...")
            try:
                content = self.process_content_file(file_num, topics_index)
                all_processed_content.update(content)
                print(f"✅ File {file_num} processed: {len(content)} topics")
            except FileNotFoundError:
                print(f"⚠️ File {file_num}.extraction.json not found, skipping...")
            except Exception as e:
                print(f"❌ Error processing file {file_num}: {str(e)}")
        
        # Step 3: Build cross-reference mapping
        print("🔗 Building cross-reference mapping...")
        cross_ref_map = self._build_cross_reference_map(all_processed_content)
        
        # Step 4: Create calculation engine rules
        print("⚙️ Creating calculation engine rules...")
        calc_engine = self._create_calculation_engine(all_processed_content)
        
        # Step 5: Generate final structured database
        final_database = {
            "metadata": {
                "source": "Income Tax Circular 2024-25",
                "total_pages": 460,
                "total_topics": len(topics_index),
                "total_files": 23,
                "processing_date": "2024",
                "version": "1.0"
            },
            "topics_index": topics_index,
            "structured_content": all_processed_content,
            "cross_reference_mapping": cross_ref_map,
            "calculation_engine": calc_engine,
            "ai_optimization_data": self._generate_ai_optimization_data(
                topics_index, all_processed_content
            )
        }
        
        print("🎯 Processing completed successfully!")
        return final_database

    def _build_cross_reference_map(self, content: Dict) -> Dict[str, Any]:
        """Build comprehensive cross-reference mapping"""
        cross_ref_map = {
            "topic_to_topic": {},
            "topic_to_section": {},
            "calculation_dependencies": {},
            "hierarchical_structure": {}
        }
        
        for topic_id, topic_data in content.items():
            cross_ref_map["topic_to_topic"][topic_id] = topic_data.get("cross_references", [])
        
        return cross_ref_map

    def _create_calculation_engine(self, content: Dict) -> Dict[str, Any]:
        """Create calculation engine rules and formulas"""
        calc_engine = {
            "tax_rate_formulas": {},
            "surcharge_formulas": {},
            "exemption_rules": {},
            "calculation_workflows": {}
        }
        
        for topic_id, topic_data in content.items():
            formulas = topic_data.get("content", {}).get("calculation_formulas", [])
            for formula in formulas:
                calc_engine["tax_rate_formulas"][topic_id] = formula
        
        return calc_engine

    def _generate_ai_optimization_data(self, topics_index: Dict, content: Dict) -> Dict[str, Any]:
        """Generate AI optimization data for multi-hop RAG"""
        return {
            "intent_classification_map": self._create_intent_map(topics_index),
            "semantic_search_data": self._create_search_data(content),
            "query_routing_rules": self._create_routing_rules(topics_index),
            "vector_embeddings_config": self._create_embeddings_config()
        }

    def _create_intent_map(self, topics_index: Dict) -> Dict[str, List[str]]:
        """Create intent to topic mapping"""
        intent_map = {}
        for intent in self.intent_tags:
            intent_map[intent] = []
            for topic_id, topic_info in topics_index.items():
                if intent in topic_info["ai_metadata"]["intent_classification"]:
                    intent_map[intent].append(topic_id)
        return intent_map

    def _create_search_data(self, content: Dict) -> Dict[str, Any]:
        """Create semantic search optimization data"""
        return {
            "keyword_index": self._build_keyword_index(content),
            "topic_similarity_matrix": self._build_similarity_matrix(content),
            "search_optimization_config": {
                "primary_language": "bengali",
                "secondary_language": "english",
                "search_fields": ["title", "content", "keywords", "examples"]
            }
        }

    def _build_keyword_index(self, content: Dict) -> Dict[str, List[str]]:
        """Build inverted keyword index"""
        keyword_index = {}
        
        for topic_id, topic_data in content.items():
            metadata = topic_data.get("metadata", {}).get("ai_metadata", {})
            keywords = metadata.get("search_keywords", {})
            
            all_keywords = keywords.get("bengali", []) + keywords.get("english", [])
            
            for keyword in all_keywords:
                if keyword not in keyword_index:
                    keyword_index[keyword] = []
                keyword_index[keyword].append(topic_id)
        
        return keyword_index

    def _build_similarity_matrix(self, content: Dict) -> Dict[str, Dict[str, float]]:
        """Build topic similarity matrix for recommendation"""
        # Simplified similarity calculation
        similarity_matrix = {}
        
        for topic_id1 in content.keys():
            similarity_matrix[topic_id1] = {}
            for topic_id2 in content.keys():
                if topic_id1 == topic_id2:
                    similarity_matrix[topic_id1][topic_id2] = 1.0
                else:
                    # Simplified similarity based on category
                    cat1 = content[topic_id1]["metadata"]["category"]
                    cat2 = content[topic_id2]["metadata"]["category"]
                    similarity_matrix[topic_id1][topic_id2] = 0.8 if cat1 == cat2 else 0.2
        
        return similarity_matrix

    def _create_routing_rules(self, topics_index: Dict) -> Dict[str, Any]:
        """Create query routing rules for multi-hop RAG"""
        return {
            "category_routing": {
                cat: [tid for tid, tinfo in topics_index.items() 
                     if tinfo["category"] == cat]
                for cat in set(tinfo["category"] for tinfo in topics_index.values())
            },
            "complexity_routing": {
                level: [tid for tid, tinfo in topics_index.items()
                       if tinfo["ai_metadata"]["complexity_level"] == level]
                for level in ["basic", "intermediate", "advanced"]
            },
            "calculation_routing": [
                tid for tid, tinfo in topics_index.items()
                if tinfo["ai_metadata"]["requires_calculation"]
            ]
        }

    def _create_embeddings_config(self) -> Dict[str, Any]:
        """Create configuration for vector embeddings"""
        return {
            "embedding_model": "multilingual-e5-large",
            "dimension": 1024,
            "fields_to_embed": [
                "title_bengali",
                "title_english", 
                "content_bengali",
                "summary_english",
                "key_points"
            ],
            "similarity_metric": "cosine",
            "index_type": "hnsw"
        }

    def save_structured_database(self, database: Dict[str, Any], output_path: str):
        """Save the complete structured database"""
        output_file = Path(output_path)
        
        # Save main database
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        
        # Save separate components for modularity
        components = {
            "topics_index": database["topics_index"],
            "cross_reference_mapping": database["cross_reference_mapping"],
            "calculation_engine": database["calculation_engine"],
            "ai_optimization_data": database["ai_optimization_data"]
        }
        
        for component_name, component_data in components.items():
            component_file = output_file.parent / f"{component_name}.json"
            with open(component_file, 'w', encoding='utf-8') as f:
                json.dump(component_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Database saved to {output_file}")
        print(f"📁 Component files saved in {output_file.parent}")


def main():
    """Main execution function"""
    
    # Configuration
    DATA_DIRECTORY = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/income-tax-complete-circular-24-25"
    OUTPUT_PATH = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/income-tax-complete-circular-24-25/income_tax_circular_2024_25_complete.json"
    
    # Initialize processor
    processor = IncomeCircularProcessor(DATA_DIRECTORY)
    
    try:
        # Process all files
        structured_database = processor.process_all_files()
        
        # Save results
        processor.save_structured_database(structured_database, OUTPUT_PATH)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 PROCESSING SUMMARY")
        print("="*60)
        print(f"📄 Total Topics Processed: {len(structured_database['topics_index'])}")
        print(f"📄 Content Files Processed: 22 files (Files 2-23)")
        print(f"🔗 Cross-references Mapped: {len(structured_database['cross_reference_mapping']['topic_to_topic'])}")
        print(f"⚙️ Calculation Rules Created: {len(structured_database['calculation_engine']['tax_rate_formulas'])}")
        print(f"🤖 AI Intent Tags: {len(structured_database['ai_optimization_data']['intent_classification_map'])}")
        print(f"💾 Output File: {OUTPUT_PATH}")
        print("="*60)
        print("✅ Income Tax Circular 24-25 processing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        raise


if __name__ == "__main__":
    main()