#!/usr/bin/env python3
import os
import argparse
from pathlib import Path
from ollama import Client
from openai import OpenAI

def run_query(system_prompt, user_prompt, model="SpeakLeash/bielik-11b-v2.3-instruct:Q8_0", api_key=None):
    """Run a single query through Ollama or OpenAI with proper system and user prompts"""
    try:
        if api_key:
            # Use OpenAI API
            client = OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            return response.choices[0].message.content
        else:
            # Use Ollama
            client = Client()

            response = client.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            return response['message']['content']
    except Exception as e:
        api_type = "OpenAI" if api_key else "Ollama"
        return f"Error running {api_type}: {e}"

def main():
    parser = argparse.ArgumentParser(description="Batch process prompts with Ollama or OpenAI")
    parser.add_argument("--system", "-s", required=True, help="System prompt file or text")
    parser.add_argument("--input-dir", "-i", required=True, help="Directory containing query prompt files")
    parser.add_argument("--output-dir", "-o", required=True, help="Directory to save outputs")
    parser.add_argument("--model", "-m", default="SpeakLeash/bielik-11b-v2.3-instruct:Q8_0", help="Model to use (default: Bielik11B for Ollama)")
    parser.add_argument("--api-key", help="OpenAI API key (if provided, uses OpenAI API instead of Ollama)")

    args = parser.parse_args()

    # Load system prompt
    if os.path.isfile(args.system):
        with open(args.system, 'r', encoding='utf-8') as f:
            system_prompt = f.read().strip()
    else:
        system_prompt = args.system

    # Create output directory if it doesn't exist
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # Process all files in input directory
    input_path = Path(args.input_dir)
    if not input_path.exists():
        print(f"Error: Input directory {args.input_dir} does not exist")
        return

    processed = 0
    failed = 0

    for query_file in input_path.iterdir():
        if query_file.is_file():
            try:
                # Read query content
                with open(query_file, 'r', encoding='utf-8') as f:
                    user_prompt = f.read().strip()

                print(f"Processing {query_file.name}...")

                # Run inference
                output = run_query(system_prompt, user_prompt, args.model, args.api_key)

                # Save output
                output_file = Path(args.output_dir) / query_file.name
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(output)

                print(f"Saved output to {output_file}")
                processed += 1

            except Exception as e:
                print(f"Error processing {query_file.name}: {e}")
                failed += 1

    print(f"\nDone! Processed: {processed}, Failed: {failed}")

if __name__ == "__main__":
    main()
