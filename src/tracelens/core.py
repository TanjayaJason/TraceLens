import re
from collections import Counter
from pathlib import Path
from pydantic import BaseModel, Field
from .support import read_text, model_result

def redact(text):
    text = re.sub(r'(?i)(authorization["\s]*[:=][ "]*(?:bearer|basic)\s+)[^\s,;"\']+', r'\1[REDACTED]', text)
    text = re.sub(
        r'''(?i)((?:api[_-]?key|password|passwd|secret|token)["'\s]*[:=]\s*)(?:"[^"\r\n]*"|'[^'\r\n]*'|[^\s,;]+)''',
        r'\1[REDACTED]', text)
    text = re.sub(r'(?i)(https?://)[^/@\s:]+:[^/@\s]+@', r'\1[REDACTED]@', text)
    text = re.sub(r'\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_]{16,})\b', '[REDACTED]', text)
    return re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[EMAIL]', text)

class Observation(BaseModel):
    statement: str = Field(min_length=1, max_length=800)
    lines: list[int] = Field(min_length=1, max_length=8)
class Summary(BaseModel):
    observations: list[Observation] = Field(max_length=6)
    hypotheses: list[Observation] = Field(max_length=4)
    next_checks: list[str] = Field(max_length=5)

def analyze(path: Path, question='', ai=False):
    if len(question) > 1500:
        raise ValueError('Question must be at most 1500 characters.')
    raw = read_text(path)
    lines = raw.splitlines()
    if len(lines) > 100_000:
        raise ValueError('Log exceeds 100,000 lines.')
    records, errors = [], []
    for index, line in enumerate(lines):
        match = re.search(r'\b(TRACE|DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL)\b', line, re.I)
        level = match.group(1).upper() if match else 'UNKNOWN'
        if level == 'WARN':
            level = 'WARNING'
        timestamp = re.search(r'\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?', line)
        records.append({'line': index + 1, 'level': level,
                        'timestamp': timestamp.group(0) if timestamp else None,
                        'text': redact(line)[:1500]})
        if level in ('ERROR', 'CRITICAL', 'FATAL'):
            errors.append(index)
    windows = set()
    for index in errors:
        windows.update(range(max(0, index - 2), min(len(lines), index + 3)))
    if not windows:
        windows.update(range(min(len(lines), 40)))
    # Keep first incident windows deterministic and cap external context.
    selected = [records[i] for i in sorted(windows)[:80]]
    groups = Counter()
    for i in errors:
        event = records[i]
        pattern = event['text']
        if event['timestamp']:
            pattern = pattern.replace(event['timestamp'], '<timestamp>', 1)
        groups[re.sub(r'\b\d+\b', '#', pattern)] += 1
    result = {'total_lines': len(lines), 'levels': dict(Counter(r['level'] for r in records)),
              'error_clusters': [{'pattern': p, 'count': n} for p, n in groups.most_common(10)],
              'timeline': selected, 'omitted_context_lines': len(windows) - len(selected),
              'analysis': None}
    if ai:
        summary = model_result(Summary, 'Summarize the incident. Observations must be '
            'directly supported by cited line numbers. Separate hypotheses from facts. '
            'Suggest diagnostic checks only; never claim a confirmed root cause.',
            {'question': redact(question), 'events': selected})
        allowed = {r['line'] for r in selected}
        for item in summary.observations + summary.hypotheses:
            if not set(item.lines) <= allowed:
                raise ValueError('Model referenced unavailable lines; summary withheld.')
        result['analysis'] = summary.model_dump()
    return result

def markdown(report):
    out = ['# TraceLens incident report', '', f"Lines: {report['total_lines']} · Levels: {report['levels']}", '', '## Timeline', '']
    for row in report['timeline']:
        out.append(f"- L{row['line']} [{row['level']}]: {row['text']}")
    out.extend(['', '## Repeated error clusters', ''])
    for cluster in report['error_clusters']:
        out.append(f"- {cluster['count']} occurrences: {cluster['pattern']}")
    out.extend(['', f"Omitted context lines: {report['omitted_context_lines']}"])
    if report['analysis']:
        for key in ('observations', 'hypotheses'):
            out.extend(['', '## ' + key.title(), ''])
            for item in report['analysis'][key]:
                out.append(f"- {item['statement']} (lines {item['lines']})")
        out.extend(['', '## Suggested diagnostic checks', ''])
        out.extend('- ' + s for s in report['analysis']['next_checks'])
    return '\n'.join(out)
