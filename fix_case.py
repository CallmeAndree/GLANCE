import re

with open('sections/s1_trucmai/s1_trucmai.py', 'r', encoding='utf-8') as f:
    content = f.read()

def lower_strings(match):
    list_str = match.group(1)
    def lower_single_string(m):
        return m.group(0).lower()
        
    new_list_str = re.sub(r'\"(.*?)\"', lower_single_string, list_str)
    return 'self.narrated_caption(' + new_list_str + ')'

content = re.sub(r'self\.narrated_caption\((.*?)\)', lower_strings, content, flags=re.DOTALL)

# Add the dot
content = content.replace('các kiến trúc lai sử dụng lờ lờ mờ', 'các kiến trúc lai. sử dụng lờ lờ mờ')

with open('sections/s1_trucmai/s1_trucmai.py', 'w', encoding='utf-8') as f:
    f.write(content)
