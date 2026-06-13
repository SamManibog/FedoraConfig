import subprocess

def always():
    return True

def callback(path):
    cmd = f"chmod +x {path}"
    print(cmd)
    subprocess.run(cmd, shell=True)
