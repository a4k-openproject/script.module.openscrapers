from .base import *
from .host.jseval import Eval
from .prototypes.jsjson import JSON

# Now we have all the necessary items to create global environment for script
__all__ = ['Js', 'PyJsComma', 'PyJsStrictEq', 'PyJsStrictNeq',
           'PyJsException', 'PyJsBshift', 'Scope', 'PyExceptionToJs',
           'JsToPyException', 'JS_BUILTINS', 'appengine', 'set_global_object',
           'JsRegExp', 'PyJsException', 'PyExceptionToJs', 'JsToPyException', 'PyJsSwitchException']


# these were defined in base.py
builtins = ('true','false','null','undefined','Infinity',
            'NaN', 'console', 'String', 'Number', 'Boolean', 'RegExp',
            'Math', 'Date', 'Object', 'Function', 'Array',
            'parseFloat', 'parseInt', 'isFinite', 'isNaN')
            #Array, Function, JSON,   Error is done later :)
            # also some built in functions like eval...

def set_global_object(obj):
    obj.IS_CHILD_SCOPE = False
    this = This({})
    this.own = obj.own
    this.prototype = obj.prototype
    PyJs.GlobalObject = this
    # make this available
    obj.register('this')
    obj.put('this', this)



scope = dict(zip(builtins, [globals()[e] for e in builtins]))
# Now add errors:
for name, error in ERRORS.items():
    scope[name] = error
#add eval
scope['eval'] = Eval
scope['JSON'] = JSON
JS_BUILTINS = {}
for k,v in scope.iteritems():
	JS_BUILTINS[k]=v 

