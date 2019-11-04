
import os
import re

files = [f for f in os.listdir('.') if os.path.isfile(f)]  # List files in current directory
files = [f for f in files if re.search('\.TAP$', f)]       # Filter out non cut files
files = sorted(files)

HOLE_SLOWDOWN = 10  # Amount to decrease hole feedrate w.r.t. base feedrate

for f in files:  # For each cut file in current directory
    print(f, end='')

    lines = []
    cut_speed = 0
    hole_speed = 0
    change_log = []
    change_log_count = []

    with open(f, 'r') as cut_file:
        old_lines = tuple(cut_file.readlines())
        lines = list(old_lines)

        for i, line in enumerate(lines):  # For each line in cut file
            if cut_speed:  # If cut speed has been set
                feedrate_match = re.search('(?<=\d)F\d+', line)

                if feedrate_match is None:  # If no feedrate cmd is found
                    continue

                if feedrate_match.group() == f'F{hole_speed}':  # If feedrate is correct
                    continue
                
                line = re.sub(feedrate_match.re, f'F{hole_speed}', line)
                lines[i] = line
                change_str = f'  {feedrate_match.group()} -> F{hole_speed}'

                try:
                    change_log_count[change_log.index(change_str)] += 1
                except ValueError:
                    change_log.append(change_str)
                    change_log_count.append(1)
            
            else:  # If cut speed has not been set
                comment_match = re.search('\d+.\d+ AMPS', line)

                if not comment_match is None:  # If profile comment found (Eg. "( 200.000 AMPS N2_H2O )")
                    lines[i] = ''
                
                try:  # Get feedrate from line
                    line_speed = re.search('(?<=F)\d+', line).group()
                except AttributeError:  # If no feedrate cmd is found
                    pass
                else:  # If feedrate cmd is found
                    cut_speed = int(line_speed)
                    if cut_speed == 130:  # If cut file is for 12ga stainless steel
                        hole_speed = cut_speed
                    else:
                        hole_speed = cut_speed - HOLE_SLOWDOWN
                    print(f' - F{cut_speed}')
                    
    for i, log in enumerate(change_log):
        print(f'{log} (x{change_log_count[i]})')

    if "".join(lines) == "".join(old_lines):  # If file has not changed
        continue
            
    with open(f, 'w') as cut_file:
        print('  Overwriting')
        cut_file.writelines(lines)  # Write changes to the cut file
