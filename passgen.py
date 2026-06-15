#!/usr/bin/env python3
import argparse
import itertools
import random
import string
import re
from flask import Flask, render_template, request, send_file
import os

app = Flask(__name__)
app.template_folder = 'templates'

# Weak patterns to block
WEAK_PATTERNS = [
    '123456', '123123', '111111', '000000', 'abc123', 'test123', 'password', 'password123',
    'qwerty', 'welcome', 'admin123', 'letmein', 'aaaaaa', 'bbbbbb', 'abcabc', 'qwerty123'
]

KEYBOARD_PATTERNS = ['qwerty', 'asdfgh', 'zxcvbn']

def is_weak(password, blocked_words):
    pw_lower = password.lower()
    if any(w in pw_lower for w in blocked_words):
        return True
    if any(p in pw_lower for p in WEAK_PATTERNS + KEYBOARD_PATTERNS):
        return True
    if re.search(r'(\d{4})$', pw_lower) or re.search(r'(\d{2,})$', pw_lower):
        return True
    if re.search(r'(.)\1{4,}', pw_lower):
        return True
    return False

def generate_passwords(keywords, specials, limit=15000, category='normal', blocked=[]):
    passwords = []
    words = [w.strip() for w in keywords.split(',') if w.strip()]
    
    # Mix combinations
    for r in range(1, min(4, len(words)+1)):
        for combo in itertools.combinations(words, r):
            base = ''.join(combo)
            for num in ['', '123', '2025', str(random.randint(10,999))]:
                pw = base + str(num)
                if not is_weak(pw, blocked) and len(pw) >= 6:
                    passwords.append(pw)
            if specials:
                for sp in specials.split():
                    pw = base + sp
                    if not is_weak(pw, blocked):
                        passwords.append(pw)
    
    # Category patterns
    if category == 'tech':
        passwords.extend([w + 'admin', w + 'dev123', w + 'root' for w in words])
    elif category == 'social':
        passwords.extend([w + 'party', w + 'love', w + '2025' for w in words])
    elif category == 'org':
        passwords.extend([w + 'official', w + 'host' for w in words])
    
    random.shuffle(passwords)
    return passwords[:limit]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keywords = request.form.get('keywords', '')
        blocked = [b.strip().lower() for b in request.form.get('blocked', '').split(',') if b.strip()]
        specials = request.form.get('specials', '')
        category = request.form.get('category', 'normal')
        limit = int(request.form.get('limit', 5000))
        
        pw_list = generate_passwords(keywords, specials, limit, category, blocked)
        
        output_file = 'generated_passwords.txt'
        with open(output_file, 'w') as f:
            f.write('\n'.join(pw_list))
        
        return send_file(output_file, as_attachment=True)
    
    return render_template('index.html')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PassGun - Targeted Password Generator')
    parser.add_argument('--web', action='store_true', help='Start Web Dashboard')
    parser.add_argument('--keywords', type=str, help='Comma separated keywords')
    parser.add_argument('--specials', type=str, default='', help='Special characters')
    parser.add_argument('--limit', type=int, default=5000)
    parser.add_argument('--category', type=str, default='normal', choices=['normal', 'social', 'org', 'tech'])
    parser.add_argument('--output', type=str, default='passwords.txt')
    args = parser.parse_args()
    
    if args.web:
        print("🚀 Starting PassGun Dashboard → http://localhost:1234")
        app.run(host='0.0.0.0', port=1234, debug=False)
    else:
        pws = generate_passwords(args.keywords or 'starmaker,star,host', args.specials, args.limit, args.category)
        with open(args.output, 'w') as f:
            f.write('\n'.join(pws))
        print(f"✅ Generated {len(pws)} passwords → {args.output}")
