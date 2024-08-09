#! /usr/bin/python

# Export .csv in same directory as this script
# Run this script with python3 and it will overwrite inside Unity Assets/Scripts 

import csv;
import datetime

INPUT_FILE          = 'Dialogue - Localized - UI.csv'
OUTPUT_FILE         = 'Script_UIText.cs'

SKIP_ROW_SYMBOL     = 'SKIP'
COMMENT_ROW_SYMBOL  = 'x'

ID_DELIMITER    = '_'
ID_MIN_LENGTH   = 4

def main():
    output = ''
    id_count = 0
    line = 0

    with open(INPUT_FILE) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        
        for row in reader:
            is_initial = id_count == 0;

            line += 1
            
            # skip rows
            if row[0].upper() == SKIP_ROW_SYMBOL.upper():
                continue
            
            # comment out rows
            if row[0].upper() == COMMENT_ROW_SYMBOL.upper():
                prepend_header = create_section_header(row[1])
                continue
                
            # notify misinputs
            if row[1] and not row[4]:
                raise ValueError(f'Line {line} Id {id}: UI text is empty even though you are defining it')
            
            id                  = row[1].strip()
            dialogue            = row[4].strip()
            dialogue_cn         = row[5].strip()
            dialogue_jp         = row[6].strip()
            dialogue_ru         = row[7].strip()
            
            # skip rows without an id
            if not id:
                continue
            
            dialogue_output = create_dialogue_object(
                id,
                dialogue,
                dialogue_cn,
                dialogue_jp,
                dialogue_ru
            )

            if prepend_header:
                dialogue_output = prepend_header + dialogue_output
                prepend_header = ''
            
            output += dialogue_output
            id_count += 1
    
    output = f'''\
{create_file_header()}
{{
{output}
}};
{create_file_footer()}
'''
    
    # write output into file
    with open(OUTPUT_FILE, 'w') as f:
        f.write(output);

    print(f'Ids: {id_count}')
    print(f'Lines processed: {line}')

def check_id(id, line):
    if id.count(ID_DELIMITER) < 2:
        raise ValueError(f'Line {line} Id {id}: Does not contain at least 2 delimiters')
    if bool(re.search(r"\s", id)):
        raise ValueError(f'Line {line} Id {id}: Contains spaces')
    if len(id) < 4:
        raise ValueError(f'Line {line} Id {id}: Is less than 4 characters')

def create_dialogue_object(
    id,
    dialogue,
    dialogue_cn,
    dialogue_jp,
    dialogue_ru,
):
    dialogue_cn = dialogue if not dialogue_cn else dialogue_cn
    dialogue_jp = dialogue if not dialogue_jp else dialogue_jp
    dialogue_ru = dialogue if not dialogue_ru else dialogue_ru
    row_data = f'''\
{{
    "{id}",
    new Model_LanguagesUI
    {{
        EN = @"{dialogue}",
        CN = @"{dialogue_cn}",
        JP = @"{dialogue_jp}",
        RU = @"{dialogue_ru}"
    }}
}},
'''
    return row_data

def create_section_header(text):
    output = f'''\
// ------------------------------------------------------------------
// {text}\n'''
    return output

def create_file_header():
    return f'''\
// Last created by UI Exporter at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// https://docs.google.com/spreadsheets/d/12PJr55wEMnZhO3n-c00xunSQxyDqnkutiAOx4BLh0tQ/edit#gid=814810533

public class Model_LanguagesUI
{{
    public string EN {{ get; set; }}
    public string CN {{ get; set; }}
    public string JP {{ get; set; }}
    public string RU {{ get; set; }}
}}

public class Script_UIText
{{
    public static Dictionary<string, Model_LanguagesUI> Text = new Dictionary<string, Model_LanguagesUI>
'''

def create_file_footer():
    return '''\
}
'''

main()