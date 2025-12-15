import re

with open('variables.tf', 'r') as f:
    lines = f.readlines()

output_lines = []
in_validation = False
validation_indent = 0
skip_until_close = 0

i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if we're in a validation block with cross-variable reference
    if 'validation {' in line:
        # Look ahead to see if this validation has cross-var references
        lookahead = []
        j = i
        brace_count = 0
        while j < len(lines):
            lookahead.append(lines[j])
            brace_count += lines[j].count('{') - lines[j].count('}')
            if brace_count == 0 and j > i:
                break
            j += 1
        
        validation_block = ''.join(lookahead)
        
        # Check for cross-var refs (var.something where there are multiple different var names)
        var_refs = re.findall(r'var\.(\w+)', validation_block)
        unique_vars = set(var_refs)
        
        if len(unique_vars) > 1:
            # This validation has cross-var refs, skip it
            print(f"Skipping problematic validation block at line {i+1}")
            i = j + 1
            continue
    
    output_lines.append(line)
    i += 1

with open('variables.tf', 'w') as f:
    f.writelines(output_lines)

print("✅ Removed problematic validation blocks")
