"""
Database connection module for Doctor application
"""
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
import os
import logging
from app.core.config import MONGO_URI, DB_NAME, PATIENTS_COLLECTION, DOCTORS_COLLECTION

logger = logging.getLogger(__name__)


class Database:
    """Database connection and operations"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.patients_collection = None
        self.doctors_collection = None
        self.temp_otp_collection = None
        self._is_connected = False
        self._connect()
    
    def _connect(self, max_retries=3):
        """Connect to MongoDB with retry logic"""
        for attempt in range(max_retries):
            try:
                logger.info(f"MongoDB connection attempt {attempt + 1}/{max_retries}")
                
                # Create MongoDB client with optimized connection pool settings
                # This reduces background connection errors by adjusting heartbeat and timeout settings
                self.client = MongoClient(
                    MONGO_URI,
                    serverSelectionTimeoutMS=30000,
                    connectTimeoutMS=30000,
                    socketTimeoutMS=30000,
                    retryWrites=True,
                    retryReads=True,
                    maxPoolSize=10,
                    minPoolSize=1,
                    heartbeatFrequencyMS=30000,     # Less frequent heartbeats
                    maxIdleTimeMS=300000,           # 5 minutes idle timeout
                    waitQueueTimeoutMS=60000
                )
                
                # Suppress background periodic task connection errors
                pymongo_logger = logging.getLogger('pymongo')
                pymongo_logger.setLevel(logging.WARNING)
                
                # Test connection
                self.client.admin.command('ping')
                logger.info("MongoDB connection test successful")
                
                # Get database
                self.db = self.client[DB_NAME]
                logger.info(f"Database '{DB_NAME}' accessed successfully")
                
                # Initialize collections
                self._initialize_collections()
                
                # Create indexes
                self._create_indexes()
                
                self._is_connected = True
                logger.info("Connected to MongoDB successfully")
                return True
                
            except Exception as e:
                logger.error(f"MongoDB connection failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    logger.info("Waiting 5 seconds before retry...")
                    import time
                    time.sleep(5)
                else:
                    self._is_connected = False
                    logger.error("Failed to connect to MongoDB after all retries")
                    return False
    
    def _initialize_collections(self):
        """Initialize database collections"""
        try:
            self.patients_collection = self.db[PATIENTS_COLLECTION]
            self.doctors_collection = self.db[DOCTORS_COLLECTION]
            self.temp_otp_collection = self.db['temp_otp']
            
            logger.info(f"Collections initialized: {PATIENTS_COLLECTION}, {DOCTORS_COLLECTION}, temp_otp")
        except Exception as e:
            logger.error(f"Collection initialization failed: {e}")
            raise
    
    def _create_indexes(self):
        """Create database indexes"""
        try:
            # Patient indexes
            if self.patients_collection is not None:
                try:
                    # Use sparse=True to match existing index and handle null values
                    self.patients_collection.create_index("patient_id", unique=True, sparse=True)
                    self.patients_collection.create_index("email", unique=True, sparse=True)
                    self.patients_collection.create_index("doctor_id")
                    logger.info("Patient indexes created")
                except Exception as e:
                    error_msg = str(e)
                    # Check if it's just a conflict with existing index (which is acceptable)
                    if 'IndexKeySpecsConflict' in error_msg or 'already exists' in error_msg.lower():
                        logger.info("Patient indexes already exist with compatible settings")
                    else:
                        logger.warning(f"Patient indexes may already exist: {e}")
            
            # Doctor indexes
            if self.doctors_collection is not None:
                try:
                    self.doctors_collection.create_index("doctor_id", unique=True)
                    self.doctors_collection.create_index("email", unique=True, sparse=True)
                    logger.info("Doctor indexes created")
                except Exception as e:
                    logger.warning(f"Doctor indexes may already exist: {e}")
            
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        if not self._is_connected or not self.client:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except:
            return False
    
    def reconnect(self) -> bool:
        """Force database reconnection"""
        logger.info("Forcing database reconnection...")
        try:
            if self.client:
                self.client.close()
        except:
            pass
        return self._connect()
    
    def get_collection(self, collection_name: str) -> Collection:
        """
        Get a collection by name
        
        Args:
            collection_name: Name of the collection
        
        Returns:
            MongoDB collection object
        """
        if self.db is None:
            raise RuntimeError("Database not initialized")
        return self.db[collection_name]
    
    def __del__(self):
        """Cleanup database connection on deletion"""
        try:
            if self.client:
                self.client.close()
                logger.info("MongoDB connection closed")
        except:
            pass


# Global database instance (singleton)
db = Database()

