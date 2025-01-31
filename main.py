import streamlit as st
import os
import io
import tempfile
import zipfile
import logging
from utils.api import (
    generate_images,
    generate_image_caption,
    generate_linkedin_post,
    generate_carousel_content,
    generate_ideas,
    generate_youtube_script
)
from utils.ppt import create_carousel_presentation
from utils.template_manager import initialize_templates, get_available_templates
from pptx import Presentation

# Add these constants near the top of the file with other constants/configurations
DEFAULT_NUM_SLIDES = 6  # or whatever default number you want

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_template_slide_count(template_path: str) -> int:
    """
    Get the number of slides in the PowerPoint template.
    
    Args:
        template_path: Path to the PowerPoint template
        
    Returns:
        Number of slides in the template
    """
    try:
        prs = Presentation(template_path)
        return len(prs.slides)
    except Exception as e:
        logger.error(f"Error reading template slides: {str(e)}")
        return 0

# Configure page
st.set_page_config(
    page_title="VAM Content Generator",
    page_icon="💥",
    layout="wide"
)

# Add custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .output-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
       

    /* Add these new styles */
    .stContainer {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    
    .stTextInput > div > div > input {
        background-color: white;
    }
    
    .stTextArea > div > div > textarea {
        background-color: white;
    }
    
    .element-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
# Initialize PowerPoint templates
initialize_templates()
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = {
        'images': None,
        'carousel': None,
        'linkedin': None,
        'ideas': None,
        'youtube_script': None
    }


with st.sidebar:
    st.sidebar.image("utils/images/vamc3.png", width=300, use_container_width=False)
    st.markdown("""
    ### Virgilio Madrid
    ### Data Scientist
    """)
    st.link_button("LinkedIn 💼", "https://www.linkedin.com/in/vamadrid/")
    st.link_button("Tutorial 📺", "https://share.descript.com/view/RZBrKJV7tMj")
    st.link_button("Email 📧", "mailto:virgiliomadrid1994@gmail.com")
    st.info("""
    ### VAM Content Generator
    Is a tool that helps you create: LinkedIn posts, LinkedIn carousel presentations, images and generate ideas.
    """)
    


# Title and description
st.title("VAM Content Generator")
st.markdown("Generate professional content in multiple formats for your topic.")
st.markdown("""
    ### Context Section
    """)

professional_experience = st.text_area("Enter your professional experience and accomplishments", placeholder="e.g., Engineer, with 10 years of experience in the field of data science and machine learning", value="Engineer, MBA, and master in AI, skilled in data science, automation with python and artificial intelligence. Building AI solutions for saving time and money")
interests = st.text_area("Enter your interests", placeholder="e.g., data science, machine learning, artificial intelligence, cloud computing, marketing, etc.", value="data science, machine learning, artificial intelligence, automation, python")
audience = st.text_input("Enter your audience", placeholder="e.g., founders, investors, entrepreneurs, etc.", value="general public")
context = ("professional experience: " + professional_experience + " interests: " + interests + " audience: " + audience)
st.markdown("""
    ### Input Section
    """)
# Input section
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Enter your topic", placeholder="e.g., Aws vs Azure vs Google Cloud")
    with col2:
        language = st.selectbox(
            "Select language",
            ["English", "Spanish (Neutral)"],
            index=0
        )
    col3, col4 = st.columns(2)
    with col3:
        output_format = st.selectbox(
            "Select output format",
            ["Images", "Carousel", "LinkedIn Post", "YouTube Script", "Ideas"],
            index=0,
            key="output_format"
        )
    with col4:
        if output_format == "Carousel":
            template_option = st.radio(
                "Template Source",
                ["Use Default Templates", "Upload Custom Template"],
                key="template_source"
            )
            
            if template_option == "Use Default Templates":
                available_templates = get_available_templates()
                template = st.selectbox(
                    "Select presentation template",
                    available_templates,
                    index=0,
                    key="template_selection"
                )
                st.info(f"Available templates: {', '.join(available_templates)}")
            else:
                uploaded_file = st.file_uploader("Upload PowerPoint Template (.pptx)", type="pptx", key="template_upload")
                if uploaded_file:
                    # Save the uploaded template
                    template_path = os.path.join("templates", uploaded_file.name)
                    with open(template_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    template = uploaded_file.name.rsplit('.', 1)[0]
                    st.success(f"Template uploaded successfully: {template}")

            carousel_type = st.selectbox(
            "Select carousel content type per slide",
            ["3-4 bullet points", "2 Paragraphs", "1 Paragraph + 3-4 bullet points"],
            index=0,
            key="carousel_type"
        )
        if output_format == "LinkedIn Post":
            post_type = st.selectbox(
            "Select LinkedIn post type",
            ["default", "set custom"],
            index=0,
            key="post_type"
            )
            
            if post_type == "set custom":
                custom_post = st.text_area("Enter your custom LinkedIn post as inspiration", placeholder="e.g., Enter a post that you want to use as inspiration")
# Generate button
if st.button("Generate Content", disabled=not topic):
    with st.spinner("Generating content..."):
        try:
            logger.info(f"Starting content generation for topic: {topic}")
            # Generate content based on selected format
            if output_format == "Images":
                try:
                    logger.info("Generating images and captions")
                    images = generate_images(topic)
                    captions = [generate_image_caption(img.get('description', '')) for img in images]
                    st.session_state.generated_content['images'] = {'images': images, 'captions': captions}
                    logger.info(f"Successfully generated {len(images)} images with captions")
                except Exception as e:
                    logger.error(f"Failed to generate images: {str(e)}")
                    error_msg = str(e)
                    if "Rate limit" in error_msg:
                        st.warning("⚠️ Unable to generate images: OpenAI API rate limit reached. Please try again in a few minutes.")
                    elif "billing" in error_msg.lower():
                        st.warning("⚠️ Unable to generate images: OpenAI API billing issue. Please check your account balance.")
                    elif "invalid api key" in error_msg.lower():
                        st.warning("⚠️ Unable to generate images: Invalid OpenAI API key. Please verify your API key is correct.")
                    else:
                        st.warning(f"⚠️ Unable to generate images: The image generation service is currently unavailable. Error: {str(e)}")
                    st.session_state.generated_content['images'] = None

            elif output_format == "Carousel":
                try:
                    # Get template path and slide count before generating content
                    if template_option == "Upload Custom Template":
                        if not uploaded_file:
                            raise Exception("Please upload a PowerPoint template first")
                        template_path = os.path.join("templates", uploaded_file.name)
                    else:
                        template_path = os.path.join("templates", f"{template}.pptx")
                    
                    # Get number of slides in template
                    template_slide_count = get_template_slide_count(template_path)-2
                    if template_slide_count == 0:
                        st.error("Invalid template or no slides found in template")
                        st.stop()
                        
                    # Adjust num_slides to match template
                    num_slides = template_slide_count
                    st.info(f"Generating {num_slides} slides to match template capacity")
                    
                    logger.info("Generating carousel presentation")
                    carousel_content = generate_carousel_content(
                        topic, 
                        language, 
                        num_slides=num_slides,
                        carousel_type=carousel_type, 
                        context=context
                    )
                    st.session_state.carousel_content = carousel_content
                    
                    # Verify template exists
                    if not os.path.exists(template_path):
                        logger.warning(f"Template not found: {template_path}")
                        raise Exception(f"Template file not found: {template_path}")
                    
                    # Create presentation using selected template
                    presentation = create_carousel_presentation(topic, carousel_content, template_path)
                    
                    # Save presentation to bytes
                    pptx_bytes = io.BytesIO()
                    presentation.save(pptx_bytes)
                    st.session_state.generated_content['carousel'] = pptx_bytes.getvalue()
                    logger.info("Successfully generated carousel presentation")
                except Exception as e:
                    logger.error(f"Failed to generate carousel: {str(e)}")
                    st.error(f"Unable to generate the carousel presentation: {str(e)}")
                    st.session_state.generated_content['carousel'] = None

            elif output_format == "LinkedIn Post":
                logger.info("Generating LinkedIn post") #this is the post that will be generated
                custom_post_content = custom_post if post_type == "set custom" else None
                linkedin_post = generate_linkedin_post(topic, language, custom_post_content, context=context)
                st.session_state.generated_content['linkedin'] = linkedin_post
                logger.info("Successfully generated LinkedIn post")

            elif output_format == "YouTube Script":
                logger.info("Generating YouTube script")
                script_content = generate_youtube_script(
                    topic, 
                    language,
                    context=context
                )
                st.session_state.generated_content['youtube_script'] = script_content
                logger.info("Successfully generated YouTube script")

            elif output_format == "Ideas":
                logger.info("Generating content ideas")
                ideas = generate_ideas(topic, language, context=context)
                st.session_state.generated_content['ideas'] = ideas
                logger.info("Successfully generated content ideas")

        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            st.error(f"Configuration error: {str(e)}")
            st.info("Please make sure all required API keys are set in the environment variables.")
            st.stop()
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            st.error(f"Error generating content: {str(e)}")
            st.stop()

# Display generated content
if output_format == "Images":
    st.subheader("📸 Generated Images with Captions")
    if st.session_state.generated_content['images']:
        images = st.session_state.generated_content['images']['images']
        captions = st.session_state.generated_content['images']['captions']
        
        cols = st.columns(3)
        for idx, (img, caption) in enumerate(zip(images, captions)):
            with cols[idx % 3]:
                st.image(img['url'], caption=caption, use_container_width=True)

elif output_format == "Carousel":
    st.subheader("🎯 Carousel Presentation")
    if st.session_state.generated_content['carousel']:
        # Store carousel_content in session state when it's generated
        if 'carousel_content' not in st.session_state:
            st.session_state.carousel_content = carousel_content
            
        with st.expander("Edit Carousel Slides", expanded=True):
            edited_slides = []
            for idx, slide in enumerate(st.session_state.carousel_content):
                st.markdown(f"### Slide {idx + 1}")
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Create a card-like container for each slide
                        with st.container():
                            st.markdown("##### Title")
                            edited_title = st.text_input(
                                "Edit title",
                                value=slide['title'],
                                key=f"title_{idx}"
                            )
                            
                            st.markdown("##### Content")
                            points_text = "\n".join(slide['points'])
                            edited_points = st.text_area(
                                "Edit points (one per line)",
                                value=points_text,
                                height=150,
                                key=f"points_{idx}"
                            )
                            
                            edited_points_list = [p.strip() for p in edited_points.split('\n') if p.strip()]
                            
                            edited_slides.append({
                                'title': edited_title,
                                'points': edited_points_list
                            })
                    
                    with col2:
                        st.markdown("##### Preview")
                        st.markdown(f"**{edited_title}**")
                        for point in edited_points_list:
                            st.markdown(f"• {point}")
                    
                st.markdown("---")
            
            # Store the edited slides in session state
            st.session_state.edited_slides = edited_slides
            
            # Update the presentation with edited content
            if st.button("Update Presentation", key="update_presentation"):
                try:
                    # Get template path based on selection
                    if template_option == "Upload Custom Template":
                        if not uploaded_file:
                            raise Exception("Please upload a PowerPoint template first")
                        template_path = os.path.join("templates", uploaded_file.name)
                    else:
                        template_path = os.path.join("templates", f"{template}.pptx")
                    
                    # Create updated presentation using edited_slides
                    updated_presentation = create_carousel_presentation(topic, st.session_state.edited_slides, template_path)
                    
                    # Save presentation to bytes
                    pptx_bytes = io.BytesIO()
                    updated_presentation.save(pptx_bytes)
                    st.session_state.generated_content['carousel'] = pptx_bytes.getvalue()
                    st.success("Presentation updated successfully!")
                except Exception as e:
                    st.error(f"Error updating presentation: {str(e)}")
        
        # Download button - will use the most recently updated content
        st.download_button(
            label="Download Presentation",
            data=st.session_state.generated_content['carousel'],
            file_name="presentation.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation" #this is the file type for pptx
        )


elif output_format == "LinkedIn Post":
    st.subheader("💼 LinkedIn Post")
    if st.session_state.generated_content['linkedin']:
        with st.expander("View LinkedIn Post", expanded=True):
            st.markdown(st.session_state.generated_content['linkedin'])
            st.download_button(
                label="Download LinkedIn Post",
                data=st.session_state.generated_content['linkedin'],
                file_name=f"{topic.replace(' ', '_')}_linkedin_post.txt",
                mime="text/plain"
            )
            
elif output_format == "YouTube Script":
    st.subheader("🎥 YouTube Script")
    if st.session_state.generated_content['youtube_script']:
        with st.expander("Edit Script", expanded=True):
            edited_slides = []
            total_sections = len(st.session_state.generated_content['youtube_script'])
            
            for idx, slide in enumerate(st.session_state.generated_content['youtube_script']):
                st.markdown(f"### Section {idx + 1}/{total_sections}")
                
                with st.container():
                    # Create a card-like container for each section
                    with st.container():
                        st.markdown("##### Title")
                        edited_title = st.text_input(
                            "Edit section title",
                            value=slide['title'],
                            key=f"yt_title_{idx}"
                        )
                        
                        st.markdown("##### Script")
                        edited_script = st.text_area(
                            "Edit script content",
                            value=slide['script'],
                            height=150,
                            key=f"yt_script_{idx}"
                        )
                        
                        edited_slides.append({
                            'title': edited_title,
                            'script': edited_script
                        })
                    
                st.markdown("---")
            
            # Store the edited script in session state
            st.session_state.edited_youtube_script = edited_slides
            
            # Download button for the script
            if st.button("Download Script"):
                script_text = ""
                for idx, slide in enumerate(st.session_state.edited_youtube_script):
                    script_text += f"\nSection {idx + 1}: {slide['title']}\n"
                    script_text += f"{slide['script']}\n"
                    script_text += "-" * 40 + "\n"
                
                st.download_button(
                    label="Download Script as Text",
                    data=script_text,
                    file_name=f"{topic.replace(' ', '_')}_youtube_script.txt",
                    mime="text/plain"
                )

elif output_format == "Ideas":
    st.subheader("💡 Content Ideas")
    if st.session_state.generated_content['ideas']:
        with st.expander("View Content Ideas", expanded=True):
            st.markdown(st.session_state.generated_content['ideas'])
            st.download_button(
                label="Download Ideas",
                data=st.session_state.generated_content['ideas'],
                file_name=f"{topic.replace(' ', '_')}_content_ideas.txt",
                mime="text/plain"
            )

# Footer
st.markdown("---")
st.markdown("VAM Content Creation Tool")

