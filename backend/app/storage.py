"""
Supabase Storage Service
Handles file uploads/downloads using Supabase Storage instead of AWS S3
"""
from fastapi import UploadFile, HTTPException, status
from app.database import get_supabase
from typing import Optional
import uuid
import mimetypes


class SupabaseStorage:
    """
    Supabase Storage wrapper for file operations
    """
    
    @staticmethod
    async def upload_file(
        file: UploadFile,
        bucket: str,
        folder: str = "",
        file_name: Optional[str] = None
    ) -> dict:
        """
        Upload file to Supabase Storage
        
        Args:
            file: FastAPI UploadFile object
            bucket: Supabase storage bucket name (e.g., 'kyc-documents', 'vehicle-images')
            folder: Optional folder path within bucket (e.g., 'user_123/documents')
            file_name: Optional custom file name (will generate UUID if not provided)
        
        Returns:
            dict: {
                'path': str,  # Full path in bucket
                'public_url': str,  # Public URL to access file
                'bucket': str  # Bucket name
            }
        
        Raises:
            HTTPException: If upload fails
        """
        try:
            supabase = get_supabase()
            
            # Generate unique file name if not provided
            if not file_name:
                extension = file.filename.split('.')[-1] if '.' in file.filename else ''
                file_name = f"{uuid.uuid4()}.{extension}" if extension else str(uuid.uuid4())
            
            # Build full path
            file_path = f"{folder}/{file_name}" if folder else file_name
            
            # Read file content
            file_content = await file.read()
            
            # Detect MIME type
            content_type = file.content_type
            if not content_type:
                content_type, _ = mimetypes.guess_type(file.filename)
                content_type = content_type or 'application/octet-stream'
            
            # Upload to Supabase Storage
            response = supabase.storage.from_(bucket).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "upsert": "false"  # Don't overwrite existing files
                }
            )
            
            # Get public URL
            public_url_response = supabase.storage.from_(bucket).get_public_url(file_path)
            
            return {
                'path': file_path,
                'public_url': public_url_response,
                'bucket': bucket,
                'size': len(file_content),
                'content_type': content_type
            }
            
        except Exception as e:
            error_message = str(e)
            
            # Handle specific Supabase errors
            if "already exists" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="File with this name already exists"
                )
            elif "bucket not found" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Storage bucket '{bucket}' not found. Please create it in Supabase dashboard."
                )
            elif "not allowed" in error_message.lower() or "unauthorized" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="File upload not allowed. Check bucket policies in Supabase."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload file: {error_message}"
                )
        finally:
            # Reset file pointer
            await file.seek(0)
    
    @staticmethod
    def get_public_url(bucket: str, file_path: str) -> str:
        """
        Get public URL for a file
        
        Args:
            bucket: Storage bucket name
            file_path: File path in bucket
        
        Returns:
            str: Public URL
        """
        try:
            supabase = get_supabase()
            return supabase.storage.from_(bucket).get_public_url(file_path)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get public URL: {str(e)}"
            )
    
    @staticmethod
    async def delete_file(bucket: str, file_path: str) -> bool:
        """
        Delete file from Supabase Storage
        
        Args:
            bucket: Storage bucket name
            file_path: File path in bucket
        
        Returns:
            bool: True if deleted successfully
        """
        try:
            supabase = get_supabase()
            supabase.storage.from_(bucket).remove([file_path])
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )
    
    @staticmethod
    async def download_file(bucket: str, file_path: str) -> bytes:
        """
        Download file from Supabase Storage
        
        Args:
            bucket: Storage bucket name
            file_path: File path in bucket
        
        Returns:
            bytes: File content
        """
        try:
            supabase = get_supabase()
            response = supabase.storage.from_(bucket).download(file_path)
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to download file: {str(e)}"
            )
    
    @staticmethod
    def list_files(bucket: str, folder: str = "") -> list:
        """
        List files in a bucket folder
        
        Args:
            bucket: Storage bucket name
            folder: Folder path (optional)
        
        Returns:
            list: List of file objects
        """
        try:
            supabase = get_supabase()
            response = supabase.storage.from_(bucket).list(folder)
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list files: {str(e)}"
            )


# Create singleton instance
storage = SupabaseStorage()


# Helper function for backward compatibility
async def upload_file(
    file: UploadFile,
    bucket: str,
    folder: str = "",
    file_name: Optional[str] = None
) -> str:
    """
    Simple upload function that returns just the public URL
    
    Returns:
        str: Public URL of uploaded file
    """
    result = await storage.upload_file(file, bucket, folder, file_name)
    return result['public_url']

