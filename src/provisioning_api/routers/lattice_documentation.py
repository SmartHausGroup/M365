"""
🏗️ LATTICE DOCUMENTATION ROUTER - M365 Integration for Central Documentation Hub! 🎯

This router provides M365 integration endpoints for:
- LATTICE repository documentation automation
- LQL, LEF, and AIOS documentation updates
- Public-facing documentation generation
- Cross-layer documentation coordination
- Zero manual documentation updates required
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Optional, Any
import json
import logging
from datetime import datetime

# Import LATTICE documentation automation
from ..automation.lattice_repo_documentation_automation import (
    LatticeRepositoryDocumentationAutomation, 
    LATTICE_DOC_AUTOMATION_CONFIG
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/lattice/documentation", tags=["LATTICE Documentation Automation"])

# Initialize LATTICE documentation automation
lattice_doc_automation = LatticeRepositoryDocumentationAutomation(LATTICE_DOC_AUTOMATION_CONFIG)

@router.get("/status")
async def get_lattice_documentation_status():
    """
    🏗️ Get LATTICE Documentation Automation Status
    
    Returns the current status of LATTICE documentation automation
    """
    try:
        logger.info("📊 Getting LATTICE Documentation Status...")
        
        status = lattice_doc_automation.get_documentation_status()
        status["timestamp"] = datetime.now().isoformat()
        
        logger.info("✅ LATTICE Documentation Status Retrieved!")
        return status
        
    except Exception as e:
        logger.error(f"Error getting LATTICE documentation status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get LATTICE documentation status: {str(e)}")

@router.get("/layers")
async def get_documentation_layers():
    """
    📚 Get Documentation Layers Status
    
    Returns the status of all documentation layers (LQL, LEF, AIOS)
    """
    try:
        logger.info("📚 Getting Documentation Layers Status...")
        
        layers_status = {}
        for layer_name in ["LQL", "LEF", "AIOS"]:
            layer_status = lattice_doc_automation.get_layer_documentation_status(layer_name)
            if layer_status:
                layers_status[layer_name] = layer_status
        
        response = {
            "layers": layers_status,
            "total_layers": len(layers_status),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("✅ Documentation Layers Status Retrieved!")
        return response
        
    except Exception as e:
        logger.error(f"Error getting documentation layers status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get documentation layers status: {str(e)}")

@router.get("/layers/{layer_name}")
async def get_layer_documentation_status(layer_name: str):
    """
    📚 Get Specific Layer Documentation Status
    
    Returns the documentation status for a specific layer (LQL, LEF, or AIOS)
    """
    try:
        logger.info(f"📚 Getting {layer_name} Documentation Status...")
        
        layer_status = lattice_doc_automation.get_layer_documentation_status(layer_name.upper())
        
        if layer_status:
            response = {
                "layer": layer_status,
                "timestamp": datetime.now().isoformat()
            }
        else:
            response = {
                "layer": layer_name.upper(),
                "status": "NOT_FOUND",
                "message": f"Layer {layer_name} not found",
                "timestamp": datetime.now().isoformat()
            }
        
        logger.info(f"✅ {layer_name} Documentation Status Retrieved!")
        return response
        
    except Exception as e:
        logger.error(f"Error getting {layer_name} documentation status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get {layer_name} documentation status: {str(e)}")

@router.get("/public")
async def get_public_documentation_status():
    """
    🌐 Get Public Documentation Status
    
    Returns the status of all public-facing documentation
    """
    try:
        logger.info("🌐 Getting Public Documentation Status...")
        
        public_status = lattice_doc_automation.get_public_documentation_status()
        public_status["timestamp"] = datetime.now().isoformat()
        
        logger.info("✅ Public Documentation Status Retrieved!")
        return public_status
        
    except Exception as e:
        logger.error(f"Error getting public documentation status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get public documentation status: {str(e)}")

@router.post("/automation/start")
async def start_lattice_documentation_automation(background_tasks: BackgroundTasks):
    """
    🚀 Start LATTICE Documentation Automation
    
    Starts the LATTICE documentation automation system in the background
    """
    try:
        logger.info("🚀 Starting LATTICE Documentation Automation...")
        
        # Start automation in background
        background_tasks.add_task(lattice_doc_automation.start_documentation_automation)
        
        response = {
            "status": "STARTING",
            "message": "LATTICE Documentation Automation is starting in the background",
            "timestamp": datetime.now().isoformat(),
            "capabilities": [
                "Automatic LQL documentation updates",
                "Automatic LEF documentation updates",
                "Automatic AIOS documentation updates",
                "Public documentation generation",
                "Cross-layer documentation coordination"
            ]
        }
        
        logger.info("✅ LATTICE Documentation Automation Starting!")
        return response
        
    except Exception as e:
        logger.error(f"Error starting LATTICE documentation automation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start LATTICE documentation automation: {str(e)}")

@router.post("/automation/stop")
async def stop_lattice_documentation_automation():
    """
    🛑 Stop LATTICE Documentation Automation
    
    Stops the LATTICE documentation automation system
    """
    try:
        logger.info("🛑 Stopping LATTICE Documentation Automation...")
        
        lattice_doc_automation.stop_documentation_automation()
        
        response = {
            "status": "STOPPED",
            "message": "LATTICE Documentation Automation has been stopped",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("✅ LATTICE Documentation Automation Stopped!")
        return response
        
    except Exception as e:
        logger.error(f"Error stopping LATTICE documentation automation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop LATTICE documentation automation: {str(e)}")

@router.get("/updates")
async def get_documentation_updates():
    """
    📝 Get Documentation Updates Status
    
    Returns the status of all documentation updates
    """
    try:
        logger.info("📝 Getting Documentation Updates Status...")
        
        status = lattice_doc_automation.get_documentation_status()
        
        response = {
            "updates": status["updates"],
            "total_updates": status["updates"]["total_updates"],
            "pending_updates": status["updates"]["pending_updates"],
            "completed_updates": status["updates"]["completed_updates"],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("✅ Documentation Updates Status Retrieved!")
        return response
        
    except Exception as e:
        logger.error(f"Error getting documentation updates status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get documentation updates status: {str(e)}")

@router.get("/dashboard")
async def get_lattice_documentation_dashboard():
    """
    📊 Get LATTICE Documentation Dashboard
    
    Returns comprehensive dashboard data for LATTICE documentation automation
    """
    try:
        logger.info("📊 Getting LATTICE Documentation Dashboard...")
        
        # Gather all dashboard data
        overall_status = lattice_doc_automation.get_documentation_status()
        layers_status = {}
        for layer_name in ["LQL", "LEF", "AIOS"]:
            layer_status = lattice_doc_automation.get_layer_documentation_status(layer_name)
            if layer_status:
                layers_status[layer_name] = layer_status
        
        public_status = lattice_doc_automation.get_public_documentation_status()
        
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status["overall_status"],
            "automation_running": overall_status["automation_running"],
            "layers": {
                "total_layers": len(layers_status),
                "layers_status": layers_status,
                "up_to_date_layers": len([l for l in layers_status.values() if l["documentation_status"] == "up_to_date"]),
                "needs_update_layers": len([l for l in layers_status.values() if l["documentation_status"] == "needs_update"])
            },
            "public_documentation": {
                "total_documents": public_status["total_documents"],
                "generated_documents": public_status["generated_documents"],
                "pending_documents": public_status["pending_documents"],
                "generation_rate": (public_status["generated_documents"] / public_status["total_documents"] * 100) if public_status["total_documents"] > 0 else 0
            },
            "updates": overall_status["updates"],
            "capabilities": [
                "Automatic LQL documentation updates",
                "Automatic LEF documentation updates",
                "Automatic AIOS documentation updates",
                "Public documentation generation",
                "Cross-layer documentation coordination",
                "Zero manual documentation updates required"
            ]
        }
        
        logger.info("✅ LATTICE Documentation Dashboard Retrieved!")
        return dashboard
        
    except Exception as e:
        logger.error(f"Error getting LATTICE documentation dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get LATTICE documentation dashboard: {str(e)}")

@router.get("/layers/{layer_name}/documentation")
async def get_layer_documentation_files(layer_name: str):
    """
    📁 Get Layer Documentation Files
    
    Returns the documentation files for a specific layer
    """
    try:
        logger.info(f"📁 Getting {layer_name} Documentation Files...")
        
        layer_status = lattice_doc_automation.get_layer_documentation_status(layer_name.upper())
        
        if layer_status:
            response = {
                "layer": layer_name.upper(),
                "documentation_path": f"docs/layers/{layer_name.lower()}",
                "files_count": layer_status["files_count"],
                "last_update": layer_status["last_update"],
                "status": layer_status["documentation_status"],
                "repository": layer_status["repository"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            response = {
                "layer": layer_name.upper(),
                "status": "NOT_FOUND",
                "message": f"Layer {layer_name} not found",
                "timestamp": datetime.now().isoformat()
            }
        
        logger.info(f"✅ {layer_name} Documentation Files Retrieved!")
        return response
        
    except Exception as e:
        logger.error(f"Error getting {layer_name} documentation files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get {layer_name} documentation files: {str(e)}")

@router.get("/public/{document_type}")
async def get_public_documentation_info(document_type: str):
    """
    🌐 Get Public Documentation Information
    
    Returns information about a specific type of public documentation
    """
    try:
        logger.info(f"🌐 Getting Public Documentation Info for {document_type}...")
        
        public_status = lattice_doc_automation.get_public_documentation_status()
        
        # Find the document by type
        document_info = None
        for doc_title, doc_data in public_status["documents"].items():
            if document_type.lower() in doc_title.lower():
                document_info = {
                    "title": doc_title,
                    "type": document_type,
                    "status": doc_data["status"],
                    "last_generated": doc_data["last_generated"],
                    "target_audience": doc_data["target_audience"],
                    "content_type": doc_data["content_type"]
                }
                break
        
        if document_info:
            response = {
                "document": document_info,
                "timestamp": datetime.now().isoformat()
            }
        else:
            response = {
                "document_type": document_type,
                "status": "NOT_FOUND",
                "message": f"Document type {document_type} not found",
                "timestamp": datetime.now().isoformat()
            }
        
        logger.info(f"✅ Public Documentation Info Retrieved for {document_type}!")
        return response
        
    except Exception as e:
        logger.error(f"Error getting public documentation info for {document_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get public documentation info: {str(e)}")

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    ❤️ LATTICE Documentation Health Check
    
    Returns the health status of the LATTICE documentation automation system
    """
    try:
        return {
            "status": "HEALTHY",
            "service": "LATTICE Documentation Automation",
            "timestamp": datetime.now().isoformat(),
            "message": "LATTICE Documentation Automation System is running and healthy!"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")
