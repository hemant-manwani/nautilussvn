#
# This is an extension to the Nautilus file manager to allow better 
# integration with the Subversion source control system.
# 
# Copyright (C) 2006-2008 by Jason Field <jason@jasonfield.com>
# Copyright (C) 2007-2008 by Bruce van der Kooij <brucevdkooij@gmail.com>
# Copyright (C) 2008-2008 by Adam Plumb <adamplumb@gmail.com>
# 
# NautilusSvn is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# NautilusSvn is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with NautilusSvn;  If not, see <http://www.gnu.org/licenses/>.
#

class Function:
    """
    Provides an interface to define and call a function.
    
    Usage:
        f = Function(self.do_this, path)
        f.run()
    
    """
    
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None
    
    def start(self):
        self.result = self.func(*self.args, **self.kwargs)
    
    def call(self):
        return self.func(*self.args, **self.kwargs)
    
    def set_args(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    
    def get_result(self):
        return self.result

class FunctionQueue:
    """
    Provides an interface to generate a queue of function calls.
    
    """
    
    def __init__(self):
        self.queue = []
        self.cancel = False
        self._exception = None
    
    def cancel_queue(self):
        self.cancel = True
    
    def append(self, func, *args, **kwargs):
        """
        Append a Function object to the FunctionQueue
        
        @type   func: def
        @param  func: A method call
        
        @type   *args: list
        @param  *args: A list of arguments
        
        @type   **kwargs: list
        @param  **kwargs: A list of keyword arguments
        
        """
        
        self.queue.append(Function(func, *args, **kwargs))
    
    def set_exception_callback(self, func):
        self._exception = Function(func)
    
    def start(self):
        """
        Runs through the queue and calls each function
        
        """
        
        for func in self.queue:
            if self.cancel == True:
                return
            
            try:
                func.start()
            except Exception, e:
                self._exception.set_args(e)
                self._exception.call()
                break

    def get_result(self, index):
        """
        Retrieve the result of a single function call by specifying the order
        in which the function was in the queue.
        
        @type   index: int
        @param  index: The queue index
        
        """
        
        return self.queue[index].get_result()

class ShellCommand:
    """
    Run a command through the shell and set a callback for what to do with the 
    command's output as they show up.  The default is simply to print to stdout.
    """
    
    def __init__(self, command):
        """
        @type   command: string
        @param  command: The shell command to run

        """
        
        self.command = command
        self.callback = self.echo
        
    def set_callback(self, func):
        """
        Set the callback function to call when something comes through the pipe
        
        @type   func: def
        @param  func: The function to call 

        """
        
        self.callback = func
    
    def echo(self, line):
        """
        The default callback function.  Simply prints to stdout.
        
        @type   line: string
        @param  line: The stdout data

        """
        
        print line
        
    def start(self):
        """
        Run the command and send the output to the callback function
        
        """

        import subprocess
        
        p = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE)
        while p.returncode == None:
            p.poll()
            
            try:
                line = p.stdout.readline().strip()
            except:
                continue
            
            if line:
                self.callback(line)
