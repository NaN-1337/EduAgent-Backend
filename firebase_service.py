import firebase_admin
from firebase_admin import credentials, storage
from config import Config
import os

class FirebaseService:
    """Service for Firebase Storage operations"""
    
    _initialized = False
    _bucket = None
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK (call once at app startup)"""
        if cls._initialized:
            return
        
        try:
            # Check if credentials file exists
            cred_path = Config.FIREBASE_SERVICE_ACCOUNT_PATH
            if not cred_path or not os.path.exists(cred_path):
                print("⚠️ Firebase credentials not found. Firebase Storage will not be available.")
                return
            
            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': Config.FIREBASE_STORAGE_BUCKET
            })
            
            # Get bucket reference
            cls._bucket = storage.bucket()
            cls._initialized = True
            
            print("✅ Firebase Storage initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Firebase Storage: {str(e)}")
            cls._initialized = False
    
    @classmethod
    def is_available(cls):
        """Check if Firebase Storage is available"""
        return cls._initialized and cls._bucket is not None
    
    @classmethod
    def get_bucket(cls):
        """Get the Firebase Storage bucket"""
        if not cls._initialized:
            cls.initialize()
        return cls._bucket
    
    @classmethod
    def upload_file(
        cls,
        file_path: str,
        destination_path: str,
        content_type: str = None,
        make_public: bool = False,
        metadata: dict = None
    ) -> dict:
        """
        Upload a file to Firebase Storage.
        
        Args:
            file_path: Local path to the file to upload
            destination_path: Path in Firebase Storage (e.g., 'teacher123/6/lecture456/podcast.mp3')
            content_type: MIME type of the file (e.g., 'audio/mpeg')
            make_public: Whether to make the file publicly accessible
            metadata: Additional metadata to attach to the file
            
        Returns:
            Dictionary with upload information:
            {
                'success': bool,
                'destination_path': str,
                'public_url': str (if make_public=True),
                'download_url': str (signed URL, valid for 7 days),
                'size_bytes': int,
                'content_type': str
            }
        """
        if not cls.is_available():
            raise Exception("Firebase Storage is not initialized")
        
        try:
            bucket = cls.get_bucket()
            blob = bucket.blob(destination_path)
            
            # Set content type if provided
            if content_type:
                blob.content_type = content_type
            
            # Set custom metadata if provided
            if metadata:
                blob.metadata = metadata
            
            # Upload the file
            blob.upload_from_filename(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            result = {
                'success': True,
                'destination_path': destination_path,
                'size_bytes': file_size,
                'content_type': content_type or blob.content_type
            }
            
            # Make public if requested
            if make_public:
                blob.make_public()
                # Use permanent public URL
                result['download_url'] = blob.public_url
                result['public_url'] = blob.public_url
            else:
                # Only use signed URL if file is private (valid for 7 days)
                from datetime import timedelta
                signed_url = blob.generate_signed_url(
                    expiration=timedelta(days=7),
                    method='GET'
                )
                result['download_url'] = signed_url
            
            print(f"✅ File uploaded to Firebase Storage: {destination_path}")
            print(f"   Size: {file_size / 1024 / 1024:.2f} MB")
            if make_public:
                print(f"   Public URL: {result['download_url']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to upload file to Firebase Storage: {str(e)}")
            raise Exception(f"Firebase upload failed: {str(e)}")
    
    @classmethod
    def upload_bytes(
        cls,
        file_bytes: bytes,
        destination_path: str,
        content_type: str = None,
        make_public: bool = False,
        metadata: dict = None
    ) -> dict:
        """
        Upload bytes directly to Firebase Storage without saving to disk.
        
        Args:
            file_bytes: File content as bytes
            destination_path: Path in Firebase Storage
            content_type: MIME type of the file
            make_public: Whether to make the file publicly accessible
            metadata: Additional metadata to attach to the file
            
        Returns:
            Dictionary with upload information (same as upload_file)
        """
        if not cls.is_available():
            raise Exception("Firebase Storage is not initialized")
        
        try:
            bucket = cls.get_bucket()
            blob = bucket.blob(destination_path)
            
            # Set content type if provided
            if content_type:
                blob.content_type = content_type
            
            # Set custom metadata if provided
            if metadata:
                blob.metadata = metadata
            
            # Upload the bytes
            blob.upload_from_string(file_bytes, content_type=content_type)
            
            result = {
                'success': True,
                'destination_path': destination_path,
                'size_bytes': len(file_bytes),
                'content_type': content_type or blob.content_type
            }
            
            # Make public if requested
            if make_public:
                blob.make_public()
                # Use permanent public URL
                result['download_url'] = blob.public_url
                result['public_url'] = blob.public_url
            else:
                # Only use signed URL if file is private (valid for 7 days)
                from datetime import timedelta
                signed_url = blob.generate_signed_url(
                    expiration=timedelta(days=7),
                    method='GET'
                )
                result['download_url'] = signed_url
            
            print(f"✅ Bytes uploaded to Firebase Storage: {destination_path}")
            print(f"   Size: {len(file_bytes) / 1024 / 1024:.2f} MB")
            if make_public:
                print(f"   Public URL: {result['download_url']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Failed to upload bytes to Firebase Storage: {str(e)}")
            raise Exception(f"Firebase upload failed: {str(e)}")
    
    @classmethod
    def delete_file(cls, file_path: str) -> bool:
        """
        Delete a file from Firebase Storage.
        
        Args:
            file_path: Path to the file in Firebase Storage
            
        Returns:
            True if deleted successfully
        """
        if not cls.is_available():
            raise Exception("Firebase Storage is not initialized")
        
        try:
            bucket = cls.get_bucket()
            blob = bucket.blob(file_path)
            blob.delete()
            
            print(f"✅ File deleted from Firebase Storage: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete file from Firebase Storage: {str(e)}")
            raise Exception(f"Firebase delete failed: {str(e)}")

# Initialize Firebase when module is imported
FirebaseService.initialize()
