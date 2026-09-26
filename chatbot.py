#!/usr/bin/env python3
"""
chatbot.py
Rule-based admissions chatbot with simple NLP (tokenization + stemming)
Designed for the COMP40055 assignment (APIIT admissions FAQs)
"""
"pip install nltk" """only run this if you have not installed nltk"""
import re

try:
    import nltk
    from nltk.stem import PorterStemmer
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.chat.util import Chat, reflections
except Exception as e:
    raise SystemExit(
        "NLTK is required. Please install it first:\n"
        "    pip install nltk\n\n"
        "Error: " + str(e)
    )

# Ensure punkt tokenizer is available
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    print("Downloading NLTK punkt tokenizer...")
    nltk.download("punkt")
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    print("Downloading NLTK stopwords...")
    nltk.download("stopwords")


ps = PorterStemmer()

# ---------------- Knowledge Base ---------------- #
KNOWLEDGE_BASE = {
   "what undergraduate programs are available at apiit":
        "APIIT offers undergraduate programs in Computing (e.g., BSc (Hons) Computer Science), Business, and other allied areas.",
    "do you offer postgraduate degrees":
        "Yes — APIIT offers postgraduate degrees such as MSc and diplomas in computing and business.",
    "what are the entry requirements for the computing degree":
        "Typically A-levels or equivalent qualifications, plus English proficiency for international students.",
    "how do i apply for a course at apiit":
        "You can apply online via the application portal or by submitting a paper application.",
    "when is the next intake":
        "APIIT commonly has intakes in January, May, and September. Check the academic calendar.",
    "are there part-time course options":
        "Some programmes may be offered part-time or flexibly. Contact admissions for details.",
    "what is the tuition fee for the bsc (hons) in computer science":
        "Fees depend on the year of study and residency status. Check the official fees schedule.",
    "can i pay the fees in installments":
        "Yes, installment payment plans are often available. Contact finance for current options.",
    "are there any scholarships available":
        "Scholarships may be available based on merit or need. Check the scholarships page.",
   "What is the registration fee for new students":
        "A non-refundable registration fee is required for new students.",
   "Can I apply online or do I need to visit the campus?":
        "You can generally apply online. Visiting campus is optional but recommended since you can get an better idea on it.",
   "what documents do i need to submit with my application":
        "Typically transcripts, qualifications, ID/passport, proof of English proficiency, and photos.",
    "what is the duration of a typical undergraduate degree":
        "A full-time undergraduate degree is usually 3–4 years, depending on the programme.",
    "Who are the lecturers for the School of Computing?":
      "Zeenath Hidaya\n"
       "Yovini Dharmapala\n"
       "Tharanga Peiris\n"
       "Tharaka Dulaj\n"
       "Shani Alwis\n"
       "Sajid Fayaz Haniff\n",
   "Do you offer business or law degrees?":
       "Yes APIIT does provides a diverse range of business-focused and Law Degree Pathways for undergraduate:\n"
       "BSc (Hons) Business Management\n"
        "BSc (Hons) Business Management (Innovation and Entrepreneurship)\n"
        "BSc (Hons) Business Management (Human Resource Management)\n"
        "LLB (Hons) Law\n"
        "LLB (Hons) Law – Digital\n"
        "LLB (Hons) Law (Part-Time)\n",
   "How many intakes are there per year?":
        "APIIT offers three intakes per year for its undergraduate programs:\n"
             "February,June and October. This allowes students to begin their higher education after their O/L or A/L examinations/n",
   "Can international students apply?":
        "Yes international students are welcome. Check visa and English requirements.",
    "what english language qualifications are required":
        "IELTS, TOEFL, or equivalent. Minimum scores vary by programme.",
    "is there an application deadline":
        "Deadlines depend on intake and programme. Some allow rolling admissions.",
    "do you offer foundation or bridging courses":
        "Yes, for students who do not meet direct entry requirements.",
    "what are the career opportunities after completing a computing degree":
        "Graduates work in software development, IT, data science, cybersecurity, and related fields.",
    "can i schedule a campus visit before applying":
        "Yes campus visits can usually be arranged via admissions or marketing office.",
   "What is the difference between internal and external programs?":
   "There is no distinction between internal and external programs at APIIT Sri Lanka. All degrees are internally delivered,\n"
  "ensuring that students receive the full benefits of the academic structure and support associated with Staffordshire University.\n",
   "will i get a degree from a uk university":
        "Some programmes are validated or awarded by UK partner universities.",
  "what is the accreditation status of apiit programs":
        "All APIIT degree programmes are validated and awarded by Staffordshire University, UK.",
    "are there evening or weekend classes":
        "Some programmes may offer evening or weekend classes. Confirm with the admissions for more details.",
    "what support services are available for new students":
        "Support includes academic mentoring, language support, counselling, internships, and career services.",
    "can i transfer credits from another university":
        "Credit transfer may be possible on a case-by-case basis. Provide transcripts to admissions for evaluation.",
    "do i need to attend an interview as part of the admission process":
        "Some programmes may require interviews, but many undergraduate applications are processed without them.",
    "how can i contact the admissions team directly":
        "You can contact admissions via info@apiit.lk, call +94 74 036 5144 / +94 76 858 3708, or visit 388 Union Place, Colombo."
}

# ---------------- Basic Conversation Patterns ---------------- #
BASIC_PAIRS = [
    (r'hello|hey', "Hello! I'm the APIIT admissions assistant. How can I help you today?"),
    (r'help', "You can ask about programmes, fees, requirements, intakes, scholarships, or type 'quit' to exit."),
    (r'quit|exit', "Goodbye — best of luck!"),
    (r'bye', "See you later!"),
    (r'thank(s)?( you)?', "You're welcome! Anything else I can help with?")
]

# ---------------- NLP Helpers ---------------- #
def tokenize_and_stem(text):
    try:
        tokens = word_tokenize(text.lower())
    except Exception:
        tokens = re.findall(r"\b\w+\b", text.lower())
    return {ps.stem(t) for t in tokens}

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

def find_best_match(user_input, threshold=0.25):
    user_stems = tokenize_and_stem(user_input)
    best_key, best_score = None, 0
    for key, answer in KNOWLEDGE_BASE.items():
        key_tokens = tokenize_and_stem(key)
        score = jaccard_similarity(user_stems, key_tokens)
        if score > best_score:
            best_key, best_score = key, score
    return (best_key if best_score >= threshold else None)

# ---------------- Chatbot Core ---------------- #
def get_response(user_input):
    text = user_input.strip()
    if not text:
        return "Please type a question."

    # Check basic conversational patterns first
    for pattern, response in BASIC_PAIRS:
        if re.search(pattern, text.lower()):
            return response

    # Direct keyword check
    for key, answer in KNOWLEDGE_BASE.items():
        if key.replace("_", " ") in text.lower():
            return answer

    # Similarity match
    kb_key = find_best_match(text)
    if kb_key:
        return KNOWLEDGE_BASE[kb_key]

    # Fallback
    return "I'm sorry, I don't have that information. Please contact the admissions team."

def interactive_loop():
    print("Welcome to the APIIT Admissions Chatbot (type 'quit' to exit).")
    while True:
        user = input("You: ")
        if user.lower() in ("quit", "exit"):
            print("Bot: Goodbye!")
            break
        print("Bot:", get_response(user))

if __name__ == "__main__":
    interactive_loop()
