import json
import re
import os

with open("donnees_finales.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def is_meaningful_word(word):
    """Check if a word is meaningful """
    word = word.strip()
    
   
    if len(word) < 3:
        return False
   
    alpha_chars = [c for c in word if c.isalpha()]
    if len(alpha_chars) == 0:  
        return True  
    
    
    vowels = 'aeiouAEIOU'
    consonant_ratio = sum(1 for c in alpha_chars if c not in vowels) / len(alpha_chars)
    if consonant_ratio > 0.8:  
        return False
    
   
    if re.search(r'(.)\1{3,}', word):  
        return False
    
  
    if len(word) > 8 and not re.search(r'[aeiou].*[aeiou]', word.lower()):
        return False
    
    return True

def is_meaningful_text(text):
    """Check if entire text line is meaningful"""
   
    if re.search(r'\d+\s*(mg|cp|fois|jour|mois|semaine|application)', text.lower()):
        return True
    
  
    medical_terms = ['atcd', 'ttt', 'ras', 'spf', 'creme', 'gel', 'lotion', 'shampoing']
    if any(term in text.lower() for term in medical_terms):
        return True
    
    words = re.findall(r'\b\w+\b', text)
    if not words:
        return False
    
    meaningful_count = sum(1 for word in words if is_meaningful_word(word))
    return meaningful_count / len(words) > 0.5  


clean_data = {}
new_key = 1  

for key, value_list in data.items():
    if isinstance(value_list, list):
        cleaned_list = [text for text in value_list if is_meaningful_text(text)]
        if cleaned_list: 
            clean_data[str(new_key)] = cleaned_list
            new_key += 1
    else:
        if value_list:  
            clean_data[str(new_key)] = value_list
            new_key += 1


output_path = os.path.join(os.path.dirname(__file__), "donnees_nettoyees_finales.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(clean_data, f, ensure_ascii=False, indent=4)

print(f" Données nettoyées sauvegardées dans: {output_path}")
