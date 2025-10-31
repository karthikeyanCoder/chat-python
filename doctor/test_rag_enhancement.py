#!/usr/bin/env python3
"""
Test script to demonstrate RAG enhancement in AI summary endpoint.
"""

import requests
import json
import time
from datetime import datetime

def test_rag_enhanced_summary():
    """Test the RAG-enhanced AI summary endpoint."""
    
    base_url = "http://localhost:8000"
    patient_id = "PAT175820015455746A"
    
    print("=" * 80)
    print("RAG-Enhanced AI Summary Test")
    print("=" * 80)
    print(f"Testing patient: {patient_id}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Basic AI summary (7 days)
    print("🧪 Test 1: Basic AI Summary (7 days)")
    print("-" * 50)
    
    try:
        response = requests.get(
            f"{base_url}/doctor/patient/{patient_id}/ai-summary",
            params={"days": 7},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Request successful!")
            print(f"📊 Response structure:")
            print(f"   - Success: {data.get('success', False)}")
            print(f"   - Message: {data.get('message', 'N/A')}")
            
            if 'data' in data:
                patient_data = data['data']
                print(f"   - Patient ID: {patient_data.get('patient_id', 'N/A')}")
                print(f"   - Date Range: {patient_data.get('date_range_days', 'N/A')} days")
                print(f"   - Generated At: {patient_data.get('generated_at', 'N/A')}")
                
                # Check if RAG enhancement is working
                ai_summary = patient_data.get('ai_summary', '')
                if 'RAG' in ai_summary or 'medical context' in ai_summary.lower():
                    print("🧠 RAG Enhancement: DETECTED")
                else:
                    print("🤖 AI Mode: Basic (RAG may not be active)")
                
                # Show statistics
                stats = patient_data.get('statistics', {})
                if stats:
                    print(f"📈 Statistics available:")
                    print(f"   - Food entries: {stats.get('food_nutrition', {}).get('total_entries', 0)}")
                    print(f"   - Medication logs: {stats.get('medication_adherence', {}).get('total_medications', 0)}")
                    print(f"   - Symptoms: {stats.get('symptoms_tracking', {}).get('total_symptoms', 0)}")
                    print(f"   - Sleep logs: {stats.get('sleep_patterns', {}).get('total_sleep_logs', 0)}")
                    print(f"   - Kick counts: {stats.get('kick_count_tracking', {}).get('total_kick_sessions', 0)}")
                    print(f"   - Mental health: {stats.get('mental_health', {}).get('total_entries', 0)}")
                    print(f"   - Hydration: {stats.get('hydration', {}).get('total_records', 0)}")
                
                # Show risk assessment
                risk_assessment = patient_data.get('pregnancy_risk_assessment', {})
                if risk_assessment:
                    print(f"🎯 Risk Assessment:")
                    print(f"   - Risk Level: {risk_assessment.get('overall_risk_level', 'N/A')}")
                    print(f"   - Risk Score: {risk_assessment.get('risk_score', 'N/A')}/100")
                    print(f"   - Risk Factors: {len(risk_assessment.get('risk_factors', []))}")
                    print(f"   - Protective Factors: {len(risk_assessment.get('protective_factors', []))}")
                
                # Show AI summary preview
                print(f"🤖 AI Summary Preview:")
                summary_preview = ai_summary[:200] + "..." if len(ai_summary) > 200 else ai_summary
                print(f"   {summary_preview}")
                
            else:
                print("❌ No data in response")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    
    print()
    
    # Test 2: Date range query
    print("🧪 Test 2: Date Range Query (Last 30 days)")
    print("-" * 50)
    
    try:
        response = requests.get(
            f"{base_url}/doctor/patient/{patient_id}/ai-summary",
            params={"days": 30},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Request successful!")
            
            if 'data' in data:
                patient_data = data['data']
                print(f"📊 Date Range: {patient_data.get('date_range_days', 'N/A')} days")
                
                # Check RAG enhancement
                ai_summary = patient_data.get('ai_summary', '')
                if 'RAG' in ai_summary or 'medical context' in ai_summary.lower():
                    print("🧠 RAG Enhancement: DETECTED")
                else:
                    print("🤖 AI Mode: Basic")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()
    
    # Test 3: Custom date range
    print("🧪 Test 3: Custom Date Range Query")
    print("-" * 50)
    
    try:
        response = requests.get(
            f"{base_url}/doctor/patient/{patient_id}/ai-summary",
            params={
                "start_date": "2025-10-01",
                "end_date": "2025-10-22"
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Request successful!")
            
            if 'data' in data:
                patient_data = data['data']
                date_range = patient_data.get('date_range', {})
                print(f"📊 Date Range: {date_range.get('start_date', 'N/A')} to {date_range.get('end_date', 'N/A')}")
                print(f"   Type: {date_range.get('type', 'N/A')}")
                print(f"   Days: {date_range.get('days', 'N/A')}")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()
    print("=" * 80)
    print("RAG Enhancement Test Complete!")
    print("=" * 80)

def test_rag_system_status():
    """Test RAG system status and knowledge base."""
    
    print("🔍 RAG System Status Check")
    print("-" * 40)
    
    try:
        # Check if RAG initialization was successful
        import os
        if os.path.exists("data/medical_knowledge.json"):
            print("✅ Medical knowledge base file exists")
            
            with open("data/medical_knowledge.json", "r") as f:
                knowledge_data = json.load(f)
                print(f"📚 Knowledge chunks: {len(knowledge_data)}")
                
                # Show knowledge distribution
                type_counts = {}
                for chunk in knowledge_data:
                    chunk_type = chunk.get('metadata', {}).get('type', 'unknown')
                    type_counts[chunk_type] = type_counts.get(chunk_type, 0) + 1
                
                print("📊 Knowledge distribution:")
                for chunk_type, count in type_counts.items():
                    print(f"   - {chunk_type}: {count} chunks")
        else:
            print("❌ Medical knowledge base file not found")
        
        if os.path.exists("data/vector_db/embeddings.pkl"):
            print("✅ Vector database embeddings exist")
        else:
            print("❌ Vector database embeddings not found")
            
        if os.path.exists("data/vector_db/chunks.json"):
            print("✅ Vector database chunks exist")
        else:
            print("❌ Vector database chunks not found")
            
    except Exception as e:
        print(f"❌ Error checking RAG system: {str(e)}")

if __name__ == "__main__":
    print("Starting RAG Enhancement Tests...")
    print()
    
    # Check RAG system status
    test_rag_system_status()
    print()
    
    # Test the enhanced endpoint
    test_rag_enhanced_summary()
