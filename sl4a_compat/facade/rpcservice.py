#coding: utf-8
from jnius import autoclass, cast, JavaException
from android.runnable import run_on_ui_thread
from android.broadcast import BroadcastReceiver
import time

Log = autoclass('com.googlecode.android_scripting.Log')
Intent = autoclass('android.content.Intent')
MinimalService = autoclass('org.alanjds.sl4acompat.MinimalService')

activity = autoclass('org.renpy.android.PythonActivity').mActivity
context = cast('android.content.Context', activity)


def start(external=False):
    """Starts am RPC service and returns the (host, port, handshake) handle. """
    host = port = received_handshake = None

    if external:
        # Public: $ am start -a com.googlecode.android_scripting.action.LAUNCH_SERVER -n com.googlecode.android_scripting/.activity.ScriptingLayerServiceLauncher --ez com.googlecode.android_scripting.extra.USE_PUBLIC_IP true
        # Private on port: $ am start -a com.googlecode.android_scripting.action.LAUNCH_SERVER -n com.googlecode.android_scripting/.activity.ScriptingLayerServiceLauncher --ei com.googlecode.android_scripting.extra.USE_SERVICE_PORT 45001
        # Private random: $ am start -a com.googlecode.android_scripting.action.LAUNCH_SERVER -n com.googlecode.android_scripting/.activity.ScriptingLayerServiceLauncher
        raise NotImplementedError('Should call stock SL4A to start the RPC service')

    netaddress_receiver = None
    netaddress_received = False
    receivedExtras = None

    def _on_netaddress_received(context, intent):
        netaddress_received = True
        receivedExtras = intent.getExtras()
        msg = 'NETADDRESS received!'; Log.v(msg); print msg
        #netaddress_receiver.stop() # Disposable BroadcastReceiver?

    netaddress_receiver = BroadcastReceiver(_on_netaddress_received,
                                            actions=['org.alanjds.sl4acompat.STORE_RPC_NETADDRESS'])
    netaddress_receiver.start()

    # TODO: How to get MinimalService.class with pyjnius without this hack?
    MinimalService__class = MinimalService().getClass()
    serviceIntent = Intent(context, MinimalService__class)
    componentName  = context.startService(serviceIntent)

    try:
        for i in xrange(20): # wait up to 10 sec
            if netaddress_received:
                break
            time.sleep(0.5)
        else:
            raise RuntimeError('Service net address has requested but never received')
    finally:
        netaddress_receiver.stop()

    return receivedExtras.getString('host'), receivedExtras.getString('port'), receivedExtras.getString('handshake')
