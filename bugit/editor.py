import subprocess

def run(
    appinfo,
    filename,
    ):
    editor = appinfo.environ.get('BUGIT_EDITOR', 'vi')
    subprocess.check_call(
        args=[editor, filename],
        )
