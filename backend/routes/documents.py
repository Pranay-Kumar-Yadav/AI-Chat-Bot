"""Document upload and management routes."""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, BackgroundTasks
from pathlib import Path
import aiofiles
import uuid
from loguru import logger

from backend.config import settings
from backend.database import get_database
from backend.services.rag_service import get_rag_service
from backend.core import ValidationException, RAGException
from backend.utils import format_response

router = APIRouter()

# Allowed file types for upload
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


async def process_document_background(
    file_path: str,
    document_id: str,
    conversation_id: str,
    filename: str,
):
    """
    Background task to process document with RAG.
    
    Args:
        file_path: Path to the uploaded file
        document_id: Document ID
        conversation_id: Conversation ID
        filename: Original filename
    """
    try:
        rag_service = await get_rag_service()
        result = await rag_service.upload_document(
            file_path=file_path,
            document_id=document_id,
            conversation_id=conversation_id,
            filename=filename,
        )
        
        db = get_database()
        if "error" not in result:
            await db.update_document_status(document_id, "completed")
            logger.info(f"Document {document_id} processed successfully")
        else:
            await db.update_document_status(document_id, "failed")
            logger.error(f"Document {document_id} processing failed: {result.get('error')}")
    
    except Exception as e:
        logger.error(f"Error in background document processing: {e}")
        try:
            db = get_database()
            await db.update_document_status(document_id, "failed")
        except:
            pass


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: str = Query(...),
    background_tasks: BackgroundTasks = None,
):
    """
    Upload a document for RAG processing.
    
    Args:
        file: Document file (PDF, TXT, MD)
        conversation_id: Associated conversation ID
        background_tasks: FastAPI background tasks
        
    Returns:
        Upload response with document ID
    """
    try:
        # Validate file
        if not file.filename:
            raise ValidationException("Filename is required")
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise ValidationException(
                f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > MAX_FILE_SIZE:
            raise ValidationException(f"File size exceeds {MAX_FILE_SIZE / (1024*1024):.1f} MB limit")
        
        if len(content) == 0:
            raise ValidationException("File is empty")
        
        # Generate document ID
        document_id = f"doc_{uuid.uuid4().hex[:12]}"
        
        # Create uploads directory if it doesn't exist
        upload_dir = Path(settings.pdf_upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file to disk
        file_path = upload_dir / f"{document_id}_{file.filename}"
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        
        logger.info(f"Saved uploaded file: {file_path}")
        
        # Save document metadata to database
        db = get_database()
        success = await db.save_document({
            "document_id": document_id,
            "conversation_id": conversation_id,
            "filename": file.filename,
            "file_type": file_ext,
            "size": len(content),
            "status": "processing",
            "created_at": None,
            "updated_at": None,
        })
        
        if not success:
            raise RAGException("Failed to save document metadata")
        
        # Schedule background processing
        if background_tasks:
            background_tasks.add_task(
                process_document_background,
                file_path=str(file_path),
                document_id=document_id,
                conversation_id=conversation_id,
                filename=file.filename,
            )
        
        return format_response(
            {
                "document_id": document_id,
                "filename": file.filename,
                "size": len(content),
                "status": "processing",
                "message": "Document uploaded successfully. Processing started.",
            },
            "Document uploaded successfully"
        )
    
    except ValidationException as e:
        logger.error(f"Validation error: {e.detail}")
        raise HTTPException(status_code=422, detail=e.detail)
    except RAGException as e:
        logger.error(f"RAG error: {e.detail}")
        raise HTTPException(status_code=400, detail=e.detail)
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_documents(
    conversation_id: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """
    List all documents for a conversation.
    
    Args:
        conversation_id: Conversation ID
        skip: Number of documents to skip
        limit: Maximum documents to return
        
    Returns:
        List of documents
    """
    try:
        db = get_database()
        documents = await db.get_documents_for_conversation(
            conversation_id=conversation_id,
            limit=limit,
        )
        
        return format_response(
            {
                "conversation_id": conversation_id,
                "documents": documents,
                "skip": skip,
                "limit": limit,
                "count": len(documents),
            },
            "Documents retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """
    Get document metadata.
    
    Args:
        document_id: Document ID
        
    Returns:
        Document information
    """
    try:
        db = get_database()
        document = await db.get_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return format_response(
            document,
            "Document retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, conversation_id: str = Query(...)):
    """
    Delete a document and associated files.
    
    Args:
        document_id: Document ID
        conversation_id: Conversation ID
        
    Returns:
        Success message
    """
    try:
        db = get_database()
        document = await db.get_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete file from disk if exists
        upload_dir = Path(settings.pdf_upload_dir)
        for file_path in upload_dir.glob(f"{document_id}_*"):
            try:
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not delete file {file_path}: {e}")
        
        # Delete from RAG vector store
        rag_service = await get_rag_service()
        await rag_service.delete_document_from_rag(
            document_id=document_id,
            conversation_id=conversation_id,
        )
        
        # Delete from database
        success = await db.delete_document(document_id)
        
        if not success:
            raise RAGException("Failed to delete document")
        
        return format_response(
            {"document_id": document_id},
            "Document deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/documents/{document_id}/status")
async def update_document_status(document_id: str, status: str = Query(...)):
    """
    Update document processing status.
    
    Args:
        document_id: Document ID
        status: New status (processing, completed, failed)
        
    Returns:
        Updated document
    """
    try:
        # Validate status
        valid_statuses = {"processing", "completed", "failed"}
        if status not in valid_statuses:
            raise ValidationException(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        db = get_database()
        document = await db.get_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        success = await db.update_document_status(document_id, status)
        
        if not success:
            raise RAGException("Failed to update document status")
        
        updated_doc = await db.get_document(document_id)
        
        return format_response(
            updated_doc,
            "Document status updated successfully"
        )
    except ValidationException as e:
        logger.error(f"Validation error: {e.detail}")
        raise HTTPException(status_code=422, detail=e.detail)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        raise HTTPException(status_code=500, detail=str(e))