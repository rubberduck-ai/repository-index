def calculate_line_positions(lines, line_separator):
    line_positions = []

    position = 0

    for line in lines:
        line_positions.append(
            {
                "start": position,
                "end": position + len(line),  # note: separator is not included
            }
        )

        position += len(line) + len(line_separator)

    return line_positions


def create_split_linear_lines(max_chunk_characters, line_separator="\n"):
    def split_linear_lines(content):
        lines = content.split(line_separator)
        line_positions = calculate_line_positions(lines, line_separator)

        chunks = []

        segment = None

        def add_segment_to_chunks(current_line):
            nonlocal segment
            if segment == None:
                return
            chunks.append(
                {
                    "startPosition": line_positions[segment["startLine"]]["start"],
                    "endPosition": line_positions[current_line]["end"],
                    "content": line_separator.join(segment["lines"]),
                }
            )
            segment = None

        for i in range(len(lines)):
            line_text = lines[i]

            if segment == None:
                segment = {
                    "lines": [line_text],
                    "startLine": i,
                    "characterCount": len(line_text),
                }
            else:
                segment["lines"].append(line_text)
                segment["characterCount"] += len(line_text) + len(line_separator)

            # this leads to chunks that are too big (by 1 line)
            if segment["characterCount"] > max_chunk_characters:
                add_segment_to_chunks(i)

        add_segment_to_chunks(len(lines) - 1)

        return chunks

    return split_linear_lines
