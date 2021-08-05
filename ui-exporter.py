#! /usr/bin/python

# Export .csv in same directory as this script
# run this script and it will output 

# {
#     "intro_narrator_hotel",
#     new Model_LanguagesUI
#     {
#         EN = "I work at the front desk of a seaside hotel| about a two hour drive from my hometown."
#     }
# },
import csv;

INPUT_FILE          = 'Dialogue - Localized - UI.csv'
OUTPUT_FILE         = 'output_UI.txt'

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
{{
{output}
}};
'''
    
    # write output into file
    with open(OUTPUT_FILE, 'w') as f:
        f.write(output);

    print(output);
    print(f'Lines: {line}')

main()