import nltk
from textblob import TextBlob, Word
from nltk.corpus import wordnet as wn
import pronouncing
import eng_to_ipa as ipa
import inflect
from pattern.text.en import conjugate, PAST, PARTICIPLE

nltk.download('wordnet')
nltk.download('omw-1.4')

p = inflect.engine()

def get_easy_definition(word):
    synsets = wn.synsets(word)
    if not synsets or synsets[0] is None:
        return None

    pos = synsets[0].pos()  # noun, verb, etc.
    definition = synsets[0].definition()
    synonyms = set()
    for s in synsets[:2]:
        if s is not None:
            for lemma in s.lemmas():
                synonyms.add(lemma.name().replace("_", " "))

    return {
        'definition': definition,
        'synonyms': list(synonyms)[:5],
        'pos': pos
    }

def make_simpler(text):
    blob = TextBlob(text)
    return str(blob.correct())

def get_pronunciation(word):
    ipa_pron = ipa.convert(word)
    arpabet_list = pronouncing.phones_for_word(word)
    arpabet = arpabet_list[0] if arpabet_list else None
    return ipa_pron, arpabet

def get_word_forms(word, pos):
    forms = ""

    if pos == 'v':  # Verb
        past = conjugate(word, tense=PAST) or "(unknown)"
        past_participle = conjugate(word, tense=PARTICIPLE) or "(unknown)"
        forms += f"\n🔁 **Past Simple**: {past}"
        forms += f"\n🔁 **Past Participle**: {past_participle}"

    elif pos == 'n':  # Noun
        plural = p.plural(word)
        forms += f"\n🔢 **Singular**: {word}"
        forms += f"\n🔢 **Plural**: {plural if plural else '(unknown)'}"

    return forms

def explain_word(word):
    info = get_easy_definition(word)
    if not info:
        return f"❌ Sorry, I don't understand the word '{word}' yet."

    easy_def = make_simpler(info['definition'])
    synonyms = ', '.join(info['synonyms'])

    ipa_pron, arpabet = get_pronunciation(word)
    ipa_pron = ipa_pron if ipa_pron else "Not available"
    arpabet = arpabet if arpabet else "Not available"

    forms = get_word_forms(word, info['pos'])

    response = (
        f"📘 **Word**: {word.capitalize()}\n"
        f"📖 **Part of Speech**: {info['pos'].upper()}\n"
        f"🔊 **Pronunciation** (IPA): /{ipa_pron}/\n"
        f"🔤 **Simple Meaning**: {easy_def}\n"
        f"🟢 **Synonyms**: {synonyms}\n"
        f"{forms}\n"
        f"💬 **Example**: \"I saw a {word} in the story.\"\n"
    )
    return response

def chatbot():
    print("🧠 Hello! I can help you understand English words. Type 'exit' to stop.")
    while True:
        word = input("\nEnter an English word: ").strip().lower()
        if word == 'exit':
            print("👋 Goodbye! Keep learning.")
            break
        print(explain_word(word))

if __name__ == "__main__":
    chatbot()
