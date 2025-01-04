import argparse
import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
import time

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("loopy")

def load_instructions(filepath):
    with open(filepath, "r") as f:
        return f.read().strip()

def setup_models():
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    editor_instructions = load_instructions('./editor.txt')
    writer_instructions = load_instructions('./writer.txt')
    
    editor_model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
        system_instruction=editor_instructions
    )

    writer_model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
        system_instruction=writer_instructions
    )
    
    return editor_model, writer_model

def process_content(model, content, history=[], stage=""):
    try:
        logger.info(f"Starting {stage} processing")
        chat = model.start_chat(history=history)
        response = chat.send_message(content)
        return response.text
    except Exception as e:
        logger.error(f"API Error during {stage}: {str(e)}")
        return content

def main():
    parser = argparse.ArgumentParser(description='Process text with Gemini API')
    parser.add_argument('input_file', help='Path to the input file')
    parser.add_argument('--loops', type=int, default=5, help='Number of loops to run')
    parser.add_argument('--sleep', type=int, default=10, help='Seconds to sleep between loops')
    args = parser.parse_args()

    global logger
    logger = setup_logging()

    try:
        logger.info(f"Starting processing with {args.loops} loops {args.sleep} seconds apart")
        logger.info(f"Input file: {args.input_file}")
        editor_model, writer_model = setup_models()
        
        for i in range(args.loops):
            start_time = time.time()
            logger.info(f"{'='*50}")
            logger.info(f"Loop {i+1}/{args.loops}")
            
            with open(args.input_file, 'r') as f:
                content = f.read()
            
            editor_feedback = process_content(
                editor_model,
                content,
                stage="editor"
            )
            
            logger.info("Editor Feedback:")
            logger.info("-" * 30)
            print(editor_feedback)
            logger.info("-" * 30)
            
            final_content = process_content(
                writer_model,
                content,
                history=[{
                    "role": "user",
                    "parts": [editor_feedback],
                }],
                stage="writer"
            )
            
            with open(args.input_file, 'w') as f:
                f.write(final_content)
            
            loop_time = time.time() - start_time
            logger.info(f"Loop completed in {loop_time:.2f} seconds")
            
            if i < args.loops - 1:
                logger.info(f"Sleeping for {args.sleep} seconds...")
                time.sleep(args.sleep)
                
    except FileNotFoundError as e:
        logger.error(f"File not found: {e.filename}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
