import tkinter as tk
from tkinter import ttk
import ply.lex as lex
import ply.yacc as yacc

# === Lexer ===
tokens = (
    'DETERMINER',
    'PRONOUN',
    'ADJECTIVE',
    'NOUN',
    'VERB',
    'ADVERB',
    'CONJUNCTION',
    'PREPOSITION',
)

# Load reserved words from a file
def load_reserved_words(filename):
    reserved = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                word, word_type = line.strip().split()
                reserved[word.lower()] = word_type
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
    return reserved

reserved = load_reserved_words("unique_words_dictionary.txt")

def t_RESERVED(t):
    r'\b[a-zA-Z]+\b'
    t.value = t.value.lower()
    t.type = reserved.get(t.value, 'NOUN')  # Default to NOUN for unreserved words
    return t

t_ignore = " \t"

def t_error(t):
    raise ValueError(f"Invalid character: {t.value[0]}")

lexer = lex.lex()

# === Parser ===
def p_sentence(p):
    '''sentence : subject predicate
                | subject predicate conjunction sentence
                | subject predicate prepositional_phrase
                | subject predicate prepositional_phrase conjunction sentence'''
    p[0] = ('sentence', p[1], p[2])

def p_subject(p):
    '''subject : noun_phrase
               | PRONOUN'''
    p[0] = ('subject', p[1])

def p_predicate(p):
    '''predicate : verb_phrase
                 | verb_phrase object
                 | verb_phrase adverb_phrase
                 | verb_phrase prepositional_phrase'''
    p[0] = ('predicate', p[1])

def p_object(p):
    '''object : noun_phrase'''
    p[0] = ('object', p[1])

def p_prepositional_phrase(p):
    '''prepositional_phrase : PREPOSITION noun_phrase'''
    p[0] = ('prepositional_phrase', p[1], p[2])

def p_adverb_phrase(p):
    '''adverb_phrase : ADVERB
                     | ADVERB ADVERB'''
    p[0] = ('adverb_phrase', ' '.join(p[1:]))

def p_noun_phrase(p):
    '''noun_phrase : NOUN
                   | DETERMINER NOUN
                   | DETERMINER ADJECTIVE NOUN
                   | ADJECTIVE NOUN'''
    p[0] = ('noun_phrase', ' '.join(p[1:]))

def p_verb_phrase(p):
    '''verb_phrase : VERB
                   | VERB noun_phrase
                   | VERB noun_phrase prepositional_phrase'''
    p[0] = ('verb_phrase', ' '.join(p[1:]))

def p_conjunction(p):
    '''conjunction : CONJUNCTION'''
    p[0] = ('conjunction', p[1])

def p_error(p):
    raise ValueError("Invalid grammar detected!")

parser = yacc.yacc()

# Caesar Cipher Function
def caesar_cipher(text, shift, encode=True):
    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            offset = (ord(char) - base + (shift if encode else -shift)) % 26
            result.append(chr(base + offset))
        elif char.isdigit():
            offset = (int(char) + (shift if encode else -shift)) % 10
            result.append(str(offset))
        else:
            result.append(char)
    return ''.join(result)

# Parse Tree Generation with GUI Integration
def parse_tree(input_text):
    try:
        # Tokenize the input and display tokens
        lexer.input(input_text)
        tokens_list = []
        for token in lexer:
            tokens_list.append(token.type)
        print(f"Tokens: {tokens_list}")

        # Parse the input and display the parse tree
        parse_result = parser.parse(input_text)
        if parse_result:
            print("\nParse Tree:")
            print(parse_result)
        else:
            print("No parse tree generated (input may not match grammar).")
    except ValueError as e:
        print(f"Error during parsing: {e}")

def draw_tree(tree, prefix="", is_tail=True):
    """Recursively draws a parse tree in a tree-like format."""
    if isinstance(tree, tuple):
        label = tree[0]  # The root of the current subtree
        print(prefix + ("└── " if is_tail else "├── ") + label)
        children = tree[1:]
        for i, child in enumerate(children):
            draw_tree(child, prefix + ("    " if is_tail else "│   "), i == len(children) - 1)
    else:
        # Leaf nodes
        print(prefix + ("└── " if is_tail else "├── ") + tree)

