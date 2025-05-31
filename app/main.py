# PODVOX: Personalized Podcast Outreach Engine
# Purpose: Main FastAPI application with core endpoints for personalized podcast outreach

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import logging
from app.config import settings
from app.services.sieve_service import sieve_service
from app.services.script_generation_service import script_generation_service
from app.services.elevenlabs_service import elevenlabs_service
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Hyper-personalized podcast outreach engine that generates customized voicenotes",
    version=settings.app_version,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ProspectData(BaseModel):
    """Input data for generating personalized voicenote"""
    name: str
    podcast_name: str
    episode_url: HttpUrl
    tone: Optional[str] = "casual"  # casual, formal, enthusiastic
    
class VoiceNoteResponse(BaseModel):
    """Response containing the generated voicenote"""
    prospect_name: str
    podcast_name: str
    voicenote_url: str
    script: str
    key_moments_referenced: list[str]
    duration_seconds: float
    
class MomentsExtractionResponse(BaseModel):
    """Response containing extracted moments from podcast episode"""
    prospect_name: str
    podcast_name: str
    key_moments: list[dict]
    episode_insights: dict
    total_moments_found: int

class HardshipAnalysisRequest(BaseModel):
    """Input data for analyzing hardship moments"""
    podcast_url: HttpUrl
    prospect_name: Optional[str] = None  # Defaults to SPEAKER_NAME if not provided
    tone: Optional[str] = "casual"  # casual, professional, enthusiastic, empathetic
    script_length: Optional[str] = "medium"  # short, medium, long
    generate_variations: Optional[bool] = False  # Generate multiple script variations

class ScriptGenerationRequest(BaseModel):
    """Input data for AI script generation from existing analysis"""
    prospect_name: str
    podcast_name: str
    sieve_analysis: dict
    tone: Optional[str] = "casual"
    script_length: Optional[str] = "medium"
    variations: Optional[List[dict]] = None  # For A/B testing

class VoiceGenerationRequest(BaseModel):
    """Input data for voice generation from script"""
    script: str
    voice_id: Optional[str] = None
    voice_settings: Optional[dict] = None
    output_format: Optional[str] = "mp3"

class CompleteVoicenoteRequest(BaseModel):
    """Input data for complete pipeline: Analysis → Script → Voice"""
    podcast_url: HttpUrl
    prospect_name: Optional[str] = None
    tone: Optional[str] = "casual"
    script_length: Optional[str] = "medium"
    voice_id: Optional[str] = None
    voice_settings: Optional[dict] = None

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.app_name} - Personalized Podcast Outreach Engine",
        "version": settings.app_version,
        "features": {
            "sieve_integration": "✅ Advanced podcast content analysis",
            "ai_script_generation": "✅ OpenAI GPT-4o powered personalized scripts",
            "voice_generation": "✅ ElevenLabs high-quality voice synthesis",
            "complete_pipeline": "✅ End-to-end: Podcast → Script → Voice"
        },
        "endpoints": {
            "healthcheck": "/healthcheck",
            "complete_voicenote_pipeline": "/generate-complete-voicenote",
            "analyze_hardship_moments": "/analyze-hardship-moments", 
            "generate_ai_script": "/generate-ai-script",
            "generate_voice": "/generate-voice",
            "list_voices": "/list-voices",
            "extract_moments": "/extract-moments",
            "docs": "/docs"
        }
    }

