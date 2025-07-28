import fitz
import json
def read_pdf(path):
    def sort_spans_page_y_x(spans, y_tolerance=0.2):
        return sorted(
            spans,
            key=lambda s: (
                s['page_no'],
                round(s['bbox'][1] / y_tolerance) * y_tolerance,
                s['bbox'][0]
            )
        )
    doc = fitz.open(path)
    all_spans = []
    all_tables = []

    #STEP 1: Read all the spans as it is in sorted order, and store positions of all the tables
    for page_number, page in enumerate(doc, start=1):
        if page_number > 50: break
        for table in page.find_tables():
            all_tables.append([page_number, table.bbox[1], table.bbox[3]])
        blocks = page.get_text('dict')['blocks']
        for block in blocks:
            if 'lines' not in block:
                continue
            for line in block['lines']: 
                for span in line['spans'] :
                    all_spans.append({**span, "page_no" : page_number})
    all_spans = sort_spans_page_y_x(all_spans)
    # STEP 2: Remove useless spans
    i = 0
    j = 0
    all_filtered_spans = []
    while (i < len(all_spans)):
        if all_spans[i]['size'] <= 8:
            i += 1
            continue
        if j == len(all_tables):
            all_filtered_spans.append(all_spans[i])
            i += 1
            continue
        if all_spans[i]['page_no'] > all_tables[j][0]: j += 1
        elif all_spans[i]['page_no'] < all_tables[j][0]: 
            all_filtered_spans.append(all_spans[i])
            i += 1
        else :
            if all_spans[i]['bbox'][1] < all_tables[j][1]:
                all_filtered_spans.append(all_spans[i])
                i += 1
            elif all_spans[i]['bbox'][1] > all_tables[j][2]:
                j += 1
            else:
                i +=1
    
    all_spans = all_filtered_spans

    #STEP 3: Map font to integer
    font_map = {}
    size_map = {}
    size_count = 0
    font_count = 0
    for i in all_spans:
        if (font_map.get(i['font']) == None):
            font_map[i['font']] = font_count
            font_count+=1
        if (size_map.get(round(i['size'])) == None):
            size_map[round(i['size'])] = size_count
            size_count+=1

    # STEP 4: Merge the spans into lines

    all_lines = []
    k = 0
    while (k < len(all_spans)):
        spans_in_this_line = []
        spans_in_this_line.append(all_spans[k])
        y_tolerance = (all_spans[k]['bbox'][3] - all_spans[k]['bbox'][1]) *0.5
        j = k+1
        while (j < len(all_spans) and abs(all_spans[j]['bbox'][1] - all_spans[k]['bbox'][1]) < y_tolerance): 
            spans_in_this_line.append(all_spans[j])
            j += 1
        k = j
        spans_in_this_line = sorted(spans_in_this_line, key=lambda s: (s['bbox'][0])) # sort wrt x
        merged_text = ""
        font_freq = {}
        size_freq = {}
        color_freq = {}
        for i in spans_in_this_line:
            if (font_freq.get(i['font']) == None):
                font_freq[i['font']] = len(i['text'])
            else:
                font_freq[i['font']] += len(i['text'])
            if (size_freq.get(i['size']) == None):
                size_freq[i['size']] = len(i['text'])
            else:
                size_freq[i['size']] += len(i['text'])
            if (color_freq.get(i['color']) == None):
                color_freq[i['color']] = len(i['text'])
            else:
                color_freq[i['color']] += len(i['text'])
            merged_text = merged_text + i['text']
        line_font = max(font_freq, key=font_freq.get)
        line_size = max(size_freq, key=size_freq.get)
        line_color = max(color_freq, key=color_freq.get)
        l = len(spans_in_this_line)
        line_bbox = (spans_in_this_line[0]['bbox'][0],spans_in_this_line[0]['bbox'][1],spans_in_this_line[l-1]['bbox'][2],spans_in_this_line[l-1]['bbox'][3])
        line = {
            "text": merged_text,
            "font": line_font,
            "color": line_color,
            "bbox": line_bbox,
            "size": round(line_size),
            "page_no": spans_in_this_line[0]['page_no'],
        }
        all_lines.append(line)
    
    # STEP 5: For each line compute if it is centered or not
    center = 0
    left_margin=10000
    right_margin = 0
    count = 0
    for i in all_lines:
        left_margin = ((count*left_margin) + i['bbox'][0])/(count+1)
        right_margin = ((count*right_margin) + i['bbox'][1])/(count+1)
        count += 1
    temp = []
    for i in all_lines:
        left_dist_from_edges = max(i["bbox"][0] - left_margin, 0)
        right_dist_from_edges = max(right_margin - i["bbox"][2], 0)
        text_len = right_margin-left_margin - left_dist_from_edges - right_dist_from_edges
        # if the text is big enough, center = 1
        if (left_dist_from_edges + right_dist_from_edges <= 0.2*(right_margin-left_margin)):
            center = 1
        # if the disfference between the left margin and right margin is big enough center = 0
        elif (abs(left_dist_from_edges - right_dist_from_edges) > 0.25*(text_len)):
            center = 0
        else:
            center = 2
        temp.append({**i, **{"center": center}})
    all_lines = temp
    
    # STEP 6: Merge Lines into Blocks

    def merge(block1, block2):
        # return None
        if (block1['font'] != block2['font'] or block1['size'] != block2['size'] or block1['color'] != block2['color'] or block1['center'] == 0): return None
        merged_text = block1['text'] + block2['text']
        block_center = 1
        block_center = block2['center']
        ans = {
            "text": merged_text,
            "font": block1['font'],
            "color": block1['color'],
            "size": block1['size'],
            "center": block_center,
            "page_no": block1['page_no']
        }
        return ans
    all_blocks = []
    i = 0
    while (i < len(all_lines)):
        block = {
            "text" : all_lines[i]['text'],
            "font": all_lines[i]['font'],
            "color": all_lines[i]['color'],
            "size": all_lines[i]['size'],
            "center": all_lines[i]['center'],
            "page_no": all_lines[i]['page_no']
        }
        j = i+1
        while (j < len(all_lines)):
            temp = merge(block, all_lines[j])
            if (temp == None): break
            block = temp
            j += 1
        i = j
        all_blocks.append(block)

    # STEP 7: Remove unncecessary blocks (like whitespaces, etc)

    def is_useful_block(block):
        full_text = block['text']
        # number of characters in the block
        if not any(c.isalpha() for c in full_text):
            return False
        if (len(full_text) > 150):
            return True
        # Remove blocks with Junk keywords + small font
        junk_keywords = [
    "you may also like",
    "related articles",
    "recommended for you",
    "further reading",
    "continue reading",
    "more from this issue",
    "previous page",
    "next page",
    "back to top",
    "all rights reserved",
    "©",
    "copyright",
    "no part of this publication may be reproduced",
    "terms and conditions",
    "privacy policy",
    "this material is protected by copyright law",
    "published by",
    "printed in",
    "downloaded from",
    "published online by",
    "available at",
    "retrieved from",
    "publisher’s note",
    "reprinted with permission",
    "doi:",
    "issn:",
    "citation:",
    "view metrics",
    "metrics details",
    "received:",
    "accepted:",
    "page",
    "volume",
    "issue",
    "journal of",
    "this article is distributed under the terms of the creative commons license",
    "corresponding author:",
    "et al.",
    "powered by",
    "institution",
    "buy now",
    "subscribe",
    "start your free trial",
    "advertisement",
    "sponsored by",
    "this is a preview of subscription content",
    "full access requires login",
    "supplementary materials",
    "open access",
    "export citation",
    "download pdf",
    "share this article",
    "http://",
    "https://",
    "www.",
    "@"
]
        if any(kw in full_text.lower() for kw in junk_keywords) and block['size'] <= 10:
            return False
        return True
    all_filtered_blocks = []
    for i in all_blocks:
        if (is_useful_block(i)): all_filtered_blocks.append(i)
    
    return all_filtered_blocks