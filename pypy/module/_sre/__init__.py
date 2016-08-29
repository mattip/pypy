from pypy.interpreter.mixedmodule import MixedModule

class Module(MixedModule):

    appleveldefs = {
    }

    interpleveldefs = {
        'CODESIZE':       'space.wrap(interp_sre.CODESIZE)',
        'MAGIC':          'space.newint(20140917)',
        'MAXREPEAT':      'space.wrap(interp_sre.MAXREPEAT)',
        'MAXGROUPS':      'space.wrap(interp_sre.MAXGROUPS)',
        'compile':        'interp_sre.W_SRE_Pattern',
        'getlower':       'interp_sre.w_getlower',
        'getcodesize':    'interp_sre.w_getcodesize',
    }
