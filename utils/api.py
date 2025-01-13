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
CONTEXT = ""

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
Ejemplo 1
"Ive grown my network to 36K+ in 2024

Heres how you can build yours in 2025:

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

Networking isnt just adding numbers.

Its building relationships that matter.

P.S. Want to grow on LinkedIn?

Follow me → Daniel"


Ejemplo 2
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


Ejemplo 3
"The right niche attracts the right audience.

Here's how to find yours in 5 steps:

Most people on LinkedIn blend in because theyre trying to appeal to everyone.

But the truth is:

When you speak to everyone
↳ You connect with no one

So finding your niche isnt limiting.

→ Its freeing

Heres how you can do it ↓

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
- Whats my proven method?
- Why is my approach special?

5. Test and refine
- Does my content resonate?
- Am I attracting ideal clients?
- What feedback am I getting?

Dont try to be everything to everyone.

Be exactly what your audience needs.

♻️ Repost to help others find their niche"

Ejemplo 4
"Así es la realidad de emprender…
❌ No empecé con dinero
❌ No sabía cómo empezar
❌ Tenía mucho miedo

¿Pero cómo lo he hecho?
✅ Me he centrado en una habilidad
✅ He tomado acción
✅ Me he pasado muchas horas trabajando duro

📌 Si te ha gustado, sígueme para más contenido auténtico."


Ejemplo 5
"BREAKING: Google just launched their AI "Whisk".

& it looks like the best AI image generator:

Whisk is a new Google Labs experiment that lets you prompt using images for a fast creative process.

This is best explained by Thomas Iljic, Director of Product Management, Google Labs:

"Instead of generating images with long, detailed text prompts, Whisk lets you prompt with images. Simply drag in images, and start creating."

Here are 7 ways Whisk changes the creative game:

1. Easy to Use
↳ Just drag and drop images.
↳ No need for long text prompts.

2. Mix and Match
↳ Input images for subject, scene, and style.
↳ Create something uniquely your own.

3. Fast Results
↳ Get instant image generation.
↳ No waiting around for results.

4. Endless Possibilities
↳ From digital plushies to enamel pins.
↳ Your creativity has no limits.

5. AI-Powered
↳ Uses Googles latest image generation model, Imagen 3.
↳ Captures the essence of your subject.

6. Editable Prompts
↳ View and edit underlying prompts anytime.
↳ Ensure your project meets your expectations.

7. Creative Exploration
↳ Built for rapid visual exploration.
↳ Not a traditional image editor.

♻️ Repost this if you agree."


Ejemplo 6
"Google is crushing OpenAI.

1. Veo 2's videos are much better than Sora.
2. Google released Gemini-2.0-thinking (like o1).
3. But also Whisk, Gemini 2.0 flash, real-time AI...

But this post is about Veo 2.

☑ Longer Videos.
☑ 4K Resolution: Crystal clear visuals.
☑ Multiple characters, lifelike interactions.
☑ Smooth and professional camera handling.

Google is stealing the show from OpenAI. 

They are winning the AI race.

♻️ Repost this if you agree."

"""

@lru_cache(maxsize=50)
def generate_linkedin_post(topic: str, language: str = DEFAULT_LANGUAGE, custom_post: str = None, context: str = CONTEXT) -> str:
    """
    Generate a professional LinkedIn post using OpenAI.
    Uses caching to avoid regenerating identical requests.
    
    Args:
        topic: The subject matter for the post
        language: Target language for the post (default: English)
        custom_post: Optional example post to use as inspiration (default: None)
        context: Optional context for the post (default: CONTEXT)
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
                    f"Generate a post replicating the style of the examples, incorporating elements such as storytelling, lists, or reflections in this language: {language_prompt}"
                    "Create a strong hook: use the same style and tone as the examples."
                    "Avoid long paragraphs and stacked sentences. Use line breaks and spaces between ideas."
                    f"Develop the content: use a clear structure with short sentences, concrete examples, and adapt to the user's style. Stick to the same style and tone as the examples: {example_posts}."
                    "Always speak from personal experience and in the first person."
                    "Call to action: include a CTA that encourages interaction or invites reflection."
                    "Avoid questions in the CTA; instead, include reflections or conclusions."
                    f"Use this examples as a reference for the style and tone: {example_posts}"
                    f"Use this context for the post: {CONTEXT}"
                    "Final Check: Before finishing, ensure the content has: 1)An engaging hook. 2)A flexible and coherent structure using short sentences without paragraphs. 3)A compelling CTA."
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
            temperature=0.45
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
                        f"Generate relevant ideas: Provide 3 creative approaches to the topic, considering storytelling, lists, or reflections."
                        f"Write everything (ideas, hook, CTA) in this language:{language_instruction} "
                        "Create a strong hook: Suggest 2-3 opening lines designed to capture immediate attention."
                        "Call to action: Include a CTA that encourages interaction or invites reflection. Suggest 2-3 closing lines"
                        "Use recent news and events for reference when creating the ideas, hook and CTA. Provide a brief explanation of why it's relevant and links to the source with complete url"
                        f"Use examples {example_posts} for reference when creating the ideas, hook and CTA"
                        f"Final Check: Before finishing, ensure the content has: 1)An engaging hook. 2)A flexible and coherent structure using short sentences without paragraphs. 3)A compelling CTA. 4) Source links to the news and events 5)Make sure eveything is in this language: {language_instruction}"
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
