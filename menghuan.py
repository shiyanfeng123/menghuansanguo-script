import xml.etree.ElementTree as ET

def parse_swf_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    swf_info = {
        'version': root.attrib['version'],
        'frameRate': root.attrib['frameRate'],
        'frameCount': root.attrib['frameCount']
    }
    
    for item in root.findall('tags/item'):
        tag_type = item.attrib['type']
        print(f"Tag Type: {tag_type}")
        # 根据需要提取更多信息
        
    return swf_info

# 调用函数解析文件
swf_info = parse_swf_xml('swf.xml')
print(swf_info)