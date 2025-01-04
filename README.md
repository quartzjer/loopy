# Loopy

Loopy is an AI-powered creative writing assistant that uses Google's Gemini API to iteratively improve and evolve text content through multiple refinement passes.

It's designed to run at a rate under the (currently) free tier of 15 requsts per minute.

## Features

- Multiple AI-powered refinement loops
- Dual-model approach using editor and writer personas
- Configurable loop count and delay timing

## Setup

1. Install dependencies:
   `pip install google-generativeai python-dotenv`

2. Create a `.env` file with your Gemini API key (get it via [AI Studio](https://aistudio.google.com/app/apikey)):
   `GEMINI_API_KEY=your_key_here`

3. Use or modify `editor.txt` and `writer.txt` files containing your custom instructions for each AI persona.

4. Create your initial base story or story ideas and put it in a text file.

## Usage

Basic usage:
`python loop.py your_story.txt`

With custom parameters:
`python loop.py input_file.txt --loops 3 --sleep 15`

## Parameters

- `input_file`: Path to the text file to process (updates in place)
- `--loops`: Number of refinement iterations (default: 5)
- `--sleep`: Seconds to wait between loops (default: 10)

## Example Stories

Here are some stories created while testing Loopy:

- [Last Measurement](stories/last_measurement_25.txt)
- [Quantum Mycelia](stories/quantum_mycelia_25.txt)
- [The Shift](stories/the_shift_25.txt)
- [Quantum Tapestry](stories/quantum_tapestry_50.txt)

## How It Works

1. The editor model analyzes the current text and provides feedback
2. The writer model receives both the original text and editor feedback
3. The writer generates an improved version
4. This process repeats for the specified number of loops

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
