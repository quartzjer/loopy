import argparse
import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
import time
import git
import sys

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

def get_git_repo():
    try:
        repo = git.Repo(".", search_parent_directories=True)
        logger.info("Git repository initialized.")
        return repo
    except git.exc.InvalidGitRepositoryError:
        logger.error("Current directory is not a valid Git repository.")
        raise

def sanitize_branch_name(name):
    clean = ''.join(c if c.isalnum() or c in '-_.' else '-' for c in name)
    clean = '-'.join(filter(None, clean.split('-')))
    clean = clean.strip('-')
    return clean or 'default'

def checkout_or_create_branch(repo, branch_name):
    if branch_name in repo.heads:
        branch = repo.heads[branch_name]
        branch.checkout()
        logger.info(f"Checked out existing branch: {branch_name}")
    else:
        branch = repo.create_head(branch_name)
        branch.checkout()
        logger.info(f"Created and checked out new branch: {branch_name}")

def commit_changes(repo, file_path, commit_message):
    try:
        repo.git.add(file_path)
        repo.index.commit(commit_message)
        logger.info(f"Committed changes to {file_path}: {commit_message}")
    except Exception as e:
        logger.error(f"Failed to commit changes: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Process text with Gemini API')
    parser.add_argument('input_file', help='Path to the input file')
    parser.add_argument('--loops', type=int, default=5, help='Number of loops to run')
    parser.add_argument('--sleep', type=int, default=10, help='Seconds to sleep between loops')
    parser.add_argument('--git', action='store_true', help='Enable git integration')
    parser.add_argument('--feedback', help='Manual feedback override (use - for stdin)')
    args = parser.parse_args()

    global logger
    logger = setup_logging()

    repo = None
    branch_name = None
    if args.git:
        try:
            repo = get_git_repo()
            base_name = os.path.basename(args.input_file)
            branch_name = sanitize_branch_name(os.path.splitext(base_name)[0])
            checkout_or_create_branch(repo, branch_name)
        except Exception as e:
            logger.error(f"Git initialization failed: {str(e)}")
            return

    try:
        editor_model, writer_model = setup_models()
        manual_feedback = None
        
        if args.feedback:
            if args.feedback == '-':
                manual_feedback = sys.stdin.read().strip()
            else:
                manual_feedback = args.feedback
            logger.info("Using manual feedback override")
        
        for i in range(args.loops):
            start_time = time.time()
            logger.info(f"{'='*50}")
            logger.info(f"Loop {i+1}/{args.loops}")
            
            if not os.path.exists(args.input_file):
                open(args.input_file, 'a').close()
            with open(args.input_file, 'r') as f:
                content = f.read()
            if not content:
                content = "Fill in story here..."
                logger.info("No content found in input file. Using placeholder text.")

            if manual_feedback and i == 0:
                editor_feedback = manual_feedback
                logger.info("Using provided manual feedback")
            else:
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
            
            if repo:
                commit_changes(repo, args.input_file, editor_feedback)
            
            loop_time = time.time() - start_time
            logger.info(f"Loop completed in {loop_time:.2f} seconds")
            
            if i < args.loops - 1:
                logger.info(f"Sleeping for {args.sleep} seconds...")
                time.sleep(args.sleep)
        
        if branch_name:
            logger.info(f"Finished all loops. You're on branch {branch_name}. You may push/PR when ready.")
        else:
            logger.info("Finished all loops.")
            
    except FileNotFoundError as e:
        logger.error(f"File not found: {e.filename}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
