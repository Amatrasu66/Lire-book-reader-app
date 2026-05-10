const mockSegments = [
    "Hello this is paragraph one.",
    "This is paragraph two. It has two sentences."
];

const mockTimings = [
    {start: 0.1, end: 1.5, text: "Hello this is paragraph one."},
    {start: 1.7, end: 3.0, text: "This is paragraph two."},
    {start: 3.1, end: 5.0, text: "It has two sentences."}
];

function generateMap(segs, timings) {
    const map = [];
    let cursor = 0;
    segs.forEach(s => {
        let sStart = -1;
        let sEnd = 0;
        
        // Accumulate sentences until they consume paragraph text
        let accumulatedTextLength = 0;
        const threshold = s.trim().length;
        
        while(cursor < timings.length) {
            const t = timings[cursor];
            if (sStart === -1) sStart = t.start;
            sEnd = t.end;
            accumulatedTextLength += t.text.trim().length;
            cursor++;
            
            // Factor in space gap padding roughly (+1 per sentence)
            if ((accumulatedTextLength + (cursor > 0 ? 1 : 0)) >= threshold - 5) {
                break;
            }
        }
        map.push({ start: sStart, end: sEnd });
    });
    return map;
}

console.log(JSON.stringify(generateMap(mockSegments, mockTimings), null, 2));
