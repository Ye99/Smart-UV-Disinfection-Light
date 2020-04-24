# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
import uos
# Make machine available in repl
import machine
# uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
import os

import webrepl
webrepl.start()

gc.collect()


def reload(mod):
    import sys
    z = __import__(mod)
    del z
    del sys.modules[mod]
    return __import__(mod)


# Show free file system space
def df():
  s = os.statvfs('//')
  return ('{0} MB'.format((s[0]*s[3])/1048576))


# free() shows free memory.
# free(True) plus bytes information.
def free(full=False):
  gc.collect()
  F = gc.mem_free()
  A = gc.mem_alloc()
  T = F+A
  P = '{0:.2f}%'.format(F/T*100)
  if not full: return P
  else : return ('Total:{0} Free:{1} ({2})'.format(T,F,P))


