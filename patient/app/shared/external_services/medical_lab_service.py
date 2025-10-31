#!/usr/bin/env python3
"""
Medical Lab Service for Patient Alert System
Direct integration of Medical Lab module
"""

import os
import base64
import io
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class MedicalLabService:
    """Medical Lab Service for OCR and document processing"""
    
    def __init__(self):
        """Initialize the Medical Lab Service"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.mongo_uri = os.getenv("MONGO_URI")
        self._ocr_instance = None
        self._openai_client = None
        
        # Initialize OpenAI client
        try:
            if self.openai_api_key and self.openai_api_key != "your_openai_api_key_here":
                import openai
                self._openai_client = openai.OpenAI(api_key=self.openai_api_key)
                print("[OK] Medical Lab OpenAI client initialized")
            else:
                print("[WARN] OpenAI API key not found, using fallback mode")
        except Exception as e:
            print(f"[WARN] OpenAI initialization failed: {e}")
        
        # Supported file formats
        self.supported_formats = {
            'pdf': ['.pdf'],
            'text': ['.txt', '.doc', '.docx'],
            'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        }
        
        self.allowed_types = [
            # Images
            "image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff", "image/tif",
            # PDF documents
            "application/pdf", "application/x-pdf", "binary/octet-stream",
            # Text files
            "text/plain", "text/plain; charset=utf-8", "text/plain; charset=iso-8859-1",
            # Word documents
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword", "application/vnd.ms-word",
            # Generic binary
            "application/octet-stream", "application/binary", "binary/pdf",
            "application/force-download", "content/unknown", "application/x-download",
            "application/unknown"
        ]
        
        print("[OK] Medical Lab Service initialized successfully")
    
    def _get_ocr_instance(self):
        """Get or create PaddleOCR instance (singleton pattern)"""
        if self._ocr_instance is None:
            try:
                from paddleocr import PaddleOCR
                self._ocr_instance = PaddleOCR(
                    use_angle_cls=True,
                    lang='en'
                )
                logger.info("[OK] PaddleOCR instance created successfully")
            except Exception as e:
                logger.error(f"[ERROR] Failed to create PaddleOCR instance: {e}")
                raise e
        return self._ocr_instance
    
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
            file_type = self.get_file_type(filename)
            return file_type != 'unknown'
        
        # Check content type first
        if content_type in self.allowed_types:
            return True
        
        # Handle content types with parameters
        base_content_type = content_type.split(';')[0].strip()
        if base_content_type in self.allowed_types:
            return True
        
        # Handle generic binary types
        if content_type in ["application/octet-stream", "binary/octet-stream", "application/binary"]:
            file_type = self.get_file_type(filename)
            return file_type != 'unknown'
        
        # Handle unknown content types
        if content_type in ["content/unknown", "application/unknown", "unknown"]:
            file_type = self.get_file_type(filename)
            return file_type != 'unknown'
        
        # Final fallback to filename extension check
        file_type = self.get_file_type(filename)
        return file_type != 'unknown'
    
    async def process_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process any supported file type and return unified results"""
        try:
            file_type = self.get_file_type(filename)
            
            if file_type == 'pdf':
                return await self._process_pdf(file_content, filename)
            elif file_type == 'text':
                return await self._process_text_file(file_content, filename)
            elif file_type == 'image':
                return await self._process_image(file_content, filename)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {filename}",
                    "supported_types": list(self.supported_formats.keys())
                }
                
        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            return {
                "success": False,
                "error": f"Processing error: {str(e)}",
                "filename": filename
            }
    
    async def _process_pdf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process PDF file (both native text and scanned pages)"""
        try:
            import fitz  # PyMuPDF
            
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            
            results = []
            total_pages = len(pdf_document)
            native_text_pages = 0
            ocr_pages = 0
            
            for page_num in range(total_pages):
                page = pdf_document[page_num]
                
                # Try to extract native text first
                page_text = page.get_text()
                
                if page_text.strip():  # Native text available
                    results.append({
                        "page": page_num + 1,
                        "text": page_text.strip(),
                        "method": "native",
                        "confidence": 1.0,
                        "bbox": [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
                    })
                    native_text_pages += 1
                else:  # No native text, need OCR
                    # Convert page to image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                    img_data = pix.tobytes("png")
                    
                    # Process image with OCR
                    ocr_result = await self._process_image_bytes(img_data, f"{filename}_page_{page_num + 1}")
                    
                    if ocr_result.get("success") and ocr_result.get("results"):
                        for item in ocr_result["results"]:
                            results.append({
                                "page": page_num + 1,
                                "text": item["text"],
                                "method": "ocr",
                                "confidence": item["confidence"],
                                "bbox": item.get("bbox", [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]])
                            })
                        ocr_pages += 1
                    else:
                        results.append({
                            "page": page_num + 1,
                            "text": "",
                            "method": "ocr_failed",
                            "confidence": 0.0,
                            "bbox": [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
                        })
            
            pdf_document.close()
            
            # Combine all text
            all_text = "\n".join([item["text"] for item in results if item["text"]])
            
            # Generate extracted_text field for consistency
            extracted_text = self._generate_extracted_text(results)
            
            # Generate dynamic content description
            dynamic_content = self._generate_dynamic_content(results, filename, "PDF")
            
            return {
                "success": True,
                "filename": filename,
                "file_type": "PDF",
                "total_pages": total_pages,
                "native_text_pages": native_text_pages,
                "ocr_pages": ocr_pages,
                "text_count": len(results),
                "extracted_text": extracted_text,
                "full_content": dynamic_content,
                "results": results,
                "processing_summary": {
                    "total_pages": total_pages,
                    "native_text_pages": native_text_pages,
                    "ocr_pages": ocr_pages,
                    "mixed_processing": native_text_pages > 0 and ocr_pages > 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {e}")
            return {
                "success": False,
                "error": f"PDF processing error: {str(e)}",
                "filename": filename
            }
    
    async def _process_text_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process text files (TXT, DOC, DOCX)"""
        try:
            ext = os.path.splitext(filename.lower())[1]
            
            if ext == '.txt':
                # Simple text file
                text_content = file_content.decode('utf-8', errors='ignore')
                lines = text_content.split('\n')
                
                results = []
                for i, line in enumerate(lines):
                    if line.strip():
                        results.append({
                            "line": i + 1,
                            "text": line.strip(),
                            "method": "native",
                            "confidence": 1.0,
                            "bbox": [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
                        })
                
                # Generate extracted_text field for consistency
                extracted_text = self._generate_extracted_text(results)
                
                # Generate dynamic content description
                dynamic_content = self._generate_dynamic_content(results, filename, "text")
                
                return {
                    "success": True,
                    "filename": filename,
                    "file_type": "TXT",
                    "total_pages": 1,
                    "text_count": len(results),
                    "extracted_text": extracted_text,
                    "full_content": dynamic_content,
                    "results": results,
                    "processing_summary": {
                        "total_pages": 1,
                        "native_text_pages": 1,
                        "ocr_pages": 0,
                        "mixed_processing": False
                    }
                }
            
            elif ext in ['.doc', '.docx']:
                # Word document - convert to text
                try:
                    from docx import Document
                    doc = Document(io.BytesIO(file_content))
                    
                    results = []
                    full_text = ""
                    
                    for para in doc.paragraphs:
                        if para.text.strip():
                            results.append({
                                "paragraph": len(results) + 1,
                                "text": para.text.strip(),
                                "method": "native",
                                "confidence": 1.0,
                                "bbox": [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
                            })
                            full_text += para.text.strip() + "\n"
                    
                    # Generate extracted_text field for consistency
                    extracted_text = self._generate_extracted_text(results)
                    
                    # Generate dynamic content description
                    dynamic_content = self._generate_dynamic_content(results, filename, "Word")
                    
                    return {
                        "success": True,
                        "filename": filename,
                        "file_type": "DOCX",
                        "total_pages": 1,
                        "text_count": len(results),
                        "extracted_text": extracted_text,
                        "full_content": dynamic_content,
                        "results": results,
                        "processing_summary": {
                            "total_pages": 1,
                            "native_text_pages": 1,
                            "ocr_pages": 0,
                            "mixed_processing": False
                        }
                    }
                    
                except Exception as e:
                    logger.error(f"Error processing Word document {filename}: {e}")
                    return {
                        "success": False,
                        "error": f"Word document processing error: {str(e)}",
                        "filename": filename
                    }
            
        except Exception as e:
            logger.error(f"Error processing text file {filename}: {e}")
            return {
                "success": False,
                "error": f"Text file processing error: {str(e)}",
                "filename": filename
            }
    
    async def _process_image(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process image files using OCR"""
        try:
            logger.info(f"[*] Processing image: {filename} ({len(file_content)} bytes)")
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(file_content))
            
            # Resize large images to improve processing speed
            max_size = 2048
            if image.width > max_size or image.height > max_size:
                logger.info(f"[*] Resizing large image from {image.width}x{image.height}")
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                logger.info(f"[*] Resized to {image.width}x{image.height}")
            
            # Convert PIL image to OpenCV format for PaddleOCR
            import cv2
            import numpy as np
            
            # Convert PIL to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Use PaddleOCR singleton instance with timeout
            logger.info(f"[*] Running PaddleOCR on {filename}")
            ocr = self._get_ocr_instance()
            
            # Run OCR with timeout to prevent hanging
            try:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, ocr.ocr, opencv_image
                    ),
                    timeout=120  # 2 minutes timeout
                )
                logger.info(f"[OK] PaddleOCR completed for {filename}")
            except asyncio.TimeoutError:
                logger.warning(f"⏰ PaddleOCR timeout for {filename}, trying OpenAI fallback")
                # If PaddleOCR times out, try OpenAI
                if self._openai_client:
                    return await self._openai_extract_text_from_image(file_content, filename)
                else:
                    raise Exception("PaddleOCR processing timeout")
            
            # Extract text from result
            extracted_text = []
            if result and result[0]:
                for line in result[0]:
                    try:
                        if line and len(line) >= 2 and line[1] and len(line[1]) >= 2:
                            text = line[1][0]  # Extract text
                            confidence = line[1][1]  # Extract confidence score
                            bbox = line[0]  # Extract bounding box coordinates
                            
                            if bbox and len(bbox) >= 4:
                                extracted_text.append({
                                    "text": text,
                                    "confidence": float(confidence),
                                    "bbox": [[float(coord) for coord in bbox[0]], [float(coord) for coord in bbox[1]], 
                                            [float(coord) for coord in bbox[2]], [float(coord) for coord in bbox[3]]]
                                })
                    except (IndexError, TypeError, ValueError) as e:
                        logger.warning(f"Skipping malformed OCR result line: {e}")
                        continue
            
            # Generate combined extracted text
            combined_text = self._generate_extracted_text(extracted_text)
            
            # Generate dynamic content description
            dynamic_content = self._generate_dynamic_content(extracted_text, filename, "image")
            
            # Prepare response
            response_data = {
                "success": True,
                "filename": filename,
                "file_type": "IMAGE",
                "total_pages": 1,
                "text_count": len(extracted_text),
                "extracted_text": combined_text,
                "full_content": dynamic_content,
                "results": extracted_text,
                "processing_summary": {
                    "total_pages": 1,
                    "native_text_pages": 0,
                    "ocr_pages": 1,
                    "mixed_processing": False
                }
            }
            
            # If PaddleOCR didn't extract any text and OpenAI is available, try OpenAI
            if len(extracted_text) == 0 and self._openai_client:
                logger.info(f"PaddleOCR found no text in {filename}, trying OpenAI Vision API...")
                openai_result = await self._openai_extract_text_from_image(file_content, filename)
                if openai_result.get("success") and openai_result.get("extracted_text"):
                    logger.info(f"OpenAI successfully extracted text from {filename}")
                    return openai_result
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing image {filename}: {e}")
            
            # If PaddleOCR failed and OpenAI is available, try OpenAI as fallback
            if self._openai_client:
                logger.info(f"PaddleOCR failed for {filename}, trying OpenAI Vision API as fallback...")
                try:
                    openai_result = await self._openai_extract_text_from_image(file_content, filename)
                    if openai_result.get("success") and openai_result.get("extracted_text"):
                        logger.info(f"OpenAI successfully extracted text from {filename} after PaddleOCR failure")
                        return openai_result
                except Exception as openai_error:
                    logger.error(f"OpenAI fallback also failed for {filename}: {openai_error}")
            
            return {
                "success": False,
                "filename": filename,
                "file_type": "IMAGE",
                "total_pages": 1,
                "text_count": 0,
                "extracted_text": "",
                "full_content": f"Failed to process image: {str(e)}",
                "results": [],
                "processing_summary": {
                    "total_pages": 1,
                    "native_text_pages": 0,
                    "ocr_pages": 0,
                    "mixed_processing": False,
                    "error": str(e)
                },
                "error": f"Image processing error: {str(e)}"
            }
    
    async def _process_image_bytes(self, image_data: bytes, filename: str) -> Dict[str, Any]:
        """Process image data from PDF pages using OCR"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert PIL image to OpenCV format for PaddleOCR
            import cv2
            import numpy as np
            
            # Convert PIL to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Use PaddleOCR singleton instance
            ocr = self._get_ocr_instance()
            result = ocr.ocr(opencv_image)
            
            # Extract text from result
            extracted_text = []
            if result and result[0]:
                for line in result[0]:
                    try:
                        if line and len(line) >= 2 and line[1] and len(line[1]) >= 2:
                            text = line[1][0]  # Extract text
                            confidence = line[1][1]  # Extract confidence score
                            bbox = line[0]  # Extract bounding box coordinates
                            
                            if bbox and len(bbox) >= 4:
                                extracted_text.append({
                                    "text": text,
                                    "confidence": float(confidence),
                                    "bbox": [[float(coord) for coord in bbox[0]], [float(coord) for coord in bbox[1]], 
                                            [float(coord) for coord in bbox[2]], [float(coord) for coord in bbox[3]]]
                                })
                    except (IndexError, TypeError, ValueError) as e:
                        logger.warning(f"Skipping malformed OCR result line: {e}")
                        continue
            
            # Prepare response
            response_data = {
                "success": True,
                "filename": filename,
                "text_count": len(extracted_text),
                "results": extracted_text
            }
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing image bytes {filename}: {e}")
            return {
                "success": False,
                "filename": filename,
                "file_type": "IMAGE",
                "total_pages": 1,
                "text_count": 0,
                "extracted_text": "",
                "full_content": f"Failed to process image bytes: {str(e)}",
                "results": [],
                "processing_summary": {
                    "total_pages": 1,
                    "native_text_pages": 0,
                    "ocr_pages": 0,
                    "mixed_processing": False,
                    "error": str(e)
                },
                "error": f"Image bytes processing error: {str(e)}"
            }
    
    async def _openai_extract_text_from_image(self, image_data: bytes, filename: str) -> Dict[str, Any]:
        """Extract text from image using OpenAI Vision API"""
        try:
            if not self._openai_client:
                return {
                    "success": False,
                    "error": "OpenAI API key not configured",
                    "filename": filename
                }
            
            # Convert image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Get image format
            image = Image.open(io.BytesIO(image_data))
            image_format = image.format.lower() if image.format else 'png'
            
            # Prepare the request
            response = self._openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please extract all text content from this image. This appears to be a medical document or report. Extract all visible text including: patient names, dates, medical conditions, medications, dosages, doctor names, addresses, phone numbers, percentages, and any other textual information. Preserve the formatting and structure. Return only the extracted text content, nothing else."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{image_format};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            extracted_text = response.choices[0].message.content.strip()
            
            if extracted_text:
                return {
                    "success": True,
                    "filename": filename,
                    "file_type": "IMAGE",
                    "total_pages": 1,
                    "text_count": 1,
                    "extracted_text": extracted_text,
                    "full_content": f"Text extracted using OpenAI Vision API: {extracted_text[:100]}...",
                    "results": [{
                        "text": extracted_text,
                        "confidence": 0.95,  # OpenAI doesn't provide confidence scores
                        "bbox": [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0]]
                    }],
                    "processing_summary": {
                        "total_pages": 1,
                        "native_text_pages": 0,
                        "ocr_pages": 1,
                        "mixed_processing": False,
                        "method": "openai_vision"
                    }
                }
            else:
                return {
                    "success": False,
                    "filename": filename,
                    "file_type": "IMAGE",
                    "total_pages": 1,
                    "text_count": 0,
                    "extracted_text": "",
                    "full_content": "No text found in image using OpenAI Vision API",
                    "results": [],
                    "processing_summary": {
                        "total_pages": 1,
                        "native_text_pages": 0,
                        "ocr_pages": 1,
                        "mixed_processing": False,
                        "method": "openai_vision"
                    },
                    "error": "No text found in image"
                }
                
        except Exception as e:
            logger.error(f"Error in OpenAI text extraction: {e}")
            return {
                "success": False,
                "filename": filename,
                "file_type": "IMAGE",
                "total_pages": 1,
                "text_count": 0,
                "extracted_text": "",
                "full_content": f"OpenAI processing error: {str(e)}",
                "results": [],
                "processing_summary": {
                    "total_pages": 1,
                    "native_text_pages": 0,
                    "ocr_pages": 0,
                    "mixed_processing": False,
                    "method": "openai_vision",
                    "error": str(e)
                },
                "error": f"OpenAI processing error: {str(e)}"
            }
    
    def _generate_extracted_text(self, results: List[Dict[str, Any]]) -> str:
        """Generate combined extracted text from OCR results"""
        if not results:
            return ""
        
        # Sort results by vertical position (top to bottom) and horizontal position (left to right)
        sorted_results = sorted(results, key=lambda x: (x['bbox'][0][1], x['bbox'][0][0]))
        
        # Combine all text with newlines
        combined_text = []
        for result in sorted_results:
            text = result.get('text', '').strip()
            if text:
                combined_text.append(text)
        
        return '\n'.join(combined_text)
    
    def _generate_dynamic_content(self, results: List[Dict[str, Any]], filename: str, file_type: str = "document") -> str:
        """Generate dynamic content description based on actual extracted text"""
        if not results:
            return f"No text extracted from {filename}"
        
        # Analyze the content to generate a meaningful description
        text_count = len(results)
        avg_confidence = sum(r.get('confidence', 0) for r in results) / len(results)
        
        # Get some sample text to understand content type
        sample_texts = [r.get('text', '')[:50] for r in results[:3] if r.get('text')]
        content_hint = ' '.join(sample_texts).lower()
        
        # Generate dynamic description based on content hints
        if 'prescription' in content_hint or 'medication' in content_hint:
            content_type = "prescription or medication document"
        elif 'invoice' in content_hint or 'bill' in content_hint:
            content_type = "invoice or billing document"
        elif 'form' in content_hint or 'application' in content_hint:
            content_type = "form or application document"
        elif 'letter' in content_hint or 'correspondence' in content_hint:
            content_type = "letter or correspondence"
        elif 'contract' in content_hint or 'agreement' in content_hint:
            content_type = "contract or agreement document"
        else:
            content_type = f"{file_type} document"
        
        return f"{content_type} containing {text_count} text elements with average confidence of {avg_confidence:.1%}"
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get list of supported file formats"""
        return self.supported_formats
    
    async def process_base64_image(self, base64_string: str, filename: str = "base64_image") -> Dict[str, Any]:
        """Process base64 encoded image and extract text"""
        try:
            # Remove data URL prefix if present
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            # Decode base64 to image bytes
            image_bytes = base64.b64decode(base64_string)
            
            # Process image using existing method
            return await self._process_image(image_bytes, filename)
            
        except Exception as e:
            logger.error(f"Error processing base64 image: {e}")
            return {
                "success": False,
                "error": f"Base64 image processing error: {str(e)}",
                "filename": filename
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get medical lab service information"""
        return {
            "service_name": "Medical Lab OCR Service",
            "version": "1.0.0",
            "supported_formats": self.supported_formats,
            "allowed_types": self.allowed_types,
            "openai_available": self._openai_client is not None,
            "ocr_available": True,  # PaddleOCR is always available
            "features": [
                "PDF processing (native text + OCR)",
                "Image processing (OCR)",
                "Text file processing",
                "Word document processing",
                "Base64 image processing",
                "OpenAI Vision API fallback",
                "Dynamic content analysis"
            ]
        }


# Global medical lab service instance - import this for use across the app
medical_lab_service = MedicalLabService()