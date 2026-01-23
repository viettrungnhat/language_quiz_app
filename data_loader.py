"""
Đọc dữ liệu từ file (TXT, Excel, JSON)
"""

import json
import os
from pathlib import Path

class DataLoader:
    def __init__(self, data_folder="data"):
        self.data_folder = data_folder
        self.data = {}
    
    def load_json(self, filename):
        """Load dữ liệu từ file JSON"""
        filepath = os.path.join(self.data_folder, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Lỗi khi đọc file {filename}: {e}")
            return []
    
    def parse_txt_file(self, filename):
        """
        Parse file TXT dạng:
        Số    Word        Example         Vietnamese
        """
        filepath = os.path.join(self.data_folder, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Phân tách các câu (by "---")
            sentences = []
            lines = content.split('\n')
            
            current_item = {}
            line_num = 0
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('-'):
                    continue
                
                # Logic đơn giản để parse
                if line[0].isdigit() and len(line.split()) < 5:
                    if current_item:
                        sentences.append(current_item)
                    current_item = {'id': len(sentences) + 1}
            
            if current_item:
                sentences.append(current_item)
            
            return sentences
        except Exception as e:
            print(f"❌ Lỗi khi đọc file {filename}: {e}")
            return []
    
    def get_available_languages(self):
        """Lấy danh sách ngôn ngữ có sẵn"""
        files = os.listdir(self.data_folder) if os.path.exists(self.data_folder) else []
        
        languages = {}
        for file in files:
            if file.endswith('.json'):
                name = file.replace('.json', '').replace('_', ' ').title()
                languages[name] = file
        
        return languages
    
    def convert_txt_to_json(self, txt_file, json_file):
        """
        Chuyển đổi file TXT sang JSON
        (Cần được customize tuỳ theo format của bạn)
        """
        data = self.parse_txt_file(txt_file)
        
        json_path = os.path.join(self.data_folder, json_file)
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ Chuyển đổi thành công: {json_file}")
            return True
        except Exception as e:
            print(f"❌ Lỗi khi lưu file: {e}")
            return False
    
    def load_language_data(self, language):
        """Load dữ liệu ngôn ngữ"""
        return self.load_json(language)

# Tạo file JSON mẫu nếu không có
def create_sample_data():
    """Tạo dữ liệu mẫu"""
    sample_english = [
        {
            "id": 1,
            "word": "aunt",
            "meaning": "cô, dì, bác gái",
            "example_en": "Is she your aunt?",
            "example_vi": "Cô ấy là cô của bạn phải không?"
        },
        {
            "id": 2,
            "word": "love",
            "meaning": "yêu, thích",
            "example_en": "Do you love this song?",
            "example_vi": "Bạn có yêu thích bài hát này không?"
        }
    ]
    
    data_folder = "data"
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    with open(os.path.join(data_folder, "sample_english.json"), 'w', encoding='utf-8') as f:
        json.dump(sample_english, f, ensure_ascii=False, indent=2)
    
    print("✓ Tạo file dữ liệu mẫu thành công")
