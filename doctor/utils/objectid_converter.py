"""
ObjectId Converter Utility

This utility handles conversion of MongoDB ObjectId objects to strings
for JSON serialization, including nested objects and arrays.
"""

from bson import ObjectId
from datetime import datetime, date
import json


def convert_objectid_to_string(obj):
    """
    Recursively convert ObjectId objects to strings in nested data structures.
    
    Args:
        obj: The object to convert (dict, list, or any other type)
    
    Returns:
        The converted object with ObjectIds as strings
    """
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_objectid_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_string(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_objectid_to_string(item) for item in obj)
    else:
        return obj


def json_safe_serialize(obj):
    """
    Safely serialize an object to JSON, converting ObjectIds and other
    non-JSON-serializable objects.
    
    Args:
        obj: The object to serialize
    
    Returns:
        JSON-safe object ready for json.dumps()
    """
    return convert_objectid_to_string(obj)


def test_objectid_conversion():
    """Test the ObjectId conversion utility."""
    from bson import ObjectId
    from datetime import datetime
    
    # Test data with various ObjectId scenarios
    test_data = {
        '_id': ObjectId(),
        'patient_id': 'PAT123456789',
        'name': 'Test Patient',
        'appointments': [
            {
                'appointment_id': ObjectId(),
                'date': datetime.now(),
                'status': 'scheduled'
            },
            {
                'appointment_id': ObjectId(),
                'date': datetime.now(),
                'status': 'completed'
            }
        ],
        'medications': [
            {
                'medication_id': ObjectId(),
                'name': 'Aspirin',
                'prescribed_date': datetime.now()
            }
        ],
        'nested_object': {
            'inner_id': ObjectId(),
            'inner_date': datetime.now(),
            'inner_array': [
                ObjectId(),
                ObjectId(),
                'regular_string'
            ]
        },
        'created_at': datetime.now(),
        'regular_string': 'This should remain unchanged',
        'regular_number': 123,
        'regular_bool': True
    }
    
    print("Original data types:")
    print(f"_id type: {type(test_data['_id'])}")
    print(f"appointments[0]['appointment_id'] type: {type(test_data['appointments'][0]['appointment_id'])}")
    print(f"nested_object['inner_id'] type: {type(test_data['nested_object']['inner_id'])}")
    print(f"nested_object['inner_array'][0] type: {type(test_data['nested_object']['inner_array'][0])}")
    print(f"created_at type: {type(test_data['created_at'])}")
    
    # Convert the data
    converted_data = convert_objectid_to_string(test_data)
    
    print("\nConverted data types:")
    print(f"_id type: {type(converted_data['_id'])}")
    print(f"appointments[0]['appointment_id'] type: {type(converted_data['appointments'][0]['appointment_id'])}")
    print(f"nested_object['inner_id'] type: {type(converted_data['nested_object']['inner_id'])}")
    print(f"nested_object['inner_array'][0] type: {type(converted_data['nested_object']['inner_array'][0])}")
    print(f"created_at type: {type(converted_data['created_at'])}")
    
    # Test JSON serialization
    try:
        json_str = json.dumps(converted_data)
        print(f"\n✅ JSON serialization successful! Length: {len(json_str)} characters")
        return True
    except Exception as e:
        print(f"\n❌ JSON serialization failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing ObjectId conversion utility...")
    test_objectid_conversion()
