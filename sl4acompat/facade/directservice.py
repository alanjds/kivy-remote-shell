#coding: utf-8
import json
import collections
from itertools import count

from jnius import autoclass, cast, JavaException
from android.runnable import run_on_ui_thread


FACADE_MANAGER = None
_CALL_ID = count(1)

FacadeConfiguration = autoclass('com.googlecode.android_scripting.facade.FacadeConfiguration')
FacadeManagerFactory = autoclass('com.googlecode.android_scripting.facade.FacadeManagerFactory')
Log = autoclass('com.googlecode.android_scripting.Log')
JsonRpcResult = autoclass('com.googlecode.android_scripting.jsonrpc.JsonRpcResult')
JSONArray = autoclass('org.json.JSONArray')
JSONException = autoclass('org.json.JSONException')
JSONObject = autoclass('org.json.JSONObject')
Intent = autoclass('android.content.Intent')
Boolean = autoclass('java.lang.Boolean')
Throwable = autoclass('java.lang.Throwable')
MinimalService = autoclass('org.alanjds.sl4acompat.MinimalService')

activity = autoclass('org.renpy.android.PythonActivity').mActivity

Result = collections.namedtuple('Result', 'id,result,error')

def _get_facademanager(service=None, intent=None):
    global FACADE_MANAGER
    if not FACADE_MANAGER:
        service = service # 'None' leads to NullPointerException at AndroidFacade.java:112
        intent = intent
        facademanager_factory = FacadeManagerFactory(
            FacadeConfiguration.getSdkLevel(),
            service, intent,
            FacadeConfiguration.getFacadeClasses()
        )
        facademanager = facademanager_factory.create()
        FACADE_MANAGER = facademanager
    return FACADE_MANAGER

def _direct_call(method, *args):
    data = {'id': _CALL_ID.next(),
            'method': method,
            'params': args}
    request_string = json.dumps(data)

    # DO THE REQUEST
    Log.v("Received: " + request_string)
    request = JSONObject(request_string)
    jId = request.getInt("id")
    jMethod = request.getString("method")
    jParams = request.getJSONArray("params")
    jResult = JsonRpcResult.result(jId, Boolean(True)) # accept the payload
    receiverManager = FACADE_MANAGER
    rpc = receiverManager.getMethodDescriptor(jMethod)

    if rpc == None:
        raise RuntimeException("Unknown RPC.")

    try:
        @run_on_ui_thread
        def _main_call():
            jResult = JsonRpcResult.result(jId, rpc.invoke(receiverManager, jParams))
        _main_call()
    except JavaException, e:
        Log.e("Invocation error.") # TODO: How to get the Throwable throwed??
        raise

    response_string = jResult.toString()
    # CONVERT THE RESULT BACK

    result = json.loads(response_string)
    if result['error'] is not None:
      print result['error']
    # namedtuple doesn't work with unicode keys.
    return Result(id=result['id'], result=result['result'],
                  error=result['error'], )
