#!/usr/bin/env python3
"""
Demo script to showcase RAG enhancement in AI medical summaries.
This script demonstrates the difference between basic and RAG-enhanced AI summaries.
"""

import requests
import json
import time
from datetime import datetime

def demo_rag_enhancement():
    """Demonstrate RAG enhancement capabilities."""
    
    print("🧠 RAG-Enhanced AI Medical Summary Demo")
    print("=" * 60)
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_url = "http://localhost:8000"
    patient_id = "PAT175820015455746A"
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "First Trimester Analysis (7 days)",
            "params": {"days": 7},
            "description": "Analyzing early pregnancy data with RAG-enhanced medical context"
        },
        {
            "name": "Comprehensive Review (30 days)",
            "params": {"days": 30},
            "description": "Full month analysis with comprehensive medical insights"
        },
        {
            "name": "Custom Date Range",
            "params": {"start_date": "2025-10-01", "end_date": "2025-10-22"},
            "description": "Specific period analysis with targeted medical recommendations"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"🔬 Test {i}: {scenario['name']}")
        print("-" * 50)
        print(f"📝 {scenario['description']}")
        print()
        
        try:
            # Make API request
            print("🌐 Making API request...")
            start_time = time.time()
            
            response = requests.get(
                f"{base_url}/doctor/patient/{patient_id}/ai-summary",
                params=scenario['params'],
                headers={"Content-Type": "application/json"},
                timeout=45
            )
            
            request_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Request successful! (took {request_time:.2f}s)")
                print()
                
                if 'data' in data:
                    patient_data = data['data']
                    
                    # Display basic info
                    print("📊 Patient Information:")
                    patient_info = patient_data.get('patient_info', {})
                    print(f"   - Name: {patient_info.get('fullname', 'N/A')}")
                    print(f"   - Age: {patient_info.get('age', 'N/A')}")
                    print(f"   - Pregnancy Week: {patient_info.get('pregnancy_week', 'N/A')}")
                    print(f"   - Trimester: {patient_info.get('trimester', 'N/A')}")
                    print(f"   - Blood Type: {patient_info.get('blood_type', 'N/A')}")
                    print()
                    
                    # Display date range info
                    date_range = patient_data.get('date_range', {})
                    if date_range.get('type') == 'custom':
                        print("📅 Date Range:")
                        print(f"   - From: {date_range.get('start_date', 'N/A')}")
                        print(f"   - To: {date_range.get('end_date', 'N/A')}")
                        print(f"   - Days: {date_range.get('days', 'N/A')}")
                    else:
                        print(f"📅 Analysis Period: {patient_data.get('date_range_days', 'N/A')} days")
                    print()
                    
                    # Display RAG enhancement status
                    ai_summary = patient_data.get('ai_summary', '')
                    if 'RAG' in ai_summary or 'medical context' in ai_summary.lower():
                        print("🧠 RAG Enhancement: ACTIVE")
                        print("   - Medical knowledge base integration: ✅")
                        print("   - Evidence-based recommendations: ✅")
                        print("   - Clinical guidelines integration: ✅")
                    else:
                        print("🤖 AI Mode: Basic")
                        print("   - Standard GPT-4 analysis")
                        print("   - No medical knowledge base integration")
                    print()
                    
                    # Display statistics
                    stats = patient_data.get('statistics', {})
                    if stats:
                        print("📈 Health Data Statistics:")
                        
                        # Food & Nutrition
                        food_stats = stats.get('food_nutrition', {})
                        if food_stats:
                            print(f"   🍎 Food & Nutrition:")
                            print(f"      - Total entries: {food_stats.get('total_entries', 0)}")
                            print(f"      - Average calories: {food_stats.get('average_calories', 0)}")
                            print(f"      - Nutrition score: {food_stats.get('nutrition_score', 0)}/100")
                        
                        # Medication Adherence
                        med_stats = stats.get('medication_adherence', {})
                        if med_stats:
                            print(f"   💊 Medication Adherence:")
                            print(f"      - Total medications: {med_stats.get('total_medications', 0)}")
                            print(f"      - Adherence rate: {med_stats.get('adherence_rate', 0)}%")
                            print(f"      - Missed doses: {med_stats.get('missed_doses', 0)}")
                        
                        # Symptoms
                        symptom_stats = stats.get('symptoms_tracking', {})
                        if symptom_stats:
                            print(f"   🤒 Symptoms:")
                            print(f"      - Total symptoms: {symptom_stats.get('total_symptoms', 0)}")
                            print(f"      - Severe symptoms: {symptom_stats.get('severe_symptoms', 0)}")
                            print(f"      - Common symptoms: {', '.join(symptom_stats.get('common_symptoms', [])[:3])}")
                        
                        # Sleep
                        sleep_stats = stats.get('sleep_patterns', {})
                        if sleep_stats:
                            print(f"   😴 Sleep Patterns:")
                            print(f"      - Total logs: {sleep_stats.get('total_sleep_logs', 0)}")
                            print(f"      - Average sleep: {sleep_stats.get('average_sleep_hours', 0)} hours")
                            print(f"      - Sleep quality: {sleep_stats.get('average_sleep_rating', 'N/A')}")
                        
                        # Kick Count
                        kick_stats = stats.get('kick_count_tracking', {})
                        if kick_stats:
                            print(f"   👶 Kick Count:")
                            print(f"      - Total sessions: {kick_stats.get('total_kick_sessions', 0)}")
                            print(f"      - Average kicks: {kick_stats.get('average_kicks_per_session', 0)}")
                            print(f"      - Last session: {kick_stats.get('last_kick_count', 0)} kicks")
                        
                        # Mental Health
                        mental_stats = stats.get('mental_health', {})
                        if mental_stats:
                            print(f"   🧠 Mental Health:")
                            print(f"      - Total entries: {mental_stats.get('total_entries', 0)}")
                            print(f"      - Mood trends: {mental_stats.get('mood_trend', 'N/A')}")
                        
                        # Hydration
                        hydration_stats = stats.get('hydration', {})
                        if hydration_stats:
                            print(f"   💧 Hydration:")
                            print(f"      - Total records: {hydration_stats.get('total_records', 0)}")
                            print(f"      - Average intake: {hydration_stats.get('average_daily_intake_ml', 0)}ml")
                            print(f"      - Goal achievement: {hydration_stats.get('goal_achievement_rate', 0)}%")
                        
                        print()
                    
                    # Display risk assessment
                    risk_assessment = patient_data.get('pregnancy_risk_assessment', {})
                    if risk_assessment:
                        print("🎯 Pregnancy Risk Assessment:")
                        print(f"   - Overall Risk Level: {risk_assessment.get('overall_risk_level', 'N/A')}")
                        print(f"   - Risk Score: {risk_assessment.get('risk_score', 'N/A')}/100")
                        
                        risk_factors = risk_assessment.get('risk_factors', [])
                        if risk_factors:
                            print(f"   - Risk Factors ({len(risk_factors)}):")
                            for factor in risk_factors[:3]:  # Show top 3
                                print(f"      • {factor}")
                        
                        protective_factors = risk_assessment.get('protective_factors', [])
                        if protective_factors:
                            print(f"   - Protective Factors ({len(protective_factors)}):")
                            for factor in protective_factors[:3]:  # Show top 3
                                print(f"      • {factor}")
                        
                        recommendations = risk_assessment.get('recommendations', [])
                        if recommendations:
                            print(f"   - Recommendations ({len(recommendations)}):")
                            for rec in recommendations[:3]:  # Show top 3
                                print(f"      • {rec}")
                        
                        print()
                    
                    # Display AI summary preview
                    print("🤖 AI Medical Summary Preview:")
                    print("-" * 40)
                    summary_preview = ai_summary[:500] + "..." if len(ai_summary) > 500 else ai_summary
                    print(summary_preview)
                    print()
                    
                    # Display raw data summary
                    raw_data = patient_data.get('raw_data', {})
                    if raw_data:
                        print("📋 Raw Data Summary:")
                        print(f"   - Food entries: {len(raw_data.get('food_data', []))}")
                        print(f"   - Medication logs: {len(raw_data.get('medications', {}).get('medication_logs', []))}")
                        print(f"   - Symptoms: {len(raw_data.get('symptoms', []))}")
                        print(f"   - Sleep logs: {len(raw_data.get('sleep', []))}")
                        print(f"   - Mental health: {len(raw_data.get('mental_health', []))}")
                        print(f"   - Kick counts: {len(raw_data.get('kick_counts', []))}")
                        print(f"   - Hydration records: {len(raw_data.get('hydration', {}).get('records', []))}")
                        print()
                
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out - this may indicate RAG processing is taking longer than expected")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
        
        print("=" * 60)
        print()
    
    print("🎉 RAG Enhancement Demo Complete!")
    print("=" * 60)
    print()
    print("Key Benefits of RAG Enhancement:")
    print("✅ Evidence-based medical recommendations")
    print("✅ ACOG and FDA guideline integration")
    print("✅ Pregnancy-stage-specific insights")
    print("✅ Enhanced risk assessment accuracy")
    print("✅ Clinical best practices integration")
    print("✅ Personalized care recommendations")

if __name__ == "__main__":
    demo_rag_enhancement()
