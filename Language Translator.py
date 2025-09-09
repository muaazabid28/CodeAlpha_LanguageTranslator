import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
from urllib.parse import quote
import threading

class LanguageTranslatorFree:
    def __init__(self, root):
        self.root = root
        root.title("🌍 Language Translator Pro")
        root.geometry("750x650")
        root.configure(bg='#2c3e50')        
        self.LANG_CODES = ["en", "ur", "ar", "fr", "de", "es", "hi", "it", "ja", "ko", "pt", "ru", "tr"]
        self.LANG_NAMES = {
            "en": "English", "ur": "Urdu", "ar": "Arabic", "fr": "French", 
            "de": "German", "es": "Spanish", "hi": "Hindi", "it": "Italian", 
            "ja": "Japanese", "ko": "Korean", "pt": "Portuguese", 
            "ru": "Russian", "tr": "Turkish"
        }
        self.setup_styles()
        self.create_widgets()
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')        
        style.configure('TFrame', background='#2c3e50')
        style.configure('TLabel', background='#2c3e50', foreground='#ecf0f1', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 12, 'bold'), padding=10)
        style.configure('TLabelframe', background='#34495e')
        style.configure('TLabelframe.Label', background='#34495e', foreground='#ecf0f1', font=('Arial', 11, 'bold'))      
        style.map('TButton',
                 background=[('active', '#2980b9'), ('pressed', '#1c638e')],
                 foreground=[('active', 'white'), ('pressed', 'white')])
    def create_widgets(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=25, pady=20)
        header = tk.Label(main_container, text="🌍 LANGUAGE TRANSLATOR PRO", 
                         font=("Arial", 18, "bold"), bg='#2c3e50', fg='#ffd700')
        header.pack(pady=(0, 20))
        top_frame = ttk.Frame(main_container)
        top_frame.pack(fill='x', pady=15)
        lang_options = [f"{code} - {self.LANG_NAMES[code]}" for code in self.LANG_CODES]      
        ttk.Label(top_frame, text="🔤 SOURCE LANGUAGE:", font=('Arial', 11, 'bold')).grid(row=0, column=0, padx=5, sticky='w')
        self.source_lang = ttk.Combobox(top_frame, values=lang_options, state="readonly", width=20, font=('Arial', 10), height=15)
        self.source_lang.set('en - English')
        self.source_lang.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Label(top_frame, text="🎯 TARGET LANGUAGE:", font=('Arial', 11, 'bold')).grid(row=0, column=1, padx=20, sticky='w')
        self.target_lang = ttk.Combobox(top_frame, values=lang_options, state="readonly", 
                                       width=20, font=('Arial', 10), height=15)
        self.target_lang.set('ur - Urdu')
        self.target_lang.grid(row=1, column=1, padx=20, pady=5, sticky='w')
        input_frame = ttk.LabelFrame(main_container, text="📝 INPUT TEXT")
        input_frame.pack(fill='x', pady=10)        
        self.input_area = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=10,
                                                   bg='#34495e', fg='#ecf0f1', font=('Arial', 10, 'bold'),
                                                   insertbackground='#3498db', selectbackground='#3498db')
        self.input_area.pack(fill='both', expand=True, padx=10, pady=10)
        button_frame = ttk.Frame(main_container)
        button_frame.pack(pady=15)
        self.translate_btn = tk.Button(button_frame, text="🚀 TRANSLATE NOW", 
                                      command=self.translate_text,
                                      font=('Arial', 14, 'bold'),
                                      bg='#e74c3c', fg='white',
                                      activebackground='#c0392b',
                                      activeforeground='white',
                                      relief='raised',
                                      bd=0,
                                      padx=30,
                                      pady=12,
                                      cursor='hand2')
        self.translate_btn.pack()
        output_frame = ttk.LabelFrame(main_container, text="📄 TRANSLATED TEXT")
        output_frame.pack(fill='x', pady=10)        
        self.output_area = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=10,
                                                    state='disabled', bg='#34495e', fg='#ecf0f1',
                                                    font=('Arial', 10, 'bold'))
        self.output_area.pack(fill='both', expand=True, padx=10, pady=10)
    def translate_text(self):
        text = self.input_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Input Error", "Please enter text to translate")
            return
        source = self.source_lang.get().split(" - ")[0]
        target = self.target_lang.get().split(" - ")[0]
        if source == target:
            self.set_output_text(text)
            return
        self.set_output_text("⏳ Translating...")
        self.translate_btn.config(state='disabled', bg='#95a5a6')
        thread = threading.Thread(target=self.perform_translation, args=(text, source, target))
        thread.daemon = True
        thread.start()
    def perform_translation(self, text, source, target):
        translated = None
        try:
            translated = self.translate_with_google(text, source, target)
        except Exception as e:
            print(f"Google Translate error: {e}")        
        if not translated:
            try:
                translated = self.translate_with_mymemory(text, source, target)
            except Exception as e:
                print(f"MyMemory error: {e}")        
        if not translated:
            try:
                translated = self.translate_with_libretranslate(text, source, target)
            except Exception as e:
                print(f"LibreTranslate error: {e}")        
        result = translated if translated else "❌ Translation failed. Try again."
        self.root.after(0, lambda: self.finish_translation(result))
    def finish_translation(self, result):
        self.set_output_text(result)
        self.translate_btn.config(state='normal', bg='#e74c3c')
    def set_output_text(self, text):
        self.output_area.config(state='normal')
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert("1.0", text)
        self.output_area.config(state='disabled')
    def translate_with_google(self, text, source, target):
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': source,
                'tl': target,
                'dt': 't',
                'q': text
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return ''.join([s[0] for s in data[0] if s[0]])
        except:
            try:
                url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source}&tl={target}&dt=t&q={quote(text)}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                return ''.join([s[0] for s in data[0] if s[0]])
            except:
                raise Exception("Google Translate failed")
    def translate_with_mymemory(self, text, source, target):
        encoded_text = quote(text)
        url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair={source}|{target}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['responseData']['translatedText']
    def translate_with_libretranslate(self, text, source, target):
        endpoints = [
            "https://libretranslate.de/translate",
            "https://translate.argosopentech.com/translate"
        ]        
        for endpoint in endpoints:
            try:
                url = endpoint
                headers = {'Content-Type': 'application/json'}
                payload = {
                    "q": text, 
                    "source": source, 
                    "target": target, 
                    "format": "text"
                }
                response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                return data.get('translatedText')
            except:
                continue
        raise Exception("All LibreTranslate endpoints failed")

if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageTranslatorFree(root)
    root.mainloop()