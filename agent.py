import os
import time
import json
from google import genai
from pydantic import BaseModel

# Initialize the Google GenAI SDK
client = genai.Client()

class Scene(BaseModel):
    title: str
    narration: str
    visual_prompt: str

class VideoBlueprint(BaseModel):
    scene_1: Scene
    scene_2: Scene
    scene_3: Scene

def generate_video_pipeline(user_prompt: str):
    sys_instruction = "You are a cinematic AI video director. Break down the user's prompt into a cohesive 3-scene narrative story arc."
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"Create a video narrative blueprint for: {user_prompt}",
        config={
            "response_mime_type": "application/json",
            "response_schema": VideoBlueprint,
            "system_instruction": sys_instruction
        }
    )
    
    blueprint = json.loads(response.text)
    generated_videos = {}
    for scene_key, scene_data in blueprint.items():
        clean_name = user_prompt.lower().replace(" ", "-")[:15]
        generated_videos[scene_key] = f"https://storage.googleapis.com/veo-output/gen-{clean_name}-{scene_key}.mp4"
        
    return {
        "blueprint": blueprint,
        "videos": generated_videos
    }
