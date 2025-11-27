"""
Configuration file for PDF to Image Generator
"""
import os

# API Configuration - 从系统环境变量获取，如果没有则使用默认值
API_KEY = os.getenv('POE_API_KEY', '')
BASE_URL = os.getenv('BASE_URL', 'https://api.poe.com/v1')
MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-3-pro')
NANO_BANANA_MODEL = os.getenv('NANO_BANANA_MODEL', 'nano-banana-pro')

# File paths - 使用相对于当前脚本文件的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(current_dir, 'output')
TEMP_DIR = os.path.join(current_dir, 'temp')

# Create directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Prompt templates
PROMPT_TEMPLATES = {
    "Nature风": """**Role:** You are a Senior Academic Designer specializing in creating scientific posters for top-tier journals like Nature and Science.

**Task:** Read the uploaded PDF and generate a detailed text-to-image prompt to create a horizontal "Scientific Poster" or "Graphical Abstract" that visually summarizes the paper.

**Step 1: Precise Content Extraction**
 Analyze the paper and extract the following details. **You must be precise—do not use vague adjectives.**

1. **Title:** The exact paper title.
2. **Metadata for Footer:**
   - **Affiliation:** The primary university or research lab.
   - **Authors:** The first author's name + "et al."
   - **Venue & Year:** The journal/conference name and publication year.
3. **Left Panel Content (Split into Background & Data):**
   - **Top - The Context:** What is the context? What is the specific pain point or gap? (Visual metaphors: e.g., noisy data, diseased tissue, bottleneck).
   - **Bottom - The Data Source:** Search the text for **exact quantitative details**. Look for:
     - **Specific Dataset Names** (e.g., "COCO", "MIMIC-III", "UK Biobank").
     - **Exact Sample Sizes/Numbers** (e.g., "N=12,450", "500 hours", "100k images").
     - *Note: Do not use terms like "massive" or "large-scale"; extract the actual numbers.*
4. **Center Column Content (The Method/Core Mechanism/Study Design):** How was it solved? (Visuals: Flowchart, architecture diagram, chemical process, step-by-step pipeline).
5. **Right Column Content (Results & Conclusion):**  What is the outcome? (Visuals: Clean bar charts, comparison graphs, clear images, performance metrics).

**Step 2: Construct the Image Prompt**
Write a prompt for an AI image generator (like DALL-E 3). The prompt must strictly follow a Three-Column Layout (Triptych) structure with a Header and Footer.

**Structure of the Output Prompt:**
 Please write the final prompt in a single code block. The prompt must include:

- **Composition:** "A professional wide scientific poster layout divided into three distinct vertical panels (Left, Center, Right) on a clean white background. The layout includes a clear Header at the top and a distinct Footer at the bottom."
- **Top Header:** "The title '[Insert Title Here]' written clearly at the top in modern sans-serif font."
- **Left Panel (Split Layout):**
  - **Instruction:** "Divide the Left Panel horizontally into two distinct sections:"
  - **Top Section (Context - approx 75% height):** Describe visuals representing the Background and Problem. Use darker or chaotic tones to represent the 'problem state'.
  - **Bottom Section (Data Source - approx 25% height):** A compact, separate box or area below the context. It must feature icons representing databases or files (e.g., folder icons, grid of thumbnails). **Crucially, include the text '[Insert Exact Dataset Name/Size extracted from Step 1]' clearly in this bottom section.** (e.g., text "N=12,450" or "Dataset: ImageNet").
- **Center Panel (The Solution):** Describe the Method. This should be the largest or most detailed section, featuring a technical diagram, flowchart, or schematic.
- **Right Panel (The Result):** Describe the Results. Use bright, clean, and organized visuals (graphs, checkmarks, clear structures) to represent the 'solution state'.
- **Bottom Footer:** "A distinct, narrow horizontal footer bar at the very bottom of the poster. It contains three text elements: 
  - Bottom Left: Text '[Insert Author Affiliation]' (e.g., University Logo or Name).
  - Bottom Center: Text '[Insert Main Authors]' (e.g., Smith et al.).
  - Bottom Right: Text '[Insert Conference/Journal & Year]'."
- **Cohesion:** “Use a sophisticated Morandi color palette (muted, desaturated, low-saturation academic tones). Analyze the topic to select a fitting primary hue (e.g., Sage Green for nature, Dusty Blue for tech, Muted Terracotta for humanities), paired with white backgrounds. The style should be flat vector illustration mixed with 3D isometric elements, high readability, clean lines, minimal text clutter. --ar 16:9”

**Output Format:**

1. **Summary:** A short bulleted list of the extracted content (Problem, exact numbers/names you found for the dataset, Method, Result) so I can verify your understanding.
2. **The Prompt:** The final image generation prompt inside a code block.""",
    
    "2D扁平": """Role: You are a Senior Academic Designer specializing in creating scientific posters for top-tier journals like Nature and Science.

Task: Read the uploaded PDF and generate a detailed text-to-image prompt to create a horizontal "Scientific Poster" or "Graphical Abstract" that visually summarizes the paper.

Step 1: Content Extraction
Analyze the paper and extract the following to ensure the visual summary is accurate:
1. Title: The exact paper title.
2. Metadata for Footer (New Requirement):
    - Affiliation: The primary university or research lab (e.g., MIT, Google DeepMind).
    - Authors: The first author's name + "et al." (or top 2 authors if space permits).
    - Venue & Year: The journal/conference name and publication year (e.g., CVPR 2024, Nature 2023).
3. **Left Panel Content (Split into Background & Data):**
   - **Top - The Context:** What is the context? What is the specific pain point or gap? (Visual metaphors: e.g., noisy data, diseased tissue, bottleneck).
   - **Bottom - The Data Source:** Search the text for **exact quantitative details**. Look for:
     - **Specific Dataset Names** (e.g., "COCO", "MIMIC-III", "UK Biobank").
     - **Exact Sample Sizes/Numbers** (e.g., "N=12,450", "500 hours", "100k images").
     - *Note: Do not use terms like "massive" or "large-scale"; extract the actual numbers.*
4. Center Column Content (The Method/Core Mechanism): How was it solved? (Visuals: Flowchart, architecture diagram, chemical process, step-by-step pipeline).
5. Right Column Content (Results & Conclusion): What is the outcome? (Visuals: Clean bar charts, comparison graphs, clear images, performance metrics).
  
Step 2: Construct the Image Prompt
Write a prompt for an AI image generator (like DALL-E 3). The prompt must strictly follow a Three-Column Layout (Triptych) structure with a Header and Footer.

Structure of the Output Prompt:
Please write the final prompt in a single code block. The prompt must include:
- Composition: "A professional wide scientific poster layout divided into three distinct vertical panels (Left, Center, Right) on a **pure white background**. Content should be organized inside **clean rounded-corner rectangular containers (cards)** with subtle drop shadows, resembling a modern UI design."
- Top Header: "The title '[Insert Title Here]' written clearly at the top in modern sans-serif font."
- **Left Panel (Split Layout):**
  - **Instruction:** "Divide the Left Panel horizontally into two distinct sections:"
  - **Top Section (Context - approx 75% height):** Describe visuals representing the Background and Problem. Use darker or chaotic tones to represent the 'problem state'.
  - **Bottom Section (Data Source - approx 25% height):** A compact, separate box or area below the context. It must feature icons representing databases or files (e.g., folder icons, grid of thumbnails). **Crucially, include the text '[Insert Exact Dataset Name/Size extracted from Step 1]' clearly in this bottom section.** (e.g., text "N=12,450" or "Dataset: ImageNet").
- Center Panel (The Solution): Describe the Method. This should be the largest section, featuring a **clear flowchart with arrows connecting steps**, utilizing flat vector icons (e.g., gears, neural networks, molecules).
- Right Panel (The Result): Describe the Results inside a rounded card. Use **simplified bar charts or comparison graphs** with a clear 'check mark' or upward trend to represent success.
- Bottom Footer: "A distinct, narrow horizontal footer bar at the very bottom of the poster. It contains three text elements: 
  1. Bottom Left: Text '[Insert Author Affiliation]' (e.g., University Logo or Name).
  2. Bottom Center: Text '[Insert Main Authors]' (e.g., Smith et al.).
  3. Bottom Right: Text '[Insert Conference/Journal & Year]'."
- Cohesion: "Use a **Modern Flat UI Illustration style**. **Analyze the topic to select a fitting primary hue** (e.g., Tech Blue for AI, Sage Green for Bio, Slate Grey for Theory) to color the container borders and headers. **Crucially, use a warm contrasting color (like Orange or Coral) for highlights, arrows, and key results**, similar to the reference style. The background must remain **pure white**. Visuals should be 2D flat vector graphics, clean lines, high readability, minimal text clutter. --ar 16:9"
  
Output Format:
1. Summary: A short bulleted list of the extracted content (Problem, Method, Result) so I can verify your understanding.
2. The Prompt: The final image generation prompt inside a code block."""
}