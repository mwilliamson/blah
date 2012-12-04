import subprocess
import errno

_dev_null = open('/dev/null', 'w')

def quiet_check_call(command, cwd=None):
    return run(command, cwd=cwd).return_code

def quiet_call(command, cwd=None):
    return run(command, cwd=cwd, allow_error=True).return_code
    
def quiet_check_output(command, cwd):
    return run(command, cwd=cwd).output
    
def _quiet_subprocess_eval(func, args, kwargs):
    return func(*args, stdout=_dev_null, stderr=subprocess.STDOUT, **kwargs)

def run(command, cwd=None, allow_error=False):
    try:
        process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=_dev_null)
    except OSError as error:
        raise NoSuchCommandError(command[0])
        
    output, unused_err = process.communicate()
    return_code = process.poll()
    result = ExecutionResult(return_code, output)
    if not allow_error and return_code:
        error = subprocess.CalledProcessError(return_code, command)
        error.output = output
        raise error
    return result

class ExecutionResult(object):
    def __init__(self, return_code, output):
        self.return_code = return_code
        self.output = output

class NoSuchCommandError(OSError):
    def __init__(self, command):
        super(type(self), self).__init__("No such command: {0}".format(command))
        self.command = command
