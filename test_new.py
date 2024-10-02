import os

def test_new():
    print("This is a simple print test", flush=True)
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}", flush=True)
    
    log_file = os.path.join(cwd, "simple_test_log.txt")
    with open(log_file, 'w') as f:
        f.write("Simple test log file\n")
    print(f"Simple log file created at: {log_file}", flush=True)
    assert True