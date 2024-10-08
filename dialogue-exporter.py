#! /usr/bin/python

'''
How to Use
- Export .csv in same directory as this script
- Run this script with python3 and it will overwrite inside Unity Assets/Scripts

Localization Notes
- on empty localized line, it will copy over English line
- on empty localized choice text, it will copy over English choice text
'''

import csv
import datetime
import re
import warnings

INPUT_FILE          = 'Dialogue - Localized - Dialogue.csv'
OUTPUT_FILE         = 'Script_Dialogue.cs'

SKIP_ROW_SYMBOL     = 'SKIP'
COMMENT_ROW_SYMBOL  = 'x'
MULTILINE_SYMBOL    = '"'
TRUE_SYMBOL         = 'TRUE' 
FALSE_SYMBOL        = 'FALSE'

ID_DELIMITER    = '_'
ID_MIN_LENGTH   = 4

def main():
    output = ''
    id_count = 0
    line = 0    # line in Excel (for debugging)

    with open(INPUT_FILE) as csv_file:
        
        id = ''
        dialogues = []
        dialogues_cn = []
        dialogues_jp = []
        dialogues_ru = []
        speaker = ''
        choice_text = ''
        choice_text_cn = ''
        choice_text_jp = ''
        choice_text_ru = ''
        prepend_header = ''
        
        # metadata
        unskippables = []
        no_continuations = []
        wait_for_timelines = []
        autonexts = []
        full_art_overrides = []
        
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
            
            current_id                  = row[1].strip()
            current_dialogue            = row[4].strip()
            current_dialogue_cn         = row[12].strip()
            current_dialogue_jp         = row[14].strip()
            current_dialogue_ru         = row[16].strip()
            current_speaker             = row[2].strip()
            current_choice_text         = row[5].strip()
            current_choice_text_cn      = row[13].strip()
            current_choice_text_jp      = row[15].strip()
            current_choice_text_ru      = row[17].strip()
            
            current_unskippable         = row[6].strip()
            current_no_continuation     = row[7].strip()
            current_wait_for_timeline   = row[8].strip()
            current_autonext            = row[9].strip()
            current_full_art_override   = row[10].strip()

            # skip rows without an id
            if not current_id:
                continue

            # handle new dialogue nodes or multilines
            is_multiline_dialogue = current_id == MULTILINE_SYMBOL
            is_new_dialogue_node = (id != current_id and not is_multiline_dialogue) or is_initial;
            
            # check for valid ids
            if not is_multiline_dialogue:
                check_id(current_id, line)

            # on new dialogue node, output the data we've been building for the previous node
            if is_new_dialogue_node:
                if not is_initial:
                    dialogue_output = create_dialogue_object(
                        id,
                        speaker,
                        dialogues,
                        dialogues_cn,
                        dialogues_jp,
                        dialogues_ru,
                        choice_text,
                        choice_text_cn,
                        choice_text_jp,
                        choice_text_ru,
                        unskippables,
                        no_continuations,
                        wait_for_timelines,
                        autonexts,
                        full_art_overrides,
                        line
                    )
                    output += dialogue_output
                    if prepend_header:
                        output += prepend_header
                        prepend_header = ''
                
                # start building data
                id = current_id
                dialogues = [current_dialogue]
                dialogues_cn = [current_dialogue_cn]
                dialogues_jp = [current_dialogue_jp]
                dialogues_ru = [current_dialogue_ru]
                speaker = current_speaker
                choice_text = current_choice_text
                choice_text_cn = current_choice_text_cn
                choice_text_jp = current_choice_text_jp
                choice_text_ru = current_choice_text_ru

                unskippables = [current_unskippable]
                no_continuations = [current_no_continuation]
                wait_for_timelines = [current_wait_for_timeline]
                autonexts = [current_autonext]
                full_art_overrides = [current_full_art_override]
            
            # append data to current node data
            elif is_multiline_dialogue:
                dialogues.append(current_dialogue)
                dialogues_cn.append(current_dialogue_cn)
                dialogues_jp.append(current_dialogue_jp)
                dialogues_ru.append(current_dialogue_ru)
                
                unskippables.append(current_unskippable)
                no_continuations.append(current_no_continuation)
                wait_for_timelines.append(current_wait_for_timeline)
                autonexts.append(current_autonext)
                full_art_overrides.append(current_full_art_override)

            id_count += 1

    # output what's left in rows data
    dialogue_output = create_dialogue_object(
        id,
        speaker,
        dialogues,
        dialogues_cn,
        dialogues_jp,
        dialogues_ru,
        choice_text,
        choice_text_cn,
        choice_text_jp,
        choice_text_ru,
        unskippables,
        no_continuations,
        wait_for_timelines,
        autonexts,
        full_art_overrides,
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

    print(f'Ids: {id_count}')
    print(f'Lines processed: {line}')

def check_id(id, line):
    if id.count(ID_DELIMITER) < 2:
        raise ValueError(f'Line {line} Id {id}: Does not contain at least 2 delimiters')
    if bool(re.search(r"\s", id)):
        raise ValueError(f'Line {line} Id {id}: Contains spaces')
    if len(id) < 4:
        raise ValueError(f'Line {line} Id {id}: Is less than 4 characters')

def format_bool_string(bool_string, line):
    if bool_string == TRUE_SYMBOL:
        return 'true'
    elif bool_string == FALSE_SYMBOL:
        return 'false'
    raise ValueError(f'Line {line}: A boolean is not formatted correctly')

def format_int(i, line):
    if isinstance(int(i), int):
        return i
    raise ValueError(f'Line {line}: An int is not formatted correctly')

def create_dialogue_object(
    id,
    speaker,
    dialogues,
    dialogues_cn,
    dialogues_jp,
    dialogues_ru,
    choice_text,
    choice_text_cn,
    choice_text_jp,
    choice_text_ru,
    unskippables,
    no_continuations,
    wait_for_timelines,
    autonexts,
    full_art_overrides,
    line # for debugging
):
    dialogues_output = ''
    dialogues_output_cn = ''
    dialogues_output_jp = ''
    dialogues_output_ru = ''
    metadatas_output = ''
    metadatas_null_count = 0

    # create dialogues string
    for i in range(len(dialogues)):
        # check if a non-starting dialogue section has no data (misinput)
        is_dialogue_empty = not dialogues[i].strip()
        if is_dialogue_empty and i > 0:
            raise ValueError(f'Line {line}: Dialogue is empty but it is not the only starting dialogue for the node')
        
        dialogue_output_en = f'''\
                @"{dialogues[i]}",''' if not is_dialogue_empty else ''
        dialogues_output += dialogue_output_en
            
        # -------------------------------------------------------------
        # CN - Dialogue Sections
        is_dialogue_empty_cn = not dialogues_cn[i].strip()
        # TBD Add BACK BELOW AFTER DIALOGUE IS FULLY POPULATED
        # if is_dialogue_empty_cn and i > 0:
        #     raise ValueError(f'Line {line}: Dialogue CN is empty but it is not the only starting dialogue for the node')
        
        # Fallback to English line if the localization is empty
        dialogues_output_cn += f'''\
                @"{dialogues_cn[i]}",''' if not is_dialogue_empty_cn else dialogue_output_en
        # -------------------------------------------------------------
        # JP - Dialogue Sections
        is_dialogue_empty_jp = not dialogues_jp[i].strip()
        # if is_dialogue_empty_jp and i > 0:
        #     warnings.warn(f'Line {line}: Dialogue JP is empty but it is not the only starting dialogue for the node')
        
        # Fallback to English line if the localization is empty
        dialogues_output_jp += f'''\
                @"{dialogues_jp[i]}",''' if not is_dialogue_empty_jp else dialogue_output_en
        # -------------------------------------------------------------
        # RU - Dialogue Sections
        is_dialogue_empty_ru = not dialogues_ru[i].strip()
        # if is_dialogue_empty_ru and i > 0:
        #     warnings.warn(f'Line {line}: Dialogue RU is empty but it is not the only starting dialogue for the node')
        
        # Fallback to English line if the localization is empty
        dialogues_output_ru += f'''\
                @"{dialogues_ru[i]}",''' if not is_dialogue_empty_ru else dialogue_output_en
        # -------------------------------------------------------------
        
        # output null if no metadata is defined for this dialogue section
        if not unskippables[i] and not no_continuations[i] and not wait_for_timelines[i] and not autonexts[i] and not full_art_overrides[i]:
            metadata = '''\
                null,'''
            metadatas_null_count += 1
        else:
            unskippable_prop        = f'isUnskippable = {format_bool_string(unskippables[i], line)}, ' if unskippables[i] else ''
            no_continuation_prop    = f'noContinuationIcon = {format_bool_string(no_continuations[i], line)}, ' if no_continuations[i] else ''
            wait_for_timeline_prop  = f'waitForTimeline = {format_bool_string(wait_for_timelines[i], line)}, ' if wait_for_timelines[i] else ''
            autonext_prop           = f'autoNext = {format_bool_string(autonexts[i], line)}, ' if autonexts[i] else ''
            full_art_override_prop  = f'fullArtOverride = {format_int(full_art_overrides[i], line)}, ' if full_art_overrides[i] else ''

            metadata = f'''\
                new Model_Languages.Metadata
                {{
                    {unskippable_prop}{no_continuation_prop}{wait_for_timeline_prop}{autonext_prop}{full_art_override_prop}
                }},'''
        metadatas_output += f'{metadata}'

        # add new lines between entries
        if i < len(dialogues) - 1:
            dialogues_output += f'\n'
            dialogues_output_cn += f'\n'
            dialogues_output_jp += f'\n'
            dialogues_output_ru += f'\n'
            metadatas_output += f'\n'
    
    choice_text_prop = f'''
        choiceText = "{choice_text}",''' if choice_text else ''

    # -------------------------------------------------------------
    # CN - Choice Text
    # localized choice text should never be blank; if no localized, copy over EN with localized key
    choice_text_name_cn = "choiceTextCN"
    choice_text_prop_cn = f'''
        {choice_text_name_cn} = "{choice_text_cn}",''' if choice_text_cn else choice_text_prop_fallback(choice_text_name_cn, choice_text)
    # -------------------------------------------------------------
    # JP - Choice Text
    choice_text_name_jp = "choiceTextJP"
    choice_text_prop_jp = f'''
        {choice_text_name_jp} = "{choice_text_jp}",''' if choice_text_jp else choice_text_prop_fallback(choice_text_name_jp, choice_text)
    # -------------------------------------------------------------
    # RU - Choice Text
    choice_text_name_ru = "choiceTextRU"
    choice_text_prop_ru = f'''
        {choice_text_name_ru} = "{choice_text_ru}",''' if choice_text_ru else choice_text_prop_fallback(choice_text_name_ru, choice_text)
    # -------------------------------------------------------------
    
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
        }},
        CN = new string[]
        {{
{dialogues_output_cn}
        }},
        JP = new string[]
        {{
{dialogues_output_jp}
        }},
        RU = new string[]
        {{
{dialogues_output_ru}
        }},{choice_text_prop}{choice_text_prop_cn}{choice_text_prop_jp}{choice_text_prop_ru}
        {metadatas_output}
    }}
}},
'''
    return row_data

def choice_text_prop_fallback(prop, choice_text):
    return f'''
        {prop} = "{choice_text}",''' if choice_text else ''

def create_section_header(text):
    output = f'''\
// ------------------------------------------------------------------
// {text}\n'''
    return output

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
    public string[] CN {{ get; set; }}
    public string[] JP {{ get; set; }}
    public string[] RU {{ get; set; }}
    public Metadata[] metadata {{ get; set; }}
    public string choiceText {{ get; set; }}
    public string choiceTextCN {{ get; set; }}
    public string choiceTextJP {{ get; set; }}
    public string choiceTextRU {{ get; set; }}
    
    // If Metadata is not defined, it will default to what is in the Editor;
    // otherwise it will overwrite with what is present.
    public class Metadata
    {{
        public bool? isUnskippable;
        public bool? noContinuationIcon;
        public bool? waitForTimeline;
        public bool? autoNext;
        public int? fullArtOverride; 
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