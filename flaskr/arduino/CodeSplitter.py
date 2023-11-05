def extract_sections(code):
    current_section = 'init'
    sections = {
        'init': [],
        'setup': [],
        'inbetween': [],
        'loop': [],
        'end': []
    }

    brace_count = 0
    for line in code.split('\n'):
        stripped_line = line.strip()

        if current_section == 'init':
            if stripped_line.startswith('void setup()'):
                current_section = 'setup'
                brace_count = 1  # We start inside the setup function brace
                continue

        elif current_section == 'setup':
            if '{' in stripped_line:
                brace_count += stripped_line.count('{')
            if '}' in stripped_line:
                brace_count -= stripped_line.count('}')
            if brace_count == 0:
                current_section = 'inbetween'
                continue

        elif current_section == 'inbetween':
            if stripped_line.startswith('void loop()'):
                current_section = 'loop'
                brace_count = 1  # We start inside the loop function brace
                continue

        elif current_section == 'loop':
            if '{' in stripped_line:
                brace_count += stripped_line.count('{')
            if '}' in stripped_line:
                brace_count -= stripped_line.count('}')
            if brace_count == 0:
                current_section = 'end'
                continue

        sections[current_section].append(line)

    # Removing trailing empty lines
    for key in sections:
        sections[key] = '\n'.join(sections[key]).strip()

    return sections
