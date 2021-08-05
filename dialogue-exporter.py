#! /usr/bin/python

# Export .csv in same directory as this script
# Run this script and it will overwrite inside Unity Assets/Scripts

import csv
import datetime

INPUT_FILE          = 'Dialogue - Localized - Dialogue.csv'
OUTPUT_FILE         = 'Script_Dialogue.cs'

SKIP_ROW_SYMBOL     = 'SKIP'
COMMENT_ROW_SYMBOL  = 'x'
MULTILINE_SYMBOL    = '"'
TRUE_SYMBOL         = 'TRUE' 
FALSE_SYMBOL        = 'FALSE'

def format_bool_string(bool_string, line):
    if bool_string == TRUE_SYMBOL:
        return 'true'
    elif bool_string == FALSE_SYMBOL:
        return 'false'
    raise ValueError(f'Line {line}: A boolean is not formatted correctly')

def create_dialogue_object(
    id,
    speaker,
    dialogues,
    choice_text,
    unskippables,
    no_continuations,
    wait_for_timelines,
    line # for debugging
):
    dialogues_output = ''
    metadatas_output = ''
    metadatas_null_count = 0

    # create dialogues string
    for i in range(len(dialogues)):
        # check if a non-starting dialogue section has no data (misinput)
        is_dialogue_empty = not dialogues[i].strip()
        if is_dialogue_empty and i > 0:
            raise ValueError(f'Line {line}: Dialogue is empty but it is not the only starting dialogue for the node')
        
        dialogues_output += f'''\
                "{dialogues[i]}",''' if not is_dialogue_empty else ''
        
        # output null if no metadata is defined for this dialogue section
        if not unskippables[i] and not no_continuations[i] and not wait_for_timelines[i]:
            metadata = '''\
                null,'''
            metadatas_null_count += 1
        else:
            unskippable_prop        = f'isUnskippable = {format_bool_string(unskippables[i], line)}, ' if unskippables[i] else ''
            no_continuation_prop    = f'noContinuationIcon = {format_bool_string(no_continuations[i], line)}, ' if no_continuations[i] else ''
            wait_for_timeline_prop  = f'waitForTimeline = {format_bool_string(wait_for_timelines[i], line)}, ' if wait_for_timelines[i] else ''

            metadata = f'''\
                new Model_Languages.Metadata
                {{
                    {unskippable_prop}{no_continuation_prop}{wait_for_timeline_prop}
                }},'''
        metadatas_output += f'{metadata}'

        # add new lines between entries
        if i < len(dialogues) - 1:
            dialogues_output += f'\n'
            metadatas_output += f'\n'
    
    choice_text_prop = f'''
        choiceText = "{choice_text}",''' if choice_text else ''
    
    # don't render metadatas field if all are null
    metadatas_output = f'''\
metadata = new Model_Languages.Metadata[]
        {{
{metadatas_output}
        }}''' if metadatas_null_count < len(dialogues) else ''
    
    row_data = f'''\
{{
    "{id}",
    new Model_Languages
    {{
        speaker = "{speaker}",
        EN = new string[]
        {{
{dialogues_output}
        }},{choice_text_prop}
        {metadatas_output}
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
        
        id = ''
        dialogues = [];
        speaker = ''
        choice_text = ''
        prepend_header = ''
        
        # metadata
        unskippables = []
        no_continuations = []
        wait_for_timelines = []
        
        reader = csv.reader(csv_file, delimiter=',')
        
        for row in reader:
            is_initial = line == 0;
            
            # skip rows
            if row[0].upper() == SKIP_ROW_SYMBOL.upper():
                continue
            
            # comment out rows
            if row[0].upper() == COMMENT_ROW_SYMBOL.upper():
                prepend_header = create_section_header(row[1])

                if is_initial:
                    output += prepend_header
                    prepend_header = ''
                continue
                
            # notify misinputs
            # if there is multiline text but no MULTILINE_SYMBOL, throw an error
            if not row[1] and row[4]:
                raise ValueError(f'Line {line} "{row[4]}": You need to signal there is a multiline with {MULTILINE_SYMBOL}')
            elif row[1] == MULTILINE_SYMBOL and not row[4]:
                raise ValueError(f'Line {line} "{row[4]}": There is a multiline sign {MULTILINE_SYMBOL} but no corresponding text')
            
            current_id                  = row[1]
            current_dialogue            = row[4]
            current_speaker             = row[2]
            current_choice_text         = row[5]
            
            current_unskippable         = row[6]
            current_no_continuation     = row[7]
            current_wait_for_timeline   = row[8]
            
            # skip rows without an id
            if not current_id:
                continue

            # handle new dialogue nodes or multilines
            is_multiline_dialogue = current_id == MULTILINE_SYMBOL
            is_new_dialogue_node = (id != current_id and not is_multiline_dialogue) or is_initial;
            
            # on new dialogue node, output the data we've been building for the previous node
            if is_new_dialogue_node:
                if not is_initial:
                    dialogue_output = create_dialogue_object(
                        id,
                        speaker,
                        dialogues,
                        choice_text,
                        unskippables,
                        no_continuations,
                        wait_for_timelines,
                        line
                    )
                    output += dialogue_output
                    if prepend_header:
                        output += prepend_header
                        prepend_header = ''
                
                id = current_id
                dialogues = [current_dialogue]
                speaker = current_speaker
                choice_text = current_choice_text

                unskippables = [current_unskippable]
                no_continuations = [current_no_continuation]
                wait_for_timelines = [current_wait_for_timeline]
            
            elif is_multiline_dialogue:
                dialogues.append(current_dialogue)
                
                unskippables.append(current_unskippable)
                no_continuations.append(current_no_continuation)
                wait_for_timelines.append(current_wait_for_timeline)

            line += 1

    # output what's left in rows data
    dialogue_output = create_dialogue_object(
        id,
        speaker,
        dialogues,
        choice_text,
        unskippables,
        no_continuations,
        wait_for_timelines,
        line
    )
    output += dialogue_output
    
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
// Last created by Dialogue Exporter at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

using System.Collections;
using System.Collections.Generic;

// https://docs.google.com/spreadsheets/d/12PJr55wEMnZhO3n-c00xunSQxyDqnkutiAOx4BLh0tQ/edit#gid=0

public class Model_Languages
{{
    public string speaker {{ get; set; }}
    public string[] EN {{ get; set; }}
    public Metadata[] metadata {{ get; set; }}
    public string choiceText {{ get; set; }}
    
    // If Metadata is not defined, it will default to what is in the Editor;
    // otherwise it will overwrite with what is present.
    public class Metadata
    {{
        public bool? isUnskippable;
        public bool? noContinuationIcon;
        public bool? waitForTimeline;
    }}
}}

/// <summary>
/// Helper to populate Dialogue Nodes. Keep the dynamic format here.
/// Id: area_speaker_description_XXXX
/// </summary>
public static class Script_Dialogue
{{
public static Dictionary<string, Model_Languages> Dialogue = new Dictionary<string, Model_Languages>
'''

def create_file_footer():
    return '''\
}
'''

main()