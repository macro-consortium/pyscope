def callmethod(method):
    """
    OK, a long explanation for 2 lines of code here...

    pywin32 seems to get confused about no-argument methods provided by 
    some COM servers, treating them as getter properties rather than methods.
    As a result, simply accessing the name of the method ends up calling it.
    Here's a trick for handling either case.

    Suppose that object1 and object2 both have an AbortSlew method. 
    (Specifically, object1 could be a SiTech.Telescope ASCOM object,
    and object2 could be an ASCOM.Simulator.Telescope object.)
    
    For object1, simply accessing the AbortSlew property causes it to be called, 
    but for object2 it needs to be explicitly called as AbortSlew(). 
    Then we can do:

      callmethod(object1.AbortSlew)
      callmethod(object2.AbortSlew)

    In the first case, object1.AbortSlew will call the method, which will return
    None or some non-method value (in the case of SiTech.Telescope, an integer). 
    That return value gets passed to this method, which finds that the value 
    does not have a __call__ attribute, so it does nothing further.

    In the second case, object2.AbortSlew returns a function object which
    includes a __call__ attribute. This method finds that, and explicitly
    calls the function object.
    """

    if hasattr(method, '__call__'):
        method()

