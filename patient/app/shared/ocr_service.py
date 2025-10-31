"""
OCR Service for processing prescription documents, PDFs, and images
"""
import os
from typing import Dict, Any

# Optional imports with fallback
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("[WARN] PyMuPDF not available")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[WARN] PIL not available")


class OCRService:
    """OCR service for processing prescription documents, PDFs, and images"""
    
    def __init__(self):
        self.supported_formats = {
            'pdf': ['.pdf'],
            'text': ['.txt', '.doc', '.docx'],
            'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        }
        self.allowed_types = [
            'application/pdf',
            'text/plain',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg',
            'image/png',
            'image/bmp',
            'image/tiff'
        ]
    
    def get_file_type(self, filename: str) -> str:
        """Determine file type based on extension"""
        ext = os.path.splitext(filename.lower())[1]
        
        for file_type, extensions in self.supported_formats.items():
            if ext in extensions:
                return file_type
        
        return 'unknown'
    
    def validate_file_type(self, content_type: str, filename: str) -> bool:
        """Validate if file type is supported for processing"""
        # Handle missing or generic content types
        if not content_type or content_type == "":
            # Fallback to filename extension check
            file_type = self.get_file_type(filename)
            return file_type != 'unknown'
        
        # Check content type first
        if content_type in self.allowed_types:
            return True
        
        # Handle content types with parameters
        base_content_type = content_type.split(';')[0].strip()
        if base_content_type in self.allowed_types:
            return True
        
        # Handle generic binary types that might be PDFs
        if content_type in ["application/octet-stream", "binary/octet-stream", "application/binary"]:
            file_type = self.get_file_type(filename)
            return file_type != 'unknown'
        
        # Final fallback to filename extension check
        file_type = self.get_file_type(filename)
        return file_type != 'unknown'
    
    def process_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process any supported file type and return unified results"""
        try:
            file_type = self.get_file_type(filename)
            
            if file_type == 'pdf':
                return self._process_pdf(file_content, filename)
            elif file_type == 'text':
                return self._process_text_file(file_content, filename)
            elif file_type == 'image':
                return self._process_image(file_content, filename)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {filename}",
                    "supported_types": list(self.supported_formats.keys())
                }
                
        except Exception as e:
            print(f"[ERROR] Error processing file {filename}: {e}")
            return {
                "success": False,
                "error": f"Processing error: {str(e)}",
                "filename": filename
            }
    
    def _process_pdf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process PDF file (both native text and scanned pages)"""
        if not PYMUPDF_AVAILABLE:
            return {
                "success": False,
                "error": "PDF processing not available. Install PyMuPDF: pip install PyMuPDF"
            }
        
        try:
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            
            results = []
            total_pages = len(pdf_document)
            native_text_pages = 0
            ocr_pages = 0
            
            for page_num in range(total_pages):
                page = pdf_document[page_num]
                
                # Try to extract native text first
                text = page.get_text()
                
                if text.strip():
                    # Native text available
                    results.append({
                        "page": page_num + 1,
                        "text": text.strip(),
                        "confidence": 1.0,
                        "method": "native_text"
                    })
                    native_text_pages += 1
                else:
                    # No native text, might be scanned image
                    results.append({
                        "page": page_num + 1,
                        "text": "[Scanned page - text extraction not available]",
                        "confidence": 0.0,
                        "method": "scanned_page"
                    })
                    ocr_pages += 1
            
            pdf_document.close()
            
            # Extract full text for prescription processing
            full_text = "\n".join([result["text"] for result in results if result["method"] == "native_text"])
            
            return {
                "success": True,
                "filename": filename,
                "file_type": "pdf",
                "total_pages": total_pages,
                "native_text_pages": native_text_pages,
                "ocr_pages": ocr_pages,
                "results": results,
                "full_text": full_text,
                "extracted_text": full_text if full_text else "No extractable text found"
            }
            
        except Exception as e:
            print(f"[ERROR] Error processing PDF {filename}: {e}")
            return {
                "success": False,
                "error": f"PDF processing error: {str(e)}",
                "filename": filename
            }
    
    def _process_text_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process text files (TXT, DOC, DOCX)"""
        try:
            # Try to decode as UTF-8 first
            try:
                text = file_content.decode('utf-8')
            except UnicodeDecodeError:
                # Try other encodings
                text = file_content.decode('latin-1')
            
            return {
                "success": True,
                "filename": filename,
                "file_type": "text",
                "total_pages": 1,
                "native_text_pages": 1,
                "ocr_pages": 0,
                "results": [{
                    "page": 1,
                    "text": text,
                    "confidence": 1.0,
                    "method": "text_file"
                }],
                "full_text": text,
                "extracted_text": text
            }
            
        except Exception as e:
            print(f"[ERROR] Error processing text file {filename}: {e}")
            return {
                "success": False,
                "error": f"Text file processing error: {str(e)}",
                "filename": filename
            }
    
    def _process_image(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process image files (basic text extraction placeholder)"""
        if not PIL_AVAILABLE:
            return {
                "success": False,
                "error": "Image processing not available. Install Pillow: pip install Pillow"
            }
        
        try:
            # For now, return a placeholder since full OCR requires additional libraries
            # In a production system, you'd integrate with Tesseract OCR or cloud OCR services
            return {
                "success": True,
                "filename": filename,
                "file_type": "image",
                "total_pages": 1,
                "native_text_pages": 0,
                "ocr_pages": 1,
                "results": [{
                    "page": 1,
                    "text": "[Image file - OCR text extraction requires Tesseract or cloud OCR service]",
                    "confidence": 0.0,
                    "method": "image_placeholder"
                }],
                "full_text": "",
                "extracted_text": "Image processing available but OCR text extraction requires additional setup"
            }
            
        except Exception as e:
            print(f"[ERROR] Error processing image {filename}: {e}")
            return {
                "success": False,
                "error": f"Image processing error: {str(e)}",
                "filename": filename
            }


# Global OCR service instance - import this for use across the app
ocr_service = OCRService()

