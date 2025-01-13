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
    generate_ideas
)
from utils.ppt import create_carousel_presentation
from utils.template_manager import initialize_templates, get_available_templates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
       

""", unsafe_allow_html=True)

# Initialize session state
# Initialize PowerPoint templates
initialize_templates()
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = {
        'images': None,
        'carousel': None,
        'linkedin': None,
        'ideas': None
    }


with st.sidebar:
    st.sidebar.image("utils/images/vamc3.png", width=300, use_container_width=False)
    st.markdown("""
    ### Virgilio Madrid
    ### Data Scientist
    ### virgiliomadrid1994@gmail.com
    ### https://www.linkedin.com/in/vamadrid/
    """)
    st.markdown("""
    ### Enter context for better results
    """)
    with st.container():
        col1 = st.columns(1)
        with col1:
            experience = st.text_input("Enter your professional experiece", placeholder="e.g., Engineer with 10 years of experience in AWS",default="")
            achievements = st.text_input("Enter your achievements", placeholder="e.g., I won the hackathon in 2024, I built a startup named VAM, I build a AI tool to generate content",default="")
            interests = st.text_input("Enter your interests", placeholder="e.g., I'm interested in AI, Machine Learning, Data Science, Cloud Computing, Startups, Entrepreneurship, etc.",default="general interests")
            audience = st.text_input("Enter your audience", placeholder="e.g., general public, tech enthusiasts, entrepreneurs, founders, etc.",default="general public")
    
    context = f"Experience: {experience}\nAchievements: {achievements}\nInterests: {interests}\nAudience: {audience}"

# Title and description
st.title("VAM Content Generator")
st.markdown("Generate professional content in multiple formats for your topic.")


# Input section
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Enter your topic", placeholder="e.g., Aws vs Azure vs Google Cloud")
    with col2:
        language = st.selectbox(
            "Select language",
            ["English", "Spanish (Honduras)"],
            index=0
        )
    col3, col4 = st.columns(2)
    with col3:
        output_format = st.selectbox(
            "Select output format",
            ["Images", "Carousel", "LinkedIn Post", "Ideas"],
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
                    logger.info("Generating carousel presentation")
                    carousel_content = generate_carousel_content(topic, language, carousel_type=carousel_type)
                    
                    # Get template path based on selection
                    if template_option == "Upload Custom Template":
                        if not uploaded_file:
                            raise Exception("Please upload a PowerPoint template first")
                        template_path = os.path.join("templates", uploaded_file.name)
                    else:
                        template_path = os.path.join("templates", f"{template}.pptx")
                    
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
                linkedin_post = generate_linkedin_post(topic, language, custom_post_content)
                st.session_state.generated_content['linkedin'] = linkedin_post
                logger.info("Successfully generated LinkedIn post")

            elif output_format == "Ideas":
                logger.info("Generating content ideas")
                ideas = generate_ideas(topic, language)
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
        st.download_button(
            label="Download Presentation",
            data=st.session_state.generated_content['carousel'],
            file_name=f"{topic.replace(' ', '_')}_presentation.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
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