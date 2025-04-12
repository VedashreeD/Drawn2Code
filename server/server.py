from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ollama import chat
import os
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app init
app = FastAPI()

# CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
IMAGE_DIR = os.path.join(os.getcwd(), "static", "images")
IMAGE_PATH = os.path.join(IMAGE_DIR, "drawing.png")  # Save as PNG

# Ensure directory exists
os.makedirs(IMAGE_DIR, exist_ok=True)


@app.post("/generate-html")
async def generate_html(image: UploadFile = File(...)):
    """
    Accepts an uploaded image, saves it, and sends a prompt with the image path to the Gemma3 model.
    """
    try:
        logger.info("Received image upload request")

        # Save uploaded image
        with open(IMAGE_PATH, "wb") as f:
            content = await image.read()
            f.write(content)
        logger.info(f"Image saved to: {IMAGE_PATH}")

        # Prepare the prompt for Gemma3
        prompt = (
        f"""
            You are a frontend developer assistant.

            You are given a **visual design image**, which represents the final look and structure of a webpage. 
            Your task is to generate the HTML and CSS code that will reproduce this exact design as a real webpage.
            Your job to only generate the HTML and CSS Code, looking at the provided image. DO NOT INCLUDE ANYTHING THAT IS NOT PART OF THE IMAGE.

        ###  Very Important:

        - Treat the design image located at {IMAGE_PATH} as the **final webpage layout** that the user wants to build.
        - You must generate HTML and CSS that will recreate the visual look, layout, text, and styling **exactly** as shown in the image.
        - The design image is your source of truth. Do not rely on assumptions or extra features — only code what you visually see in the image.

        ###  What You Should Do:

        1. **Analyze the design image carefully.**  
        Look at:
        - All visible **text** (headings, labels, buttons, etc.)
        - The **layout** and positioning of every element (e.g., top bar, center text, spacing)
        - All **colors**, **fonts**, **sizing**, **alignment**, **borders**, and other styles
        - The **overall structure** of the page (e.g., header, footer, sections, etc.)

        2. **Generate clean, semantic HTML and CSS** that accurately recreates the page:
        - Use `<nav>`, `<header>`, `<main>`, `<section>`, `<footer>` where appropriate
        - Use CSS to apply all styling
        - Recreate the same structure, alignment, spacing, and design as in the image
        - Do not include JavaScript
        - DO NOT INCLUDE ANY EXPLANATION OR COMMENTS. ONLY RETURN THE HTML AND CSS CODE.
        - DO NOT USE ANY PLACEHOLDER TEXT TO FILL BLANK SPACES. ALWAYS USE THE TEXT FROM THE IMAGE AND DO NOT FILL IN BLANK SPACE. LEAVE IT BLANK.
        - If the design contains any text, make sure to include it exactly as shown. If no visible or readable text can be extracted from the image, **leave the space empty** instead of using placeholder text like "Lorem Ipsum."

        ### Example Scenario:
        This is an example of what the image might look like and how you should respond. DO NOT USE THIS EXAMPLE AS YOUR DESIGN.
        This is just a **hypothetical** example to illustrate the task.
        Let's say the design image in `IMAGE_PATH` looks like this:

        - At the very top of the page is a horizontal navigation bar with three items:  
        `Home | Projects | Contact`
        - These items are spaced evenly and centered horizontally at the top.
        - In the middle of the page (vertically centered), it says in large bold text:  
        `Veda D`

        This is a simple personal homepage layout. Your task is to generate HTML and CSS that creates this exact design.

        ---

        ###  Expected Output:

        ```html
        <nav class="navbar">
        <ul class="nav-list">
            <li>Home</li>
            <li>Projects</li>
            <li>Contact</li>
        </ul>
        </nav>

        <main class="hero">
        <h1>Veda D</h1>
        </main>
        ```
        
        ```css
        body {{
        margin: 0;
        font-family: sans-serif;
        background-color: white;
        height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        }}

        .navbar {{
        width: 100%;
        background-color: #f5f5f5;
        padding: 20px 0;
        }}

        .nav-list {{
        list-style: none;
        display: flex;
        justify-content: center;
        gap: 40px;
        margin: 0;
        padding: 0;
        font-size: 18px;
        font-weight: 500;
        }}

        .hero {{
        flex-grow: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        }}

        .hero h1 {{
        font-size: 48px;
        font-weight: bold;
        }}
        ```
        This is your final-webpage-look : {IMAGE_PATH}
        What is the html and css code for this webpage?
        """
        )
        logger.info(f"Prompt sent to Gemma3: {prompt}")

        # Send request to Gemma3 API using Ollama chat function
        stream = chat(
            model="gemma3",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        # Collect the streamed response
        html_response = ""
        for chunk in stream:
            content = chunk.get('message', {}).get('content', "")
            if content:
                html_response += content

        if not html_response:
            logger.error("No response generated from Gemma3.")
            raise HTTPException(status_code=500, detail="Gemma3 failed to generate HTML.")

        logger.info(f"HTML generation successful: {html_response}")
        return {"html": html_response}

    except Exception as e:
        logger.error(f"Error generating HTML: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