# Health check endpoint
@app.get("/healthcheck")
async def healthcheck():
    """Service health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "apis": {
            "sieve": bool(settings.sieve_api_key),
            "openai": bool(settings.openai_api_key),
            "elevenlabs": bool(settings.elevenlabs_api_key)
        },
        "pipeline_ready": all([
            settings.sieve_api_key,
            settings.openai_api_key,
            settings.elevenlabs_api_key
        ])
    }

# Complete voicenote generation pipeline
@app.post("/generate-complete-voicenote")
async def generate_complete_voicenote(request: CompleteVoicenoteRequest):
    """
    Complete end-to-end pipeline: Podcast Analysis → AI Script → Voice Generation
    
    This is the full PODVOX workflow:
    1. Analyze podcast for hardship moments (Sieve)
    2. Generate personalized script (OpenAI GPT-4o)
    3. Convert script to high-quality voice (ElevenLabs)
    """
    try:
        logger.info("🚀 Starting complete voicenote generation pipeline")
        logger.info(f"   🎯 Target: {request.prospect_name or 'Default speaker'}")
        logger.info(f"   📺 Podcast: {request.podcast_url}")
        logger.info(f"   🎭 Tone: {request.tone}")
        
        # Step 1: Sieve Analysis
        logger.info("📋 STEP 1: SIEVE HARDSHIP ANALYSIS")
        sieve_analysis = await sieve_service.analyze_hardship_moments(
            podcast_url=str(request.podcast_url),
            prospect_name=request.prospect_name
        )
        
        if sieve_analysis["total_moments"] == 0:
            raise HTTPException(
                status_code=404, 
                detail="No hardship moments found in podcast - cannot generate personalized voicenote"
            )
        
        prospect_name = sieve_analysis["speaker_analyzed"]
        logger.info(f"✅ Found {sieve_analysis['total_moments']} hardship moments for {prospect_name}")
        
        # Step 2: AI Script Generation
        logger.info("🤖 STEP 2: AI SCRIPT GENERATION")
        ai_script = await script_generation_service.generate_hardship_outreach_script(
            prospect_name=prospect_name,
            podcast_name="Podcast",  # Could extract from URL analysis
            sieve_analysis=sieve_analysis,
            tone=request.tone,
            script_length=request.script_length
        )
        
        logger.info(f"✅ Generated {ai_script['word_count']}-word script ({ai_script['estimated_duration_seconds']}s)")
        
        # Step 3: Voice Generation
        logger.info("🎙️ STEP 3: VOICE GENERATION")
        voicenote_result = await elevenlabs_service.generate_voicenote_with_ai_script(
            ai_script_data=ai_script,
            voice_id=request.voice_id,
            voice_settings=request.voice_settings
        )
        
        logger.info("🎉 Complete pipeline successful!")
        
        return {
            "status": "success",
            "pipeline": "Complete PODVOX Workflow",
            "prospect_name": prospect_name,
            "results": voicenote_result,
            "pipeline_steps": {
                "1_sieve_analysis": f"Found {sieve_analysis['total_moments']} hardship moments",
                "2_ai_script": f"Generated {ai_script['word_count']}-word personalized script",
                "3_voice_generation": f"Created voicenote: {voicenote_result['voicenote']['audio_file_path']}"
            },
            "download_info": {
                "audio_file": voicenote_result['voicenote']['audio_file_path'],
                "format": voicenote_result['voicenote']['format'],
                "duration": voicenote_result['voicenote']['estimated_duration_seconds'],
                "file_size": voicenote_result['voicenote']['file_size_bytes']
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error in complete voicenote pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Voice generation endpoint
@app.post("/generate-voice")
async def generate_voice(request: VoiceGenerationRequest):
    """
    Generate voice from script using ElevenLabs
    
    Takes a text script and converts it to high-quality audio using ElevenLabs TTS.
    """
    try:
        logger.info(f"🎙️ Generating voice from script ({len(request.script)} characters)")
        
        voicenote_result = await elevenlabs_service.generate_voicenote_from_script(
            script=request.script,
            voice_id=request.voice_id,
            voice_settings=request.voice_settings,
            output_format=request.output_format
        )
        
        return {
            "status": "success",
            "voicenote": voicenote_result,
            "message": "Voice generated successfully",
            "download_url": f"/download-audio/{voicenote_result['audio_file_path'].split('/')[-1]}"
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating voice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# List available voices
@app.get("/list-voices")
async def list_voices():
    """Get list of available ElevenLabs voices"""
    try:
        voices_data = await elevenlabs_service.list_available_voices()
        return {
            "status": "success",
            "voices": voices_data
        }
    except Exception as e:
        logger.error(f"❌ Error listing voices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Download audio file endpoint
@app.get("/download-audio/{filename}")
async def download_audio(filename: str):
    """Download generated audio file"""
    try:
        # For security, validate the filename
        temp_dir = os.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return FileResponse(
            path=file_path,
            media_type="audio/mpeg",
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"❌ Error downloading audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Script Generation endpoint
@app.post("/generate-ai-script")
async def generate_ai_script(request: ScriptGenerationRequest):
    """
    Generate AI-powered personalized outreach scripts from existing Sieve analysis
    
    This endpoint takes rich Sieve analysis data and uses OpenAI to generate
    compelling, personalized outreach scripts that reference specific podcast moments.
    """
    try:
        logger.info(f"🤖 Generating AI script for {request.prospect_name}")
        
        if request.variations and len(request.variations) > 0:
            # Generate multiple variations for A/B testing
            scripts = await script_generation_service.generate_multiple_variations(
                prospect_name=request.prospect_name,
                podcast_name=request.podcast_name,
                sieve_analysis=request.sieve_analysis,
                variations=request.variations
            )
            
            return {
                "status": "success",
                "prospect_name": request.prospect_name,
                "script_variations": scripts,
                "total_variations": len(scripts),
                "recommendation": "Test different variations to see which performs best"
            }
        else:
            # Generate single script
            script = await script_generation_service.generate_hardship_outreach_script(
                prospect_name=request.prospect_name,
                podcast_name=request.podcast_name,
                sieve_analysis=request.sieve_analysis,
                tone=request.tone,
                script_length=request.script_length
            )
            
            return {
                "status": "success",
                "prospect_name": request.prospect_name,
                "script": script,
                "generation_metadata": {
                    "model": "gpt-4o",
                    "tone": request.tone,
                    "length": request.script_length,
                    "format": "short_casual_under_20_seconds"
                }
            }
            
    except Exception as e:
        logger.error(f"❌ Error generating AI script: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced endpoint with AI script generation
@app.post("/analyze-hardship-moments")
async def analyze_hardship_moments(request: HardshipAnalysisRequest):
    """
    Complete workflow: Find hardship moments → Get detailed insights → Generate AI scripts
    
    This endpoint demonstrates the enhanced Moments → Ask → AI Script pipeline:
    1. Use Moments API to find timestamps where hardship is discussed
    2. Use Ask API with detailed markdown prompts for structured analysis
    3. Use OpenAI to generate compelling, personalized outreach scripts
    """
    try:
        logger.info(f"🚀 Starting complete hardship analysis + AI script generation for {request.prospect_name or 'default speaker'}")
        
        # Step 1 & 2: Run the complete hardship analysis workflow
        sieve_analysis = await sieve_service.analyze_hardship_moments(
            podcast_url=str(request.podcast_url),
            prospect_name=request.prospect_name
        )
        
        # Step 3: Generate AI-powered scripts if we found hardship moments
        ai_scripts = []
        if sieve_analysis["hardship_moments"]:
            prospect_name = sieve_analysis["speaker_analyzed"]
            
            if request.generate_variations:
                # Generate multiple script variations
                logger.info("🎭 Generating multiple AI script variations...")
                ai_scripts = await script_generation_service.generate_multiple_variations(
                    prospect_name=prospect_name,
                    podcast_name="Podcast",  # Could extract from URL analysis
                    sieve_analysis=sieve_analysis
                )
            else:
                # Generate single optimized script
                logger.info("🤖 Generating single AI-optimized script...")
                script = await script_generation_service.generate_hardship_outreach_script(
                    prospect_name=prospect_name,
                    podcast_name="Podcast",
                    sieve_analysis=sieve_analysis,
                    tone=request.tone,
                    script_length=request.script_length
                )
                ai_scripts = [script]
        
        return {
            "status": "success",
            "workflow_completed": "Sieve Analysis + AI Script Generation",
            "sieve_analysis": sieve_analysis,
            "ai_generated_scripts": ai_scripts,
            "workflow_steps": {
                "1_moments_extraction": f"Found {sieve_analysis['total_moments']} hardship moments",
                "2_ask_analysis": f"Analyzed {len(sieve_analysis['detailed_insights'])} moments with detailed prompts",
                "3_ai_script_generation": f"Generated {len(ai_scripts)} AI-powered script(s)"
            },
            "technologies_used": {
                "content_analysis": "Sieve Moments + Ask APIs",
                "script_generation": "OpenAI GPT-4o",
                "prompt_engineering": "Short casual format prompts",
                "format": "Under 20 seconds, casual voicenotes"
            },
            "next_step": {
                "message": "Use /generate-voice endpoint to convert scripts to audio",
                "example_payload": {
                    "script": ai_scripts[0]["script"] if ai_scripts else "No script generated",
                    "voice_id": "optional_custom_voice_id",
                    "output_format": "mp3"
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error in complete hardship analysis workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# New endpoint for testing Sieve integration
@app.post("/extract-moments", response_model=MomentsExtractionResponse)
async def extract_moments(prospect: ProspectData):
    """
    Extract key moments from a podcast episode using Sieve APIs
    
    Args:
        prospect: ProspectData containing name, podcast name, and episode URL
        
    Returns:
        MomentsExtractionResponse with extracted moments and insights
    """
    try:
        logger.info(f"Extracting moments for {prospect.name} from {prospect.podcast_name}")
        
        # Extract contextual moments using Sieve service
        extracted_data = await sieve_service.extract_contextual_moments(
            podcast_url=str(prospect.episode_url),
            prospect_name=prospect.name,
            podcast_name=prospect.podcast_name
        )
        
        return MomentsExtractionResponse(
            prospect_name=extracted_data["prospect_name"],
            podcast_name=extracted_data["podcast_name"],
            key_moments=extracted_data["key_moments"],
            episode_insights=extracted_data["episode_insights"],
            total_moments_found=extracted_data["total_moments_found"]
        )
        
    except Exception as e:
        logger.error(f"Error extracting moments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to extract moments: {str(e)}")

# Legacy function kept for compatibility
def generate_personalized_script(
    prospect_name: str,
    podcast_name: str, 
    key_moments: list[dict],
    tone: str = "casual"
) -> str:
    """
    Legacy function for basic script generation (replaced by AI service)
    """
    if not key_moments:
        return f"Hey {prospect_name}, I listened to your recent episode of {podcast_name} and found it really insightful!"
    
    primary_moment = key_moments[0]
    
    if tone == "formal":
        script = f"""Hello {prospect_name},

I recently listened to your episode of {podcast_name} and was particularly struck by your discussion around {primary_moment['timestamp_formatted']} about {primary_moment['query']}. 

Your insights resonated with me, and I would welcome the opportunity to connect and share some thoughts.

Best regards"""
        
    elif tone == "enthusiastic":
        script = f"""Hey {prospect_name}! 

Just finished listening to your latest {podcast_name} episode and WOW! The part at {primary_moment['timestamp_formatted']} where you talked about {primary_moment['query']} absolutely blew my mind!

I have some thoughts I'd love to share with you - would love to connect!"""
        
    else:  # casual (default)
        script = f"""Hey {prospect_name},

I was listening to your recent {podcast_name} episode and really connected with what you said around {primary_moment['timestamp_formatted']} about {primary_moment['query']}.

It got me thinking and I'd love to share some thoughts. Would be great to connect!"""
    
    return script

# Run the application (for development)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    ) 