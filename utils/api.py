import os
import json
import logging
from typing import List, Dict, Optional, TypedDict
from functools import lru_cache
from openai import OpenAI
from datetime import datetime, timedelta
import requests

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

# Add this constant with the other constants
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
if not PERPLEXITY_API_KEY:
    logger.error("Perplexity API key is not set in environment variables.")
    raise ValueError("Perplexity API key is required")

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

example_posts = """
Ejemplo 1 (Inglés)
"I’ve grown my network to 36K+ in 2024

Here’s how you can build yours in 2025:

1. Start with likes
↳ Likes are the easiest way to get noticed

2. Drop comments
↳ Shows support and makes you likeable

3. Build your tribe
↳ Connect with people who interact with you

4. Slide into DMs
↳ Start a conversation with a kind message

5. Go for a coffee
↳ Build trust and support each other's goals

6. Team up
↳ Collaborate on posts to reach new people

Networking isn’t just adding numbers.

It’s building relationships that matter.

P.S. Want to grow on LinkedIn?

Follow me → Daniel"


Ejemplo 2 (Español)
"Nunca hay que parar de formarse...


Y más cuando estás empezando tu Startup (es un buen reto).

Ayer le di una vuelta a mis KPIs, y aprendí lo siguiente:

Tienen que ser:

- Medibles y entendibles
- Transparentes
- Ambiciosos pero realistas
- Vinculados a la NSM (North Star Metric)
- En un horizonte temporal
- Revisables

En nuestro caso al ser un SaaS, podríamos definir:

Captar 500 usuarios de pago en los primeros 3 meses tras el lanzamiento.

Tengo que seguir dándole vueltas, la semana que viene os cuento por donde pueden ir los tiros.

Hay que actuar, pero hay que formarse también.

Si puedes evitar cagarla, mejor ;)"


Ejemplo 3 (Inglés)
"The right niche attracts the right audience.

Here's how to find yours in 5 steps:

Most people on LinkedIn blend in because they’re trying to appeal to everyone.

But the truth is:

When you speak to everyone
↳ You connect with no one

So finding your niche isn’t limiting.

→ It’s freeing

Here’s how you can do it ↓

1. Identify your expertise
- What skills set me apart?
- What problems do I solve?
- What do people ask me for?

2. Clarify your audience
- Who benefits the most?
- What roles do I relate to?
- Who do I enjoy working with?

3. Define the problem
- What keeps them stuck?
- What result are they after?
- What frustrates them most?

4. Describe your solution
- What result do I deliver?
- What’s my proven method?
- Why is my approach special?

5. Test and refine
- Does my content resonate?
- Am I attracting ideal clients?
- What feedback am I getting?

Don’t try to be everything to everyone.

Be exactly what your audience needs.

♻️ Repost to help others find their niche"

Ejemplo 4 (Español)
"
"Así es la realidad de emprender…
❌ No empecé con dinero
❌ No sabía cómo empezar
❌ Tenía mucho miedo

¿Pero cómo lo he hecho?
✅ Me he centrado en una habilidad
✅ He tomado acción
✅ Me he pasado muchas horas trabajando duro

📌 Si te ha gustado, sígueme para más contenido auténtico."
"
"""

@lru_cache(maxsize=50)
def generate_linkedin_post(topic: str, language: str = DEFAULT_LANGUAGE, custom_post: str = None) -> str:
    """
    Generate a professional LinkedIn post using OpenAI.
    Uses caching to avoid regenerating identical requests.
    
    Args:
        topic: The subject matter for the post
        language: Target language for the post (default: English)
        custom_post: Optional example post to use as inspiration (default: None)
        
    Returns:
        A formatted LinkedIn post string
    """
    logger.info(f"Generating LinkedIn post for topic: {topic} in {language}")
    
    try:
        language_prompt = ("in Spanish, using the dialect from Honduras" 
                         if language == "Spanish (Honduras)" else "in English")
        
        messages = [
            {
                "role": "system",
                "content": (
                    f"Act as a writing specialist for LinkedIn posts and create an engaging LinkedIn post in this language: {language_prompt}. "
                    "Use short phrases and lists, do not use paragraphs"
                    "Use clear and concise language"
                    "Avoid using cliches or overused phrases. "
                    "Avoid being too salesy or promotional. Use a human and conversational tone."
                    "CTA should be a reflection of the post or a conclusion, not a sales pitch. "
                    "At the end of the post, add: 'Follow me → {your name}' or 'Sigueme para mas → {tu nombre}'"
                    "Use little emojis to make the post more engaging for example--> ❌,✅,📌,♻️"
                    "Use this examples as a reference for the style and tone: {example_posts}"
                )
            }
        ]

        if custom_post:
            messages.append({
                "role": "system",
                "content": f"Use this post as inspiration for the style and format, mantaining the same rythm, tone and use correct spacing between each line: {custom_post}"
            })

        messages.append({"role": "user", "content": f"Write a LinkedIn post about: {topic}"})

        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
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
            "1 Paragraph + 3-4 bullet points": "Include 1 short paragraph and 3 concise bullet points per slide"
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
                        "4. Use informative, educational and engaging language\n"
                        "5. Use storytelling\n"
                        "6. Give real examples\n"
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

@lru_cache(maxsize=50)
def generate_ideas(topic: str, language: str = DEFAULT_LANGUAGE) -> str:
    """
    Generate content ideas using Perplexity API.
    
    Args:
        topic: The subject matter for idea generation
        language: Target language for the ideas
        
    Returns:
        A formatted string containing generated ideas
    """
    logger.info(f"Generating ideas for topic: {topic} in {language}")
    
    try:
        url = "https://api.perplexity.ai/chat/completions"
        
        language_instruction = ("in Spanish, using the dialect from Honduras" 
                              if language == "Spanish (Honduras)" else "in English")
        
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"You are a creative content strategist. Generate 10 unique content ideas {language_instruction} "
                        "for the given topic. Each idea should be creative, specific, and actionable. "
                        "Format the response with bullet points and include a brief description for each idea."
                    )
                },
                {
                    "role": "user",
                    "content": f"Generate content ideas for: {topic}"
                }
            ],
            "temperature": 0.7,
            "top_p": 0.9,
            "return_images": False,
            "return_related_questions": False,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        content = response.json()
        if not content.get('choices') or not content['choices'][0].get('message', {}).get('content'):
            raise ValueError("No content generated in API response")
            
        ideas = content['choices'][0]['message']['content']
        logger.info("Successfully generated ideas")
        return ideas
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to generate ideas via Perplexity API: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)
