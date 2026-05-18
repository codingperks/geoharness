import subprocess

# hacky claude code cli call before buying api
def send_message(prompt: str) -> str:
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()
