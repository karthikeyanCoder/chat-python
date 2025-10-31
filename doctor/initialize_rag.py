#!/usr/bin/env python3
"""
RAG System Initialization Script
Initializes the medical knowledge base and vector database for the RAG system.
"""

import os
import sys
import logging
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.medical_knowledge_base import MedicalKnowledgeBase
from services.vector_database import VectorDatabase
from services.rag_medical_service import RAGMedicalService

def setup_logging():
    """Set up logging for the initialization process."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def initialize_rag_system():
    """Initialize the complete RAG system."""
    logger = setup_logging()
    
    try:
        logger.info("Starting RAG system initialization...")
        
        # Initialize medical knowledge base
        logger.info("Initializing medical knowledge base...")
        knowledge_base = MedicalKnowledgeBase()
        knowledge_stats = knowledge_base.get_stats()
        logger.info(f"Medical knowledge base initialized: {knowledge_stats}")
        
        # Initialize vector database
        logger.info("Initializing vector database...")
        vector_db = VectorDatabase()
        vector_stats = vector_db.get_stats()
        logger.info(f"Vector database initialized: {vector_stats}")
        
        # Add knowledge chunks to vector database
        logger.info("Adding knowledge chunks to vector database...")
        knowledge_chunks = knowledge_base.get_knowledge_chunks()
        
        # Convert knowledge chunks to vector database format
        vector_chunks = []
        for chunk in knowledge_chunks:
            vector_chunks.append({
                'content': chunk['content'],
                'metadata': chunk['metadata']
            })
        
        # Add chunks to vector database
        success = vector_db.add_chunks(vector_chunks)
        if success:
            logger.info(f"Successfully added {len(vector_chunks)} knowledge chunks to vector database")
        else:
            logger.error("Failed to add knowledge chunks to vector database")
            return False
        
        # Test RAG service
        logger.info("Testing RAG service...")
        rag_service = RAGMedicalService()
        
        # Test with sample patient data
        sample_patient_data = {
            'pregnancy_week': 8,
            'age': 28,
            'blood_type': 'O+',
            'symptom_analysis_reports': [
                {
                    'symptom_text': 'morning sickness',
                    'severity': 'moderate'
                }
            ],
            'medication_logs': [
                {
                    'medication_name': 'prenatal vitamins'
                }
            ]
        }
        
        # Test medical context retrieval
        context = rag_service.get_medical_context(sample_patient_data, "pregnancy")
        logger.info(f"Retrieved {len(context)} medical context chunks for test patient")
        
        # Test enhanced summary generation
        enhanced_summary = rag_service.generate_enhanced_summary(
            sample_patient_data, 
            context, 
            "pregnancy"
        )
        
        if enhanced_summary.get('rag_enhanced', False):
            logger.info("RAG system test successful - Enhanced summary generated")
        else:
            logger.warning("RAG system test completed with fallback summary")
        
        # Final statistics
        final_vector_stats = vector_db.get_stats()
        final_knowledge_stats = knowledge_base.get_stats()
        
        logger.info("RAG System Initialization Complete!")
        logger.info(f"Vector Database: {final_vector_stats}")
        logger.info(f"Knowledge Base: {final_knowledge_stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing RAG system: {str(e)}")
        return False

def main():
    """Main function to run the initialization."""
    print("=" * 60)
    print("RAG Medical System Initialization")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = initialize_rag_system()
    
    print()
    print("=" * 60)
    if success:
        print("✅ RAG System Initialization SUCCESSFUL!")
        print("The system is ready to provide enhanced medical AI summaries.")
    else:
        print("❌ RAG System Initialization FAILED!")
        print("Please check the logs for error details.")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
