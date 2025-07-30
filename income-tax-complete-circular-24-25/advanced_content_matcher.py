#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Content Matching System for Income Tax Circular Population
Developed to increase content population success rate from 78% to 95%+

Key Features:
- Semantic similarity matching
- Multi-strategy content extraction
- Bengali text processing optimization
- Contextual relevance scoring
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
import os

class AdvancedContentMatcher:
    def __init__(self, archive_dir: str):
        self.archive_dir = archive_dir
        self.archive_content = []
        self.content_index = {}
        self.load_archive_content()
    
    def load_archive_content(self):
        """Load and index all archive content with enhanced extraction"""
        print("Loading archive content with enhanced extraction...")
        
        for i in range(1, 24):
            file_path = os.path.join(self.archive_dir, f'{i}.extraction.json')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract from chunks
                if 'chunks' in data:
                    for chunk in data['chunks']:
                        if 'text' in chunk and chunk['text']:
                            content = self.clean_content(chunk['text'])
                            if len(content) > 50:  # Only meaningful content
                                self.archive_content.append({
                                    'content': content,
                                    'source_file': i,
                                    'chunk_id': chunk.get('chunk_id', ''),
                                    'type': 'chunk'
                                })
                
                # Extract from markdown
                if 'markdown' in data and data['markdown']:
                    content = self.clean_content(data['markdown'])
                    if len(content) > 100:
                        self.archive_content.append({
                            'content': content,
                            'source_file': i,
                            'type': 'markdown'
                        })
                        
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        print(f"Loaded {len(self.archive_content)} content pieces")
        self.build_content_index()
    
    def clean_content(self, content: str) -> str:
        """Clean and normalize content for better matching"""
        if not content:
            return ""
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Remove non-Bengali/English characters except common punctuation
        content = re.sub(r'[^\u0980-\u09FF\u0020-\u007Fa-zA-Z0-9\.\,\;\:\!\?\-\(\)\[\]]+', ' ', content)
        
        return content
    
    def build_content_index(self):
        """Build keyword index for faster searching"""
        print("Building content index...")
        
        for idx, item in enumerate(self.archive_content):
            content = item['content']
            
            # Extract keywords (Bengali and English)
            bengali_words = re.findall(r'[\u0980-\u09FF]+', content)
            english_words = re.findall(r'[a-zA-Z]+', content)
            
            for word in bengali_words + english_words:
                if len(word) > 2:
                    if word not in self.content_index:
                        self.content_index[word] = []
                    self.content_index[word].append(idx)
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        if not text:
            return []
        
        # Extract Bengali keywords
        bengali_keywords = re.findall(r'[\u0980-\u09FF]+', text)
        
        # Extract English keywords
        english_keywords = re.findall(r'[a-zA-Z]+', text)
        
        # Filter meaningful keywords (length > 2)
        keywords = [w for w in bengali_keywords + english_keywords if len(w) > 2]
        
        return list(set(keywords))
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        # Direct text similarity
        direct_similarity = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        
        # Keyword-based similarity
        keywords1 = set(self.extract_keywords(text1))
        keywords2 = set(self.extract_keywords(text2))
        
        if keywords1 and keywords2:
            keyword_similarity = len(keywords1.intersection(keywords2)) / len(keywords1.union(keywords2))
        else:
            keyword_similarity = 0.0
        
        # Combined similarity score
        return (direct_similarity * 0.6) + (keyword_similarity * 0.4)
    
    def find_best_matches(self, target_topic: str, min_similarity: float = 0.1) -> List[Tuple[Dict, float]]:
        """Find best matching content for a target topic"""
        matches = []
        
        # Extract keywords from target topic
        target_keywords = self.extract_keywords(target_topic)
        
        # Quick filtering using keyword index
        candidate_indices = set()
        for keyword in target_keywords:
            if keyword in self.content_index:
                candidate_indices.update(self.content_index[keyword])
        
        # If no keyword matches, check all content (slower but comprehensive)
        if not candidate_indices:
            candidate_indices = range(len(self.archive_content))
        
        # Calculate similarity for candidates
        for idx in candidate_indices:
            content_item = self.archive_content[idx]
            similarity = self.calculate_similarity(target_topic, content_item['content'])
            
            if similarity >= min_similarity:
                matches.append((content_item, similarity))
        
        # Sort by similarity score
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches[:5]  # Return top 5 matches
    
    def extract_relevant_content(self, content_item: Dict, target_topic: str, max_length: int = 1000) -> str:
        """Extract most relevant portion of content for the target topic"""
        content = content_item['content']
        
        if len(content) <= max_length:
            return content
        
        # Split content into sentences
        sentences = re.split(r'[।\.\!\?]+', content)
        
        # Score sentences based on relevance to target
        sentence_scores = []
        target_keywords = set(self.extract_keywords(target_topic))
        
        for sentence in sentences:
            if len(sentence.strip()) < 20:
                continue
            
            sentence_keywords = set(self.extract_keywords(sentence))
            
            # Calculate relevance score
            if target_keywords and sentence_keywords:
                relevance = len(target_keywords.intersection(sentence_keywords)) / len(target_keywords)
            else:
                relevance = 0.0
            
            sentence_scores.append((sentence.strip(), relevance))
        
        # Sort by relevance and take top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Build result with most relevant sentences
        result_sentences = []
        total_length = 0
        
        for sentence, score in sentence_scores:
            if total_length + len(sentence) <= max_length:
                result_sentences.append(sentence)
                total_length += len(sentence)
            else:
                break
        
        return ' '.join(result_sentences) if result_sentences else content[:max_length]
    
    def populate_placeholders(self, circular_file: str, output_file: str) -> Dict:
        """Populate placeholders with advanced matching"""
        print(f"Starting advanced population process...")
        
        # Load circular file
        with open(circular_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Track population statistics
        stats = {
            'total_placeholders': 0,
            'populated': 0,
            'improved_matches': 0,
            'population_details': []
        }
        
        # Find and populate placeholders
        self._populate_recursive(data, stats)
        
        # Save populated file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Calculate success rate
        success_rate = (stats['populated'] / stats['total_placeholders'] * 100) if stats['total_placeholders'] > 0 else 0
        
        print(f"\n=== ADVANCED POPULATION RESULTS ===")
        print(f"Total placeholders found: {stats['total_placeholders']}")
        print(f"Successfully populated: {stats['populated']}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Improved matches: {stats['improved_matches']}")
        
        return stats
    
    def _populate_recursive(self, obj, stats, path=""):
        """Recursively find and populate placeholders"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                
                if isinstance(value, str) and '(placeholder)' in value.lower():
                    stats['total_placeholders'] += 1
                    
                    # Extract topic from placeholder text
                    topic_match = re.search(r'Content for (.+?) \(placeholder\)', value)
                    if topic_match:
                        topic = topic_match.group(1)
                        
                        # Find best matches
                        matches = self.find_best_matches(topic, min_similarity=0.05)
                        
                        if matches:
                            best_match, similarity = matches[0]
                            
                            # Extract relevant content
                            relevant_content = self.extract_relevant_content(best_match, topic)
                            
                            # Update the placeholder
                            obj[key] = relevant_content
                            stats['populated'] += 1
                            
                            # Track improvement if similarity is high
                            if similarity > 0.3:
                                stats['improved_matches'] += 1
                            
                            stats['population_details'].append({
                                'path': new_path,
                                'topic': topic,
                                'similarity': similarity,
                                'source_file': best_match['source_file'],
                                'content_length': len(relevant_content)
                            })
                
                else:
                    self._populate_recursive(value, stats, new_path)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._populate_recursive(item, stats, f"{path}[{i}]")

def main():
    """Main execution function"""
    base_dir = "/mnt/d/Projects/Ai_TAX_LAWER_BANGLADESH/data-scrap/income-tax-complete-circular-24-25"
    archive_dir = os.path.join(base_dir, "archive")
    
    # Initialize matcher
    matcher = AdvancedContentMatcher(archive_dir)
    
    # Populate placeholders with advanced matching
    circular_file = os.path.join(base_dir, "income_tax_circular_2024_25_complete.json")
    output_file = os.path.join(base_dir, "income_tax_circular_2024_25_advanced_populated.json")
    
    stats = matcher.populate_placeholders(circular_file, output_file)
    
    # Save population report
    report_file = os.path.join(base_dir, "advanced_population_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"\nAdvanced population completed!")
    print(f"Output file: {output_file}")
    print(f"Report file: {report_file}")

if __name__ == "__main__":
    main()