# VAM Content Generator

A powerful tool for automatically generating professional content in multiple formats including LinkedIn posts, carousel presentations, images, YouTube scripts, and content ideas.

## 📋 Overview

The VAM Content Generator is an AI-powered Streamlit application that helps content creators, professionals, and marketers generate high-quality content. The tool leverages OpenAI's API to transform simple topic inputs into ready-to-use professional content across multiple formats.

## ✨ Features

- **Image Generation**: Create professional images with captions for your content
- **LinkedIn Carousel Creation**: Generate complete PowerPoint carousel presentations with customizable templates
- **LinkedIn Post Generation**: Create engaging LinkedIn posts in multiple styles
- **YouTube Script Generation**: Produce video scripts in various styles (Mr. Beast, Alex Hormozi, Medical, Legal, etc.)
- **Content Ideas**: Generate creative content ideas for any topic
- **Multilingual Support**: Create content in English or Spanish
- **Customizable Templates**: Use built-in templates or upload your own PowerPoint templates

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/content-creation.git
cd content-creation
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## 🚀 Usage

1. Start the Streamlit application:
```bash
streamlit run main.py
```

2. Navigate to the URL displayed in your terminal (typically http://localhost:8501)

3. Fill in your professional context:
   - Professional experience
   - Interests
   - Target audience

4. Enter your topic and select the desired:
   - Output format (Images, Carousel, LinkedIn Post, YouTube Script, Ideas)
   - Language (English or Spanish)
   - Format-specific options (template, style, etc.)

5. Click "Generate Content" and wait for the AI to produce your content

6. Download or copy the generated content for your use

## 📁 Project Structure

```
content-creation/
├── main.py                   # Main Streamlit application
├── requirements.txt          # Dependencies
├── .gitignore                # Git ignore file
├── templates/                # PowerPoint templates
│   ├── Linkedin_carousel_template_blue_en.pptx
│   ├── Linkedin_carousel_template_green_en.pptx
│   ├── Linkedin_carousel_template_orange_en.pptx
│   ├── Linkedin_carousel_template_blue_es.pptx
│   ├── Linkedin_carousel_template_green_es.pptx
│   └── Linkedin_carousel_template_orange_es.pptx
└── utils/                    # Utility modules
    ├── api.py                # API interactions with OpenAI
    ├── template_manager.py   # Template management functionality
    ├── ppt.py                # PowerPoint generation utilities
    └── images/               # Static images for the application
```

## 🛠️ Dependencies

- **openai**: AI model interactions
- **python-dotenv**: Environment variable management
- **python-pptx**: PowerPoint file generation
- **requests**: HTTP requests
- **streamlit**: Web application framework

## 🧩 How It Works

1. **Content Generation**: Leverages OpenAI API to generate content based on user input and selected format
2. **Template Management**: Handles PowerPoint templates for carousel presentations
3. **User Interface**: Streamlit-based interface for easy interaction and content generation
4. **Content Export**: Provides downloadable content in various formats

## 👤 Author

Created by Virgilio Madrid - Data Scientist

- [Portfolio](https://portfolio-vam.vercel.app/)
- [LinkedIn](https://www.linkedin.com/in/vamadrid/)
- [Email](mailto:virgiliomadrid1994@gmail.com)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- OpenAI for providing the API
- Streamlit for the web application framework
- Python community for excellent libraries
