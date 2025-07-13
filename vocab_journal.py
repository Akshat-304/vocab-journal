import os
import textwrap
import google.generativeai as genai  # Google's Generative AI library
import re

# Configure the Gemini API key
genai.configure(api_key="your_actual_key_here")


def get_word_details_from_gemini(word):
    """Ask Gemini to provide the meaning and correct the word if needed."""
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = (
        f"Provide the correct spelling and meaning of the word '{word}'. in simple language"
        f"If the word is misspelled, correct it. Return the response in the following format:\n"
        f"Corrected Word: <corrected_word>\nMeaning: <meaning>"
    )

    response = model.generate_content(prompt)
    response_text = response.text.strip() if hasattr(response, 'text') else "Response failed."
    
    # Parse the response
    corrected_word = None
    meaning = None
    for line in response_text.split("\n"):
        if line.startswith("Corrected Word:"):
            corrected_word = line.replace("Corrected Word:", "").strip()
        if line.startswith("Meaning:"):
            meaning = line.replace("Meaning:", "").strip()
    
    return corrected_word or word, meaning or "Meaning not found."


def generate_story(word, meaning):
    """Generate a story using Gemini based on the word and its meaning."""
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = (
        f"The word is '{word}'. Its meaning is: {meaning}. "
        f"Write a short and simple story of around 50 words in simple language"
        f"that uses the word '{word}' in the text and illustrates its meaning naturally."
    )   

    response = model.generate_content(prompt)
    story = response.text.strip() if hasattr(response, 'text') else "Story generation failed."
    return story








def write_to_file(word, meaning, story):
    """Write the word, meaning, and story to a text file with proper numbering and formatting."""
    first_letter = word[0].upper()
    file_name = f"{first_letter}.txt"

    # Wrap the story for better readability
    wrapped_story = textwrap.fill(story, width=80)

    new_entry = (
        f"Word: {word}\n"
        f"Meaning: {meaning}\n"
        f"Story:\n{wrapped_story}"
    )

    entries = []
    
    # Read existing entries if file exists
    if os.path.exists(file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                content = file.read().strip()
                if content:
                    raw_entries = content.split("\n" + "-" * 80 )
                    # Clean and remove leading numbers from entries
                    entries = [re.sub(r'^\d+\.\s*', '', entry.strip()) for entry in raw_entries if entry.strip()]
        except UnicodeDecodeError:
            with open(file_name, "r", encoding="ISO-8859-1") as file:
                content = file.read().strip()
                if content:
                    raw_entries = content.split("\n" + "-" * 80 + "\n")
                    entries = [re.sub(r'^\d+\.\s*', '', entry.strip()) for entry in raw_entries if entry.strip()]

    # Check if the word already exists in entries
    word_exists = any(entry.startswith(f"Word: {word}") for entry in entries)
    if not word_exists:
        entries.append(new_entry)

    # Sort entries by the word alphabetically
    entries = sorted(
        entries,
        key=lambda x: x.split(': ')[1].split('\n')[0].lower() if ': ' in x and x.startswith('Word:') else ''
        )

    # Write all entries back to the file with corrected numbering
    with open(file_name, "w", encoding="utf-8") as file:
        for i, entry in enumerate(entries, start=1):
            file.write(f"{i}. {entry}\n{'-' * 80}\n")





def main():
    while True:
        word = input("Enter a word (or type 'exit' to quit): ").strip()
        if word.lower() == "exit":
            break
        if not word.isalpha():
            print("Please enter a valid word.")
            continue

        # Get corrected word and meaning from Gemini
        corrected_word, meaning = get_word_details_from_gemini(word)
        if corrected_word != word:
            print(f"Did you mean '{corrected_word}'?")

        # Generate story
        story = generate_story(corrected_word, meaning)

        # Display before saving
        print(f"\nWord: {corrected_word}")
        print(f"Meaning: {meaning}")
        print("Story:")
        print(textwrap.fill(story, width=80))
        print("-" * 80)

       
        write_to_file(corrected_word, meaning, story)


if __name__ == "__main__":
    main()
