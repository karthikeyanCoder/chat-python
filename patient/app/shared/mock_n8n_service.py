"""
Mock N8N Service for testing webhook integration
"""
from datetime import datetime


class MockN8NService:
    """Mock N8N service for testing webhook integration"""
    
    def process_prescription_webhook(self, webhook_data):
        """Simulate N8N workflow processing"""
        try:
            # Extract key information from webhook data
            patient_id = webhook_data.get('patient_id', 'unknown')
            medication_name = webhook_data.get('medication_name', 'unknown')
            extracted_text = webhook_data.get('extracted_text', '')
            filename = webhook_data.get('filename', 'unknown')
            
            # Simulate AI processing of prescription text
            processed_result = self._simulate_ai_processing(extracted_text)
            
            # Return structured N8N response
            return {
                'success': True,
                'message': 'Prescription processed by Mock N8N workflow',
                'workflow_id': 'mock_prescription_processor_001',
                'processing_time': '1.2s',
                'patient_id': patient_id,
                'filename': filename,
                'extracted_fields': processed_result['extracted_fields'],
                'confidence_score': processed_result['confidence'],
                'recommendations': processed_result['recommendations'],
                'ai_analysis': processed_result['ai_analysis'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Mock N8N processing failed: {str(e)}',
                'step': 'mock_processing_error'
            }
    
    def _simulate_ai_processing(self, text):
        """Simulate AI extraction of prescription fields"""
        text_lower = text.lower()
        
        # Extract medication information using pattern matching
        extracted_fields = {}
        
        # Medication name patterns
        if 'amoxicillin' in text_lower:
            extracted_fields['medication_name'] = 'Amoxicillin'
            extracted_fields['dosage'] = '500mg'
            extracted_fields['frequency'] = 'Three times daily'
            extracted_fields['duration'] = '7 days'
        elif 'paracetamol' in text_lower:
            extracted_fields['medication_name'] = 'Paracetamol'
            extracted_fields['dosage'] = '500mg'
            extracted_fields['frequency'] = 'Every 4-6 hours'
            extracted_fields['duration'] = 'As needed'
        elif 'vitamin' in text_lower:
            extracted_fields['medication_name'] = 'Vitamin Supplement'
            extracted_fields['dosage'] = '1 tablet'
            extracted_fields['frequency'] = 'Once daily'
            extracted_fields['duration'] = 'Ongoing'
        else:
            extracted_fields['medication_name'] = 'Unknown Medication'
            extracted_fields['dosage'] = 'As prescribed'
            extracted_fields['frequency'] = 'As prescribed'
            extracted_fields['duration'] = 'As prescribed'
        
        # Extract doctor information
        if 'dr.' in text_lower or 'doctor' in text_lower:
            extracted_fields['prescribed_by'] = 'Dr. Smith'
        else:
            extracted_fields['prescribed_by'] = 'Unknown'
        
        # Extract patient information
        if 'patient:' in text_lower:
            extracted_fields['patient_name'] = 'Jane Doe'
        
        # Generate AI analysis
        ai_analysis = {
            'text_complexity': 'medium',
            'extraction_confidence': 0.85,
            'key_phrases_found': len(extracted_fields),
            'processing_notes': 'Successfully extracted prescription details using pattern matching'
        }
        
        # Generate recommendations
        recommendations = [
            'Take medication as prescribed by your doctor',
            'Complete the full course of treatment',
            'Store in a cool, dry place',
            'Contact your doctor if you experience side effects'
        ]
        
        return {
            'extracted_fields': extracted_fields,
            'confidence': 0.85,
            'recommendations': recommendations,
            'ai_analysis': ai_analysis
        }


# Global mock N8N service instance - import this for use across the app
mock_n8n_service = MockN8NService()

