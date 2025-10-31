from datetime import datetime
import uuid


class DictationModel:
	def __init__(self, db):
		self.db = db
		# Now using doctors_collection instead of separate patient_dictations collection
		self.doctors_collection = db.doctors_collection

	def create(self, *, patient_id: str, language: str, text: str, doctor_id: str = None):
		if not patient_id or not language or not text:
			raise ValueError("patient_id, language, and text are required")
		
		if not doctor_id:
			raise ValueError("doctor_id is required for storing dictations in doctor document")

		# Generate unique dictation ID
		dictation_id = f"dict_{int(datetime.utcnow().timestamp() * 1000)}"
		
		# Create dictation object
		dictation = {
			"dictation_id": dictation_id,
			"patient_id": patient_id.strip(),
			"language": language.strip(),
			"text": text.strip(),
			"source": "doctor_dictation",
			"created_at": datetime.utcnow(),
			"updated_at": datetime.utcnow(),
		}
		
		# Add dictation to doctor's document
		result = self.doctors_collection.update_one(
			{"doctor_id": doctor_id.strip()},
			{
				"$push": {"dictations": dictation},
				"$set": {"last_dictation_at": datetime.utcnow()}
			}
		)
		
		if result.matched_count == 0:
			raise ValueError(f"Doctor with ID {doctor_id} not found")
		
		if result.modified_count == 0:
			raise ValueError("Failed to add dictation to doctor document")
		
		return dictation

	def list(self, *, patient_id: str, doctor_id: str, language=None, ts_from=None, ts_to=None, limit: int = 20, offset: int = 0):
		if not patient_id or not str(patient_id).strip():
			raise ValueError("patient_id is required")
		
		if not doctor_id:
			raise ValueError("doctor_id is required for retrieving dictations from doctor document")

		# Get doctor's document
		doctor_doc = self.doctors_collection.find_one({"doctor_id": doctor_id.strip()})
		
		if not doctor_doc:
			return {"items": [], "count": 0}
		
		# Get dictations array from doctor document
		dictations = doctor_doc.get("dictations", [])
		
		# Filter dictations by patient_id
		filtered_dictations = [d for d in dictations if d.get("patient_id") == patient_id.strip()]
		
		# Apply additional filters
		if language:
			filtered_dictations = [d for d in filtered_dictations if d.get("language") == language.strip()]
		
		if ts_from:
			filtered_dictations = [d for d in filtered_dictations if d.get("created_at") >= ts_from]
		
		if ts_to:
			filtered_dictations = [d for d in filtered_dictations if d.get("created_at") <= ts_to]
		
		# Sort by created_at (newest first)
		filtered_dictations.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
		
		# Apply pagination
		total_count = len(filtered_dictations)
		items = filtered_dictations[offset:offset + limit]
		
		return {"items": items, "count": total_count}
	
	def get_doctor_dictations_count(self, doctor_id: str):
		"""Get total count of dictations for a doctor"""
		doctor_doc = self.doctors_collection.find_one({"doctor_id": doctor_id.strip()})
		if not doctor_doc:
			return 0
		
		dictations = doctor_doc.get("dictations", [])
		return len(dictations)
	
	def get_patient_dictations_count(self, patient_id: str, doctor_id: str):
		"""Get count of dictations for a specific patient by a specific doctor"""
		doctor_doc = self.doctors_collection.find_one({"doctor_id": doctor_id.strip()})
		if not doctor_doc:
			return 0
		
		dictations = doctor_doc.get("dictations", [])
		filtered_dictations = [d for d in dictations if d.get("patient_id") == patient_id.strip()]
		return len(filtered_dictations)