def encode_text():
    try:
        input_text = english_textbox.get("1.0", tk.END).strip()
        shift = int(shift_entry.get().strip())
        if shift < 0 or shift > 25:
            raise ValueError("Shift must be between 0 and 25.")

        # Tokenize the input text
        lexer.input(input_text)
        for token in lexer:
            pass  # Verify tokenization

        # Parse the input text and get the parse tree
        parse_tree = parser.parse(input_text)

        # Print the parse tree in CLI as a tree structure
        print("\nParse Tree:")
        draw_tree(parse_tree)
        
        # Perform Caesar cipher encoding
        output_text = caesar_cipher(input_text, shift, encode=True)
        cipher_textbox.config(state=tk.NORMAL)
        cipher_textbox.delete("1.0", tk.END)
        cipher_textbox.insert("1.0", output_text)
        cipher_textbox.config(state=tk.DISABLED)

    except ValueError as e:
        cipher_textbox.config(state=tk.NORMAL)
        cipher_textbox.delete("1.0", tk.END)
        cipher_textbox.insert("1.0", f"Error: {e}")
        cipher_textbox.config(state=tk.DISABLED)

def decode_text():
    try:
        input_text = cipher_textbox_input.get("1.0", tk.END).strip()
        shift = int(shift_entry.get().strip())
        if shift < 0 or shift > 25:
            raise ValueError("Shift must be between 0 and 25.")
        # lexer.input(input_text)
        # for token in lexer:
        #     pass
        # parser.parse(input_text)
        output_text = caesar_cipher(input_text, shift, encode=False)
        decoded_textbox.config(state=tk.NORMAL)
        decoded_textbox.delete("1.0", tk.END)
        decoded_textbox.insert("1.0", output_text)
        decoded_textbox.config(state=tk.DISABLED)
    except ValueError as e:
        decoded_textbox.config(state=tk.NORMAL)
        decoded_textbox.delete("1.0", tk.END)
        decoded_textbox.insert("1.0", f"Error: {e}")
        decoded_textbox.config(state=tk.DISABLED)

# Create main window
root = tk.Tk()
root.title("Caesar Cipher Translation Tool")
root.geometry("900x700")

# Title
title_label = ttk.Label(root, text="Caesar Cipher Translation Tool", font=("Helvetica", 24, "bold"))
title_label.pack(pady=10)

# Description
description_label = ttk.Label(
    root,
    text="Ciphertext is encrypted text transformed from plaintext using an encryption algorithm. "
         "This tool allows you to encode or decode text using a Caesar cipher. "
         "Insert text and determine the shift value below.",
    wraplength=800,
    justify="center",
    font=("Helvetica", 12)
)
description_label.pack(pady=10)

# Top Section: English to Cipher
frame_top = ttk.Frame(root)
frame_top.pack(pady=20, padx=20)

# English Text
english_label = ttk.Label(frame_top, text="English", font=("Helvetica", 14, "bold"))
english_label.grid(row=0, column=0, padx=10, sticky="w")
english_textbox = tk.Text(frame_top, width=40, height=6, wrap="word")
english_textbox.grid(row=1, column=0, padx=10, pady=5)
english_textbox.insert("1.0", "Insert Text Here")

# Encode Button
encode_button = ttk.Button(frame_top, text="Encode", command=encode_text)
encode_button.grid(row=1, column=1, padx=10)

# Shift Entry
shift_entry = tk.Entry(frame_top, width=5, justify="center", font=("Helvetica", 14))
shift_entry.insert(0, "3")
shift_entry.grid(row=0, column=1, pady=5)

# Cipher Text Output
cipher_label = ttk.Label(frame_top, text="Cipher Text", font=("Helvetica", 14, "bold"))
cipher_label.grid(row=0, column=2, padx=10, sticky="w")
cipher_textbox = tk.Text(frame_top, width=40, height=6, wrap="word")
cipher_textbox.grid(row=1, column=2, padx=10, pady=5)
cipher_textbox.config(state=tk.DISABLED)

# Bottom Section: Cipher to English
frame_bottom = ttk.Frame(root)
frame_bottom.pack(pady=20, padx=20)

# Cipher Text Input
cipher_label_input = ttk.Label(frame_bottom, text="Cipher Text", font=("Helvetica", 14, "bold"))
cipher_label_input.grid(row=0, column=0, padx=10, sticky="w")
cipher_textbox_input = tk.Text(frame_bottom, width=40, height=6, wrap="word")
cipher_textbox_input.grid(row=1, column=0, padx=10, pady=5)

# Decode Button
decode_button = ttk.Button(frame_bottom, text="Decode", command=decode_text)
decode_button.grid(row=1, column=1, padx=10)

# Decoded Text Output
decoded_label = ttk.Label(frame_bottom, text="Decoded Text", font=("Helvetica", 14, "bold"))
decoded_label.grid(row=0, column=2, padx=10, sticky="w")
decoded_textbox = tk.Text(frame_bottom, width=40, height=6, wrap="word")
decoded_textbox.grid(row=1, column=2, padx=10, pady=5)
decoded_textbox.config(state=tk.DISABLED)

# Start the application
root.mainloop()