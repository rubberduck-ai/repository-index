def calculateLinePositions(lines, lineSeparator):
    linePositions = []

    position = 0

    for line in lines:
        linePositions.append(
            {
                "start": position,
                "end": position + len(line),  # note: separator is not included
            }
        )

        position += len(line) + len(lineSeparator)

    return linePositions


def createSplitLinearLines(maxChunkCharacters, lineSeparator="\n"):
    def splitLinearLines(content):
        lines = content.split(lineSeparator)
        linePositions = calculateLinePositions(lines, lineSeparator)

        chunks = []

        segment = None

        def addSegmentToChunks(currentLine):
            nonlocal segment
            if segment == None:
                return
            chunks.append(
                {
                    "startPosition": linePositions[segment["startLine"]]["start"],
                    "endPosition": linePositions[currentLine]["end"],
                    "content": lineSeparator.join(segment["lines"]),
                }
            )
            segment = None

        for i in range(len(lines)):
            lineText = lines[i]

            if segment == None:
                segment = {
                    "lines": [lineText],
                    "startLine": i,
                    "characterCount": len(lineText),
                }
            else:
                segment["lines"].append(lineText)
                segment["characterCount"] += len(lineText) + len(lineSeparator)

            # this leads to chunks that are too big (by 1 line)
            if segment["characterCount"] > maxChunkCharacters:
                addSegmentToChunks(i)

        addSegmentToChunks(len(lines) - 1)

        return chunks

    return splitLinearLines
