from flask import jsonify


class DictationController:
	def __init__(self, dictation_model, jwt_service, validators):
		self.dictation_model = dictation_model
		self.jwt_service = jwt_service
		self.validators = validators

	def _get_bearer_token(self, request):
		auth = request.headers.get('Authorization', '')
		if auth and auth.lower().startswith('bearer '):
			return auth.split(' ', 1)[1].strip()
		return None

	def _get_doctor_like(self, claims: dict):
		return claims.get("doctor_id") or claims.get("user_id") or claims.get("patient_id") or claims.get("sub")

	def _decode_claims(self, token: str):
		# Use the existing JWTService API: verify_access_token returns { success, data }
		resp = self.jwt_service.verify_access_token(token)
		if not isinstance(resp, dict) or not resp.get('success'):
			raise ValueError("Invalid or expired token")
		return resp.get('data') or {}

	def create_dictation(self, request, patient_id: str):
		try:
			if not patient_id or not str(patient_id).strip():
				return jsonify({"success": False, "message": "patient_id is required"}), 400

			token = self._get_bearer_token(request)
			if not token:
				return jsonify({"success": False, "message": "Missing Bearer token"}), 401

			claims = self._decode_claims(token)
			doctor_like = self._get_doctor_like(claims)  # optional

			data = request.get_json(silent=True) or {}
			language = (data.get("language") or "").strip()
			text = (data.get("text") or "").strip()
			if not language or not text:
				return jsonify({"success": False, "message": "language and text are required"}), 400

			saved = self.dictation_model.create(
				patient_id=patient_id.strip(),
				language=language,
				text=text,
				doctor_id=str(doctor_like).strip() if doctor_like else None
			)
			return jsonify({"success": True, "dictation": saved, "message": "Dictation saved"}), 201

		except ValueError as ve:
			return jsonify({"success": False, "message": str(ve)}), 401
		except Exception as e:
			return jsonify({"success": False, "message": f"Failed to save dictation: {str(e)}"}), 500

	def _parse_iso(self, s):
		from datetime import datetime
		try:
			return datetime.fromisoformat(s) if s else None
		except:
			return None

	def list_for_doctor(self, request, patient_id: str):
		try:
			if not patient_id or not str(patient_id).strip():
				return jsonify({"success": False, "message": "patient_id is required"}), 400

			token = self._get_bearer_token(request)
			if not token:
				return jsonify({"success": False, "message": "Missing Bearer token"}), 401

			claims = self._decode_claims(token)
			role = (claims.get("role") or "").lower()
			if role != "doctor":
				return jsonify({"success": False, "message": "Doctor role required"}), 403

			args = request.args or {}
			result = self.dictation_model.list(
				patient_id=patient_id,
				language=(args.get("language") or "").strip() or None,
				ts_from=self._parse_iso(args.get("from")),
				ts_to=self._parse_iso(args.get("to")),
				limit=int(args.get("limit", 20)),
				offset=int(args.get("offset", 0)),
			)
			return jsonify({"success": True, "data": result}), 200

		except ValueError as ve:
			return jsonify({"success": False, "message": str(ve)}), 401
		except Exception as e:
			return jsonify({"success": False, "message": f"Failed to fetch dictations: {str(e)}"}), 500

	def list_for_patient(self, request, patient_id: str):
		try:
			if not patient_id or not str(patient_id).strip():
				return jsonify({"success": False, "message": "patient_id is required"}), 400

			token = self._get_bearer_token(request)
			if not token:
				return jsonify({"success": False, "message": "Missing Bearer token"}), 401

			claims = self._decode_claims(token)
			role = (claims.get("role") or "").lower()
			user_id = claims.get("user_id")

			if not ((role == "patient" and user_id == patient_id) or role == "doctor"):
				return jsonify({"success": False, "message": "Not permitted"}), 403

			# For doctor role, get doctor_id; for patient role, we need to find their doctor
			doctor_id = None
			if role == "doctor":
				doctor_id = self._get_doctor_like(claims)
				if not doctor_id:
					return jsonify({"success": False, "message": "Doctor ID is required for dictation retrieval"}), 400
			else:
				# For patient view, we need to find their assigned doctor
				# Get patient's doctor_id from the patient document
				try:
					# Access the database through the dictation model
					patients_collection = self.dictation_model.doctors_collection.database['Patient_test']
					patient_doc = patients_collection.find_one({"patient_id": patient_id})
					
					if not patient_doc:
						return jsonify({"success": False, "message": "Patient not found"}), 404
					
					# Get the doctor_id from patient document
					doctor_id = patient_doc.get('doctor_id')
					print(f"🔍 Patient {patient_id} doctor_id: {doctor_id}")
					
					if not doctor_id:
						# If no doctor_id in patient document, try to get from any doctor's dictations
						# This is a fallback - look for any doctor who has dictations for this patient
						doctors_collection = self.dictation_model.doctors_collection
						doctors = list(doctors_collection.find({"dictations.patient_id": patient_id}))
						
						if doctors:
							doctor_id = doctors[0].get('doctor_id')
							print(f"🔍 Found doctor from dictations: {doctor_id}")
						else:
							return jsonify({"success": False, "message": "No assigned doctor found for this patient"}), 404
						
				except Exception as e:
					print(f"❌ Error finding patient's doctor: {str(e)}")
					return jsonify({"success": False, "message": f"Failed to find patient's doctor: {str(e)}"}), 500

			# Safety check - ensure doctor_id is not None
			if not doctor_id:
				return jsonify({"success": False, "message": "Doctor ID is required but not found"}), 400
			
			print(f"🔍 Using doctor_id: {doctor_id} for patient: {patient_id}")

			args = request.args or {}
			result = self.dictation_model.list(
				patient_id=patient_id,
				doctor_id=str(doctor_id).strip(),
				language=(args.get("language") or "").strip() or None,
				ts_from=self._parse_iso(args.get("from")),
				ts_to=self._parse_iso(args.get("to")),
				limit=int(args.get("limit", 20)),
				offset=int(args.get("offset", 0)),
			)

			if role == "patient":
				for d in result["items"]:
					d.pop("doctor_id", None)

			return jsonify({"success": True, "data": result}), 200

		except ValueError as ve:
			return jsonify({"success": False, "message": str(ve)}), 401
		except Exception as e:
			return jsonify({"success": False, "message": f"Failed to fetch dictations: {str(e)}"}), 500


