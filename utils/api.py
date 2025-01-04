import os
import json
import logging
from typing import List, Dict, Optional, TypedDict
from functools import lru_cache
from openai import OpenAI
from datetime import datetime, timedelta

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
OPENAI_MODEL = "gpt-4o"  # Released May 13, 2024 - do not change unless requested
DALLE_MODEL = "dall-e-3"
DEFAULT_IMAGE_SIZE = "1024x1024"
MAX_TOKENS = 2000
DEFAULT_LANGUAGE = "English"
DEFAULT_NUM_SLIDES = 10
DEFAULT_CAROUSEL_TYPE = "3-4 bullet points"

class ImageResponse(TypedDict):
    url: str
    description: str

class SlideContent(TypedDict):
    title: str
    points: List[str]

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OpenAI API key is not set in environment variables.")
    raise ValueError("OpenAI API key is required")

openai = OpenAI(api_key=OPENAI_API_KEY)

@lru_cache(maxsize=100)
def generate_images(topic: str, limit: int = 3) -> List[ImageResponse]:
    """
    Generate professional images using OpenAI DALL-E related to a topic.
    Uses caching to avoid regenerating identical requests.
    
    Args:
        topic: The subject matter for image generation
        limit: Maximum number of images to generate (default: 3)
        
    Returns:
        List of ImageResponse containing image URLs and descriptions
        
    Raises:
        ValueError: If the API response is invalid
        Exception: For other API-related errors
    """
    logger.info(f"Generating {limit} images via OpenAI DALL-E for topic: {topic}")
    
    try:
        images: List[ImageResponse] = []
        for i in range(limit):
            logger.debug(f"Generating image {i+1}/{limit}")
            response = openai.images.generate(
                model=DALLE_MODEL,
                prompt=f"Professional, high-quality image representing: {topic}. "
                       f"Ensure the image is clear, well-composed, and suitable for business presentations.",
                n=1,
                size=DEFAULT_IMAGE_SIZE,
                quality="standard",
                style="natural"
            )
            
            if not response.data:
                logger.warning(f"Empty response for image {i+1}")
                continue
                
            image_url = response.data[0].url
            images.append({
                "url": image_url,
                "description": f"Professional visualization of {topic}"
            })
            logger.info(f"Generated image {i+1}: {image_url[:50]}...")
            
        if not images:
            raise ValueError("No images were generated successfully")
            
        logger.info(f"Successfully generated {len(images)} images")
        return images
            
    except Exception as e:
        error_msg = f"Failed to generate images via OpenAI: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)

@lru_cache(maxsize=200)
def generate_image_caption(image_description: str, max_length: int = 50) -> str:
    """
    Generate a creative and professional caption for an image using OpenAI.
    Uses caching to avoid regenerating identical requests.
    
    Args:
        image_description: Description of the image to caption
        max_length: Maximum length of the caption in tokens
        
    Returns:
        A creative and professional caption string
        
    Raises:
        ValueError: If the API response is invalid
        Exception: For other API-related errors
    """
    logger.info(f"Generating caption for image: {image_description[:50]}...")
    
    try:
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": ("Create a professional, engaging, and concise caption "
                              "that highlights the key aspects of the image. "
                              "The caption should be suitable for business presentations.")
                },
                {"role": "user", "content": f"Generate a caption for: {image_description}"}
            ],
            max_tokens=max_length,
            temperature=0.7
        )
        
        if not response.choices:
            raise ValueError("No caption generated in API response")
            
        caption = response.choices[0].message.content.strip()
        logger.info(f"Generated caption: {caption[:50]}...")
        return caption
        
    except Exception as e:
        error_msg = f"Failed to generate image caption: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)

