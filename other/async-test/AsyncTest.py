'''
Created on 27/06/2009

This is an attempt to create the simplest possible test for threading in a
Python extension for Nautilus.

Run with 'nautilus -q && nautilus'

@author: Jason Heeris
'''

import nautilus
import gobject

import threading
import time

import logging
        
class AsyncTest(nautilus.MenuProvider):
    ''' Simple test class for multithreaded Python Nautilus extension.
    '''
    
    def __init__(self):
        logging.getLogger().setLevel(logging.DEBUG)
    
    def get_background_items(self, window, files):
        '''
        Gets the context menu entry.
        '''
        menu_item = nautilus.MenuItem(
            'AsyncTest',
            'Test Async. Behaviour',
            'Tests multithreading in python-nautilus extensions',
            'apps/gnome-panel-clock'
        )
        
        menu_item.connect('activate', self.test_asynchronicity)
        
        return [menu_item]
        
    def test_asynchronicity(self, *args, **kwargs):
        '''
        This is a function to test doing things asynchronously.
        '''
              
        def asynchronous_function():
            
            logging.getLogger().setLevel(logging.DEBUG)

            logging.debug('\n%s Inside asynchronous_function()' % time.time())         
            
            for i in range(1, 21):
                time.sleep(0.01)
                logging.debug('%s %0i Asynchronous thread still running...' % (time.time(), i))
                logging.debug('Current thread: %s' % threading.currentThread())
                logging.debug('Is demon: %s' % threading.currentThread().isDaemon())
            
            logging.debug("%s asynchronous_function() finished\n" % time.time())
        
        # Calling threads_init does not seem to do anything.
        logging.debug('Current thread: %s' % threading.currentThread())
        gobject.threads_init()
        threading.Thread(target=asynchronous_function, name='Asynch Test').start()
