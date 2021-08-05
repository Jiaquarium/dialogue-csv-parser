#! /usr/bin/python

# Export .csv in same directory as this script
# Run this script and it will overwrite inside Unity Assets/Scripts 

import csv;
import datetime

INPUT_FILE          = 'Dialogue - Localized - UI.csv'
OUTPUT_FILE         = 'Script_UIText.cs'

SKIP_ROW_SYMBOL     = 'SKIP'
COMMENT_ROW_SYMBOL  = 'x'

def create_dialogue_object(
    id,
    dialogue,
):
    row_data = f'''\
{{
    "{id}",
    new Model_LanguagesUI
    {{
        EN = @"{dialogue}"
    }}
}},
'''
    return row_data

def create_section_header(text):
    output = f'''\
// ------------------------------------------------------------------
// {text}\n'''
    return output

def main():
    output = ''
    line = 0

    with open(INPUT_FILE) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        
        for row in reader:
            is_initial = line == 0;
            
            # skip rows
            if row[0].upper() == SKIP_ROW_SYMBOL.upper():
                continue
            
            # comment out rows
            if row[0].upper() == COMMENT_ROW_SYMBOL.upper():
                prepend_header = create_section_header(row[1])
                continue
                
            # notify misinputs
            # if there is multiline text but no MULTILINE_SYMBOL, throw an error
            if row[1] and not row[4]:
                raise ValueError(f'Id {id}: UI text is empty even though you are defining it')
            
            id                  = row[1]
            dialogue            = row[4]
            
            # skip rows without an id
            if not id:
                continue
            
            dialogue_output = create_dialogue_object(id, dialogue)

            if prepend_header:
                dialogue_output = prepend_header + dialogue_output
                prepend_header = ''
            
            output += dialogue_output
            line += 1
    
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

    print(output);
    print(f'Lines: {line}')

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