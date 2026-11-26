import json
import pytest
from typer.testing import CliRunner
from tracelens import core
from tracelens.cli import app

def test_timeline_windows_and_clusters(tmp_path,monkeypatch):
    monkeypatch.setattr(core,'model_result',lambda *a,**kw: pytest.fail('Unexpected LLM path'))
    path = tmp_path/'app.log'
    path.write_text('2026-01-01T10:00:00Z INFO start\n'
                    '2026-01-01T10:00:01Z WARN pool busy\n'
                    '2026-01-01T10:00:02Z ERROR timeout request=42\n'
                    '2026-01-01T10:00:03Z ERROR timeout request=43\n',encoding='utf-8')
    report = core.analyze(path)
    assert report['total_lines'] == 4
    assert report['levels'] == {'INFO':1,'WARNING':1,'ERROR':2}
    assert report['timeline'][1]['level'] == 'WARNING'
    assert report['timeline'][0]['timestamp'] == '2026-01-01T10:00:00Z'
    assert report['error_clusters'][0]['count'] == 2
    assert [r['line'] for r in report['timeline']] == [1,2,3,4]
    assert report['analysis'] is None

@pytest.mark.parametrize('text,secret',[
    ('password=synthetic-secret','synthetic-secret'),
    ('Authorization: Bearer synthetic-bearer','synthetic-bearer'),
    ('{"api_key": "synthetic-key"}','synthetic-key'),
    ('https://demo:synthetic-pass@example.org','synthetic-pass'),
    ('email=demo@example.org','demo@example.org'),
    ("password='synthetic secret with spaces'",'secret with spaces'),
])
def test_redaction(text,secret):
    assert secret not in core.redact(text)

def test_context_cap_and_empty_input(tmp_path):
    path = tmp_path/'app.log'
    path.write_text('ERROR repeated\n'*100,encoding='utf-8')
    report = core.analyze(path)
    assert len(report['timeline']) == 80
    assert report['omitted_context_lines'] == 20
    path.write_text('',encoding='utf-8')
    assert core.analyze(path)['total_lines'] == 0

def test_reject_unknown_line_from_fake_output(tmp_path,monkeypatch):
    path = tmp_path/'app.log'
    path.write_text('ERROR timeout',encoding='utf-8')
    fake = core.Summary(observations=[core.Observation(statement='Timeout',lines=[99])],hypotheses=[],next_checks=[])
    monkeypatch.setattr(core,'model_result',lambda *a,**kw:fake)
    with pytest.raises(ValueError,match='unavailable lines'):
        core.analyze(path,ai=True)

def test_cli_reports(tmp_path):
    path = tmp_path/'app.log'
    path.write_text('ERROR timeout\n',encoding='utf-8')
    result = CliRunner().invoke(app,[str(path),'--json'])
    assert result.exit_code == 0,result.output
    assert json.loads(result.output)['total_lines'] == 1
    assert 'Repeated error clusters' in CliRunner().invoke(app,[str(path)]).output
    assert CliRunner().invoke(app,[str(tmp_path/'missing.log')]).exit_code == 1