@lru_cache(maxsize=50)
def generate_linkedin_post(topic: str, language: str = DEFAULT_LANGUAGE) -> str:
    """
    Generate a professional LinkedIn post using OpenAI.
    Uses caching to avoid regenerating identical requests.
    
    Args:
        topic: The subject matter for the post
        language: Target language for the post (default: English)
        
    Returns:
        A formatted LinkedIn post string
        
    Raises:
        ValueError: If the API response is invalid
        Exception: For other API-related errors
    """
    logger.info(f"Generating LinkedIn post for topic: {topic} in {language}")
    
    try:
        language_prompt = ("in Spanish, using the dialect from Honduras" 
                         if language == "Spanish (Honduras)" else "in English")
        
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Create a professional LinkedIn post {language_prompt}. "
                        "The post should be engaging, informative, and follow "
                        "LinkedIn best practices including appropriate hashtags "
                        "and clear paragraph breaks."
                        "Avoid using cliches or overused phrases."
                        "Avoid being too salesy or promotional. Use a human and conversational tone."
                    )
                },
                {"role": "user", "content": f"Write a LinkedIn post about: {topic}"}
            ],
            max_tokens=MAX_TOKENS,
            temperature=0.7
        )
        
        if not response.choices:
            raise ValueError("No content generated in API response")
            
        post_content = response.choices[0].message.content.strip()
        logger.info("Successfully generated LinkedIn post")
        return post_content
        
    except Exception as e:
        error_msg = f"Failed to generate LinkedIn post: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)

@lru_cache(maxsize=50)
def generate_carousel_content(
    topic: str,
    language: str = DEFAULT_LANGUAGE,
    num_slides: int = DEFAULT_NUM_SLIDES,
    carousel_type: str = DEFAULT_CAROUSEL_TYPE
) -> List[SlideContent]:
    """
    Generate content for carousel slides using OpenAI.
    Uses caching to avoid regenerating identical requests.
    
    Args:
        topic: The subject matter for the carousel
        language: Target language for the content
        num_slides: Number of slides to generate
        carousel_type: Type of content structure for each slide
        
    Returns:
        List of SlideContent containing titles and bullet points
    """
    logger.info(f"Generating carousel content: {num_slides} slides about '{topic}' in {language}")
    
    try:
        language_prompt = ("in Spanish, using the dialect from Honduras" 
                         if language == "Spanish (Honduras)" else "in English")
        
        # Modify content guidelines based on carousel_type
        content_format = {
            "3-4 bullet points": "Include 3-4 concise bullet points per slide",
            "2 Paragraphs": "Include 2 short paragraphs per slide",
            "1 Paragraph + 3-4 bullet points": "Include 1 short paragraph followed by 3-4 concisebullet points per slide"
        }.get(carousel_type, "Include 3-4 bullet points per slide")
        
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Create content for {num_slides} presentation slides {language_prompt}.\n"
                        "Follow these guidelines:\n"
                        "1. Each slide should have a clear, concise title\n"
                        f"2. {content_format}\n"
                        "3. Maintain consistent narrative flow\n"
                        "4. Use professional language\n"
                        "Return a JSON object with this structure:\n"
                        '{"slides": [{"title": "string", "points": ["string"]}]}'
                    )
                },
                {"role": "user", "content": f"Create presentation content about: {topic}"}
            ],
            response_format={"type": "json_object"},
            max_tokens=MAX_TOKENS,
            temperature=0.7
        )
        
        content = json.loads(response.choices[0].message.content)
        
        # Validate response structure
        if not isinstance(content, dict) or 'slides' not in content:
            raise ValueError("API response missing 'slides' array")
            
        slides = content['slides']
        if not slides or not isinstance(slides, list):
            raise ValueError("No slides content was generated")
            
        # Validate and clean each slide
        validated_slides: List[SlideContent] = []
        for i, slide in enumerate(slides):
            if not isinstance(slide, dict):
                logger.warning(f"Skipping invalid slide {i}: not a dictionary")
                continue
                
            if not slide.get('title') or not isinstance(slide['points'], list):
                logger.warning(f"Skipping invalid slide {i}: missing title or points")
                continue
                
            if not slide['points']:
                logger.warning(f"Skipping slide {i}: no bullet points")
                continue
                
            validated_slides.append({
                'title': slide['title'].strip(),
                'points': [point.strip() for point in slide['points'] if point.strip()]
            })
            
        if not validated_slides:
            raise ValueError("No valid slides were generated")
            
        logger.info(f"Successfully generated {len(validated_slides)} slides")
        return validated_slides
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON response from API: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Failed to generate carousel content: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)
