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
`python loop.py your_story.md`

With custom parameters:
`python loop.py input_file.md --loops 3 --sleep 15`

With Git integration:
`python loop.py input_file.md --git`

With one-time manual feedback (first run only):
`python loop.py input_file.md --feedback "Make the dialogue more natural"`
Or read feedback from stdin:
`echo "Add more conflict" | python loop.py input_file.md --feedback -`

With initial content (convenient bootstrap to create new_story.md in one go):
`python loop.py new_story.md --bootstrap "Once upon a time..."`
Or read initial content from stdin:
`cat seed_story.md | python loop.py new_story.md --bootstrap -`

## Parameters

- `input_file`: Path to the text file to process (updates in place)
- `--loops`: Number of refinement iterations (default: 5)
- `--sleep`: Seconds to wait between loops (default: 10)
- `--git`: Enable Git integration to track changes in branches
- `--feedback`: Provide one-time manual editor feedback or use '-' to read from stdin
- `--bootstrap`: Initial content for input file or use '-' to read from stdin

## Example Stories

Here are some stories created while testing Loopy:

- [Last Measurement](stories/last_measurement.md)
- [Quantum Mycelia](stories/quantum_mycelia.md)
- [The Shift](stories/the_shift.md)
- [Quantum Tapestry](stories/quantum_tapestry.md)

These using the new git tracking for each revision:

- [The Uncertainty Barrier](stories/uncertainty_barrier.md)
- [Perfect Mirror](stories/perfect_mirror.md)

## How It Works

1. The editor model analyzes the current text and provides feedback
2. The writer model receives both the original text and editor feedback
3. The writer generates an improved version
4. This process repeats for the specified number of loops

## Git Integration

When using the `--git` flag, Loopy will:
1. Create a new branch named after your input file
2. Commit changes after each refinement loop
3. Use editor feedback as commit messages
4. Leave you ready to push or create a PR when done

## TODO

I'd like to have an outer loop that loads all the existing stories into gemini and asks it to develop a novel new story unlike any existing ones but based on given themes. Then the inner loop will write/refine it and create a PR, then kick back out to the outer loop.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
