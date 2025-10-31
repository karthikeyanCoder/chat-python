"""
Vital Signs Service - Integrated from FastAPI vital signs module
Provides AI-powered vital signs analysis and monitoring
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

class VitalSignsService:
    def __init__(self, db=None):
        """Initialize the vital signs service"""
        self.db = db
        if self.db is None:
            self._initialize_database()
    
    def _initialize_database(self):
        """Initialize MongoDB connection"""
        try:
            mongo_uri = os.getenv('MONGO_URI')
            if mongo_uri:
                from pymongo import MongoClient
                self.mongo_client = MongoClient(mongo_uri)
                db_name = os.getenv('DB_NAME', 'patients_db')
                self.db = self.mongo_client[db_name]
                print("[OK] Vital Signs Service: MongoDB connected")
            else:
                print("[WARN] Vital Signs Service: MongoDB URI not found")
        except Exception as e:
            print(f"[ERROR] Vital Signs Service: Database connection failed: {e}")
    
    def record_vital_sign(self, patient_id: str, vital_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record a new vital sign for a patient"""
        try:
            if self.db is None:
                return {"success": False, "message": "Database not connected"}
            
            # Prepare vital sign record
            vital_record = {
                "type": vital_data.get('type'),
                "value": vital_data.get('value'),
                "secondary_value": vital_data.get('secondary_value'),
                "timestamp": datetime.now(),
                "notes": vital_data.get('notes', ''),
                "is_anomaly": False,
                "confidence": None,
                "created_at": datetime.now()
            }
            
            # Add to patient's vital_signs_logs array
            result = self.db.patients_collection.update_one(
                {"patient_id": patient_id},
                {"$push": {"vital_signs_logs": vital_record}},
                upsert=True
            )
            
            if result.acknowledged:
                # Check for anomalies and create alerts if needed
                self._check_for_alerts(patient_id, vital_record)
                
                return {
                    "success": True,
                    "message": "Vital sign recorded successfully",
                    "vital_sign": vital_record
                }
            else:
                return {"success": False, "message": "Failed to record vital sign"}
                
        except Exception as e:
            logger.error(f"Error recording vital sign: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_vital_signs_history(self, patient_id: str, days: int = 30) -> Dict[str, Any]:
        """Get vital signs history for a patient"""
        try:
            if self.db is None:
                return {"success": False, "message": "Database not connected"}
            
            # Find patient
            patient = self.db.patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return {"success": False, "message": "Patient not found"}
            
            # Get vital signs logs
            vital_signs_logs = patient.get('vital_signs_logs', [])
            
            # Filter by date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            filtered_logs = [
                log for log in vital_signs_logs
                if log.get('timestamp', datetime.now()) >= start_date
            ]
            
            # Sort by timestamp (newest first)
            filtered_logs.sort(key=lambda x: x.get('timestamp', datetime.now()), reverse=True)
            
            return {
                "success": True,
                "patient_id": patient_id,
                "vital_signs": filtered_logs,
                "total_count": len(filtered_logs),
                "date_range_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting vital signs history: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def analyze_vital_signs(self, patient_id: str, days: int = 7) -> Dict[str, Any]:
        """Analyze vital signs for anomalies and trends"""
        try:
            if self.db is None:
                return {"success": False, "message": "Database not connected"}
            
            # Get recent vital signs
            history_result = self.get_vital_signs_history(patient_id, days)
            if not history_result["success"]:
                return history_result
            
            vital_signs = history_result["vital_signs"]
            
            if not vital_signs:
                return {
                    "success": True,
                    "message": "No vital signs data for analysis",
                    "analysis": {
                        "anomalies": [],
                        "trends": [],
                        "early_warning_score": None,
                        "health_status": "no_data"
                    }
                }
            
            # Analyze for anomalies
            anomalies = self._detect_anomalies(vital_signs)
            
            # Analyze trends
            trends = self._analyze_trends(vital_signs)
            
            # Calculate early warning score
            ews = self._calculate_early_warning_score(vital_signs)
            
            # Determine overall health status
            health_status = self._determine_health_status(anomalies, ews)
            
            return {
                "success": True,
                "patient_id": patient_id,
                "analysis": {
                    "anomalies": anomalies,
                    "trends": trends,
                    "early_warning_score": ews,
                    "health_status": health_status,
                    "total_vital_signs": len(vital_signs),
                    "analysis_period_days": days
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing vital signs: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_health_summary(self, patient_id: str) -> Dict[str, Any]:
        """Get comprehensive health summary for a patient"""
        try:
            if self.db is None:
                return {"success": False, "message": "Database not connected"}
            
            # Find patient
            patient = self.db.patients_collection.find_one({"patient_id": patient_id})
            if not patient:
                return {"success": False, "message": "Patient not found"}
            
            # Get recent vital signs (last 24 hours)
            vital_signs_logs = patient.get('vital_signs_logs', [])
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=24)
            
            recent_vitals = [
                log for log in vital_signs_logs
                if log.get('timestamp', datetime.now()) >= start_date
            ]
            
            # Get alerts
            alerts = patient.get('vital_signs_alerts', [])
            critical_alerts = len([a for a in alerts if a.get('severity') == 'critical' and not a.get('is_resolved', False)])
            warning_alerts = len([a for a in alerts if a.get('severity') in ['high', 'medium'] and not a.get('is_resolved', False)])
            
            # Analyze recent data
            analysis_result = self.analyze_vital_signs(patient_id, 1)
            analysis = analysis_result.get('analysis', {}) if analysis_result['success'] else {}
            
            # Determine overall status
            if critical_alerts > 0 or analysis.get('early_warning_score', {}).get('risk_level') == 'critical':
                overall_status = 'critical'
            elif warning_alerts > 0 or analysis.get('early_warning_score', {}).get('risk_level') == 'high':
                overall_status = 'warning'
            elif analysis.get('health_status') == 'caution':
                overall_status = 'caution'
            else:
                overall_status = 'normal'
            
            return {
                "success": True,
                "patient_id": patient_id,
                "health_summary": {
                    "overall_status": overall_status,
                    "critical_alerts": critical_alerts,
                    "warning_alerts": warning_alerts,
                    "recent_vital_signs_count": len(recent_vitals),
                    "analysis": analysis,
                    "last_updated": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting health summary: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def _detect_anomalies(self, vital_signs: List[Dict]) -> List[Dict]:
        """Detect anomalies in vital signs using statistical methods"""
        anomalies = []
        
        # Group by type
        by_type = {}
        for vs in vital_signs:
            vs_type = vs.get('type')
            if vs_type not in by_type:
                by_type[vs_type] = []
            by_type[vs_type].append(vs)
        
        for vs_type, signs in by_type.items():
            if len(signs) < 3:  # Need at least 3 data points
                continue
                
            values = [vs.get('value', 0) for vs in signs]
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            for vs in signs:
                value = vs.get('value', 0)
                z_score = abs((value - mean_val) / std_val) if std_val > 0 else 0
                
                if z_score > 2.0:  # 2 standard deviations threshold
                    anomaly = {
                        "type": vs_type,
                        "is_anomaly": True,
                        "confidence": min(z_score / 2.0, 1.0),
                        "reason": f"Value {value} is {z_score:.2f} standard deviations from mean",
                        "suggested_action": self._get_anomaly_action(vs_type, value, mean_val),
                        "timestamp": vs.get('timestamp')
                    }
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _analyze_trends(self, vital_signs: List[Dict]) -> List[Dict]:
        """Analyze trends in vital signs"""
        trends = []
        
        # Group by type
        by_type = {}
        for vs in vital_signs:
            vs_type = vs.get('type')
            if vs_type not in by_type:
                by_type[vs_type] = []
            by_type[vs_type].append(vs)
        
        for vs_type, signs in by_type.items():
            if len(signs) < 2:
                continue
                
            # Sort by timestamp
            signs.sort(key=lambda x: x.get('timestamp', datetime.now()))
            
            values = [vs.get('value', 0) for vs in signs]
            if len(values) < 2:
                continue
                
            # Calculate trend
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            first_avg = np.mean(first_half)
            second_avg = np.mean(second_half)
            
            change_percentage = ((second_avg - first_avg) / first_avg * 100) if first_avg != 0 else 0
            
            if abs(change_percentage) < 5:
                trend = "stable"
            elif change_percentage > 0:
                trend = "increasing"
            else:
                trend = "decreasing"
            
            trend_data = {
                "type": vs_type,
                "trend": trend,
                "change_percentage": round(change_percentage, 2),
                "confidence": min(abs(change_percentage) / 10, 1.0),
                "period_days": (signs[-1].get('timestamp', datetime.now()) - signs[0].get('timestamp', datetime.now())).days
            }
            trends.append(trend_data)
        
        return trends
    
    def _calculate_early_warning_score(self, vital_signs: List[Dict]) -> Dict[str, Any]:
        """Calculate Early Warning Score based on recent vital signs"""
        if not vital_signs:
            return None
        
        # Get latest values for each vital sign type
        latest_values = {}
        for vs in vital_signs:
            vs_type = vs.get('type')
            if vs_type not in latest_values or vs.get('timestamp', datetime.now()) > latest_values[vs_type].get('timestamp', datetime.min):
                latest_values[vs_type] = vs
        
        score = 0
        factors = []
        
        # Heart Rate scoring
        if 'heartRate' in latest_values:
            hr = latest_values['heartRate'].get('value', 0)
            if hr < 40 or hr > 130:
                score += 3
                factors.append(f"Heart rate {hr} BPM (abnormal)")
            elif hr < 50 or hr > 110:
                score += 2
                factors.append(f"Heart rate {hr} BPM (elevated)")
            elif hr < 60 or hr > 100:
                score += 1
                factors.append(f"Heart rate {hr} BPM (slightly elevated)")
        
        # Blood Pressure scoring
        if 'bloodPressure' in latest_values:
            bp = latest_values['bloodPressure'].get('value', 0)
            if bp < 90 or bp > 180:
                score += 3
                factors.append(f"Blood pressure {bp} mmHg (abnormal)")
            elif bp < 100 or bp > 160:
                score += 2
                factors.append(f"Blood pressure {bp} mmHg (elevated)")
            elif bp < 110 or bp > 140:
                score += 1
                factors.append(f"Blood pressure {bp} mmHg (slightly elevated)")
        
        # Temperature scoring
        if 'temperature' in latest_values:
            temp = latest_values['temperature'].get('value', 0)
            if temp < 35 or temp > 39:
                score += 3
                factors.append(f"Temperature {temp}°C (abnormal)")
            elif temp < 36 or temp > 38:
                score += 2
                factors.append(f"Temperature {temp}°C (elevated)")
            elif temp < 36.5 or temp > 37.5:
                score += 1
                factors.append(f"Temperature {temp}°C (slightly elevated)")
        
        # Determine risk level
        if score >= 7:
            risk_level = "critical"
        elif score >= 4:
            risk_level = "high"
        elif score >= 2:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Generate recommendations
        recommendations = []
        if risk_level == "critical":
            recommendations.append("Seek immediate medical attention")
        elif risk_level == "high":
            recommendations.append("Contact healthcare provider urgently")
        elif risk_level == "medium":
            recommendations.append("Monitor closely and consider contacting healthcare provider")
        else:
            recommendations.append("Continue regular monitoring")
        
        return {
            "score": score,
            "risk_level": risk_level,
            "factors": factors,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    def _determine_health_status(self, anomalies: List[Dict], ews: Dict[str, Any]) -> str:
        """Determine overall health status based on analysis"""
        if not ews:
            return "no_data"
        
        risk_level = ews.get('risk_level', 'low')
        anomaly_count = len([a for a in anomalies if a.get('is_anomaly', False)])
        
        if risk_level == "critical" or anomaly_count > 3:
            return "critical"
        elif risk_level == "high" or anomaly_count > 1:
            return "warning"
        elif risk_level == "medium" or anomaly_count > 0:
            return "caution"
        else:
            return "normal"
    
    def _get_anomaly_action(self, vs_type: str, value: float, mean: float) -> str:
        """Get suggested action for anomaly"""
        if vs_type == "heartRate":
            if value > mean:
                return "Monitor heart rate closely, consider rest"
            else:
                return "Check for signs of fatigue or dehydration"
        elif vs_type == "bloodPressure":
            if value > mean:
                return "Monitor blood pressure, consider relaxation techniques"
            else:
                return "Check for signs of dizziness or weakness"
        elif vs_type == "temperature":
            if value > mean:
                return "Monitor temperature, consider fever management"
            else:
                return "Check for signs of hypothermia"
        else:
            return "Monitor closely and contact healthcare provider if symptoms worsen"
    
    def _check_for_alerts(self, patient_id: str, vital_record: Dict[str, Any]):
        """Check if vital sign requires an alert and create one if needed"""
        try:
            vs_type = vital_record.get('type')
            value = vital_record.get('value', 0)
            
            # Define alert thresholds
            thresholds = {
                'heartRate': {'low': 50, 'high': 100},
                'bloodPressure': {'low': 90, 'high': 140},
                'temperature': {'low': 36.0, 'high': 37.5},
                'spO2': {'low': 95, 'high': 100},
                'respiratoryRate': {'low': 12, 'high': 20}
            }
            
            if vs_type not in thresholds:
                return
            
            threshold = thresholds[vs_type]
            severity = None
            message = ""
            
            if value < threshold['low']:
                severity = 'high'
                message = f"{vs_type} is below normal range ({value})"
            elif value > threshold['high']:
                severity = 'high'
                message = f"{vs_type} is above normal range ({value})"
            
            if severity:
                alert = {
                    "type": vs_type,
                    "severity": severity,
                    "message": message,
                    "timestamp": datetime.now(),
                    "action_required": "Monitor closely",
                    "is_resolved": False,
                    "created_at": datetime.now()
                }
                
                # Add alert to patient's vital_signs_alerts array
                self.db.patients_collection.update_one(
                    {"patient_id": patient_id},
                    {"$push": {"vital_signs_alerts": alert}}
                )
                
        except Exception as e:
            logger.error(f"Error creating alert: {e}")

# Global instance
vital_signs_service = VitalSignsService()
